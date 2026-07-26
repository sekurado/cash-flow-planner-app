from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, QSettings, QThreadPool, Signal, Slot

from src.app.i18n.user_messages import translate_template_text
from src.app.qml_variant import coerce_mapping
from src.app.version import app_version
from src.app.viewmodels.error_support import ErrorSupport
from src.app.workers.plan_export_worker import PlanExportWorker
from src.data.repositories.entry_repo import AbstractEntryRepository
from src.data.repositories.plan_repo import (
    AbstractPlanRepository,
    PlanCreateDto,
    PlanUpdateDto,
)
from src.domain.entities import Plan
from src.domain.template_service import TemplateService
from src.export.plan_exporter import PlanExporter

_LAST_PLAN_ID_KEY = "lastPlanId"


def _plan_to_dict(plan: Plan) -> dict[str, Any]:
    return plan.model_dump()


def _load_available_templates() -> list[dict[str, Any]]:
    return [
        {
            "id": template.template_id,
            "name": translate_template_text(template.name),
            "description": translate_template_text(template.description),
        }
        for template in TemplateService.list_templates()
    ]


class PlanViewModel(QObject):
    """Exposes plan CRUD and selection state to QML."""

    plansChanged = Signal()
    selectedPlanChanged = Signal()
    exportSucceeded = Signal()
    errorChanged = Signal()
    availableTemplatesChanged = Signal()

    def __init__(
        self,
        plan_repo: AbstractPlanRepository,
        plan_exporter: PlanExporter | None = None,
        entry_repo: AbstractEntryRepository | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._repo = plan_repo
        self._plan_exporter = plan_exporter
        self._entry_repo = entry_repo
        self._plans: list[dict[str, Any]] = []
        self._selected_plan: dict[str, Any] | None = None
        self._errors = ErrorSupport(self)
        self._export_worker: PlanExportWorker | None = None
        self._available_templates = _load_available_templates()
        self._refresh_plans()
        self._restore_selected_plan()

    @Property("QVariantList", notify=plansChanged)  # type: ignore[arg-type]
    def plans(self) -> list[dict[str, Any]]:
        return self._plans

    @Property("QVariant", notify=selectedPlanChanged)  # type: ignore[arg-type]
    def selectedPlan(self) -> dict[str, Any] | None:
        return self._selected_plan

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Property("QVariantList", notify=availableTemplatesChanged)  # type: ignore[arg-type]
    def availableTemplates(self) -> list[dict[str, Any]]:
        return self._available_templates

    @Slot(str, str, float)
    def createPlan(self, name: str, base_currency: str, initial_balance: float) -> None:
        try:
            self._clear_error()
            dto = PlanCreateDto(
                name=name,
                base_currency=base_currency,
                initial_balance=initial_balance,
            )
            self._repo.create(dto)
            self._refresh_plans()
            self.plansChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, str, result=bool)
    def createFromTemplate(self, name: str, template_id: str) -> bool:
        try:
            self._clear_error()
            if self._entry_repo is None:
                msg = "Entry repository is not configured"
                raise RuntimeError(msg)
            template = TemplateService.load(template_id)
            plan = self._repo.create(
                PlanCreateDto(
                    name=name,
                    base_currency=template.suggested_base_currency,
                    initial_balance=template.suggested_initial_balance,
                )
            )
            self._entry_repo.create_many(plan.id, template.entries)
            self._refresh_plans()
            self.plansChanged.emit()
            self.selectPlan(plan.id)
            return True
        except Exception as exc:
            self._set_error(exc)
            return False

    @Slot(str)
    def selectPlan(self, plan_id: str) -> None:
        try:
            self._clear_error()
            plan = self._repo.find_by_id(plan_id)
            if plan is None:
                msg = f"Plan not found: {plan_id}"
                raise ValueError(msg)
            self._selected_plan = _plan_to_dict(plan)
            QSettings().setValue(_LAST_PLAN_ID_KEY, plan_id)
            self.selectedPlanChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, "QVariant")
    def updatePlan(self, plan_id: str, data: object) -> None:
        try:
            self._clear_error()
            dto = PlanUpdateDto.model_validate(coerce_mapping(data, label="Plan update data"))
            updated = self._repo.update(plan_id, dto)
            self._refresh_plans()
            self.plansChanged.emit()
            if self._selected_plan is not None and self._selected_plan.get("id") == plan_id:
                self._selected_plan = _plan_to_dict(updated)
                self.selectedPlanChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str)
    def deletePlan(self, plan_id: str) -> None:
        try:
            self._clear_error()
            self._repo.delete(plan_id)
            if self._selected_plan is not None and self._selected_plan.get("id") == plan_id:
                self._selected_plan = None
                QSettings().remove(_LAST_PLAN_ID_KEY)
                self.selectedPlanChanged.emit()
            self._refresh_plans()
            self.plansChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, str)
    def exportPlan(self, plan_id: str, file_path: str) -> None:
        try:
            self._clear_error()
            if self._plan_exporter is None:
                msg = "Plan export is not configured"
                raise RuntimeError(msg)
            worker = PlanExportWorker(
                self._plan_exporter,
                plan_id,
                file_path,
                app_version=app_version(),
            )
            worker.signals.finished.connect(self._on_export_finished)
            worker.signals.error.connect(self._on_export_error)
            self._export_worker = worker
            QThreadPool.globalInstance().start(worker)
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def loadPlans(self) -> None:
        try:
            self._clear_error()
            self._refresh_plans()
            self.plansChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()
        self._available_templates = _load_available_templates()
        self.availableTemplatesChanged.emit()

    def _on_export_finished(self) -> None:
        self._export_worker = None
        self.exportSucceeded.emit()

    def _on_export_error(self, message: str) -> None:
        self._export_worker = None
        self._set_error(message)

    def _refresh_plans(self) -> None:
        self._plans = [_plan_to_dict(plan) for plan in self._repo.find_all()]

    def _restore_selected_plan(self) -> None:
        saved_id = QSettings().value(_LAST_PLAN_ID_KEY)
        if not isinstance(saved_id, str) or not saved_id:
            return
        plan = self._repo.find_by_id(saved_id)
        if plan is None:
            QSettings().remove(_LAST_PLAN_ID_KEY)
            return
        self._selected_plan = _plan_to_dict(plan)

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
