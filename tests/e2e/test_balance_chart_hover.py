from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path

import PySide6.QtCharts  # noqa: F401  # registers QtCharts QML module
import pytest
from PySide6.QtCore import QLocale, QObject, QPoint, QPointF, QUrl
from PySide6.QtQuick import QQuickItem, QQuickWindow, QSGRendererInterface
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtQuickWidgets import QQuickWidget

from main import register_qml_types
from src.app import resources_rc  # noqa: F401  # registers Qt resource bundle
from tests.e2e.conftest import E2EStack

ROOT_DIR = Path(__file__).resolve().parents[2]
BALANCE_CHART_QML = ROOT_DIR / "qml" / "components" / "BalanceChart.qml"


def _simulation_params(
    *,
    start: date,
    end: date,
    initial_balance: float,
    base_currency: str,
) -> dict[str, object]:
    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "initial_balance": initial_balance,
        "base_currency": base_currency,
    }


def _find_qml_child(root: QObject, predicate: Callable[[QObject], bool]) -> QObject | None:
    for child in root.children():
        if predicate(child):
            return child
        found = _find_qml_child(child, predicate)
        if found is not None:
            return found
    return None


def _is_mouse_area(item: QObject) -> bool:
    return item.metaObject().className() == "QQuickMouseArea"


def _map_to_widget(overlay_item: QQuickItem, widget: QQuickWidget, point: QPoint) -> QPoint:
    global_pos = overlay_item.mapToGlobal(QPointF(point))
    return widget.mapFromGlobal(global_pos.toPoint())


def _load_balance_chart_widget(simulation_vm: object) -> tuple[QQuickWidget, QObject]:
    register_qml_types()
    QQuickStyle.setStyle("Material")
    QQuickWindow.setGraphicsApi(QSGRendererInterface.Software)

    widget = QQuickWidget()
    widget.engine().rootContext().setContextProperty("simulationViewModel", simulation_vm)
    widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
    widget.setSource(QUrl.fromLocalFile(str(BALANCE_CHART_QML)))
    if widget.status() != QQuickWidget.Status.Ready:
        errors = widget.errors()
        msg = "; ".join(error.toString() for error in errors) or "unknown QML load error"
        raise RuntimeError(msg)

    widget.resize(900, 320)
    widget.show()
    root = widget.rootObject()
    if root is None:
        msg = f"Failed to load BalanceChart from {BALANCE_CHART_QML}"
        raise RuntimeError(msg)
    return widget, root


def _parse_tooltip_amount(balance_text: str, currency: str) -> float:
    amount_text = balance_text.replace(currency, "").strip()
    parsed, ok = QLocale.system().toDouble(amount_text)
    if ok:
        return parsed

    normalized = amount_text.replace("\xa0", "").replace(" ", "")
    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    elif "," in normalized:
        integer_part, _, fraction_part = normalized.partition(",")
        if len(fraction_part) == 2 and fraction_part.isdigit():
            normalized = f"{integer_part}.{fraction_part}"
        else:
            normalized = normalized.replace(",", "")
    return float(normalized)


@pytest.mark.e2e
def test_balance_chart_hover_shows_date_and_balance(
    qtbot: object,
    e2e_stack: E2EStack,
) -> None:
    """Hovering the plot area shows a tooltip with the nearest day and display-currency balance."""
    plan_vm = e2e_stack.plan_vm
    simulation_vm = e2e_stack.simulation_vm

    plan_vm.createPlan("Hover Chart Plan", "USD", 0.0)
    plan_id = plan_vm.plans[0]["id"]
    plan_vm.selectPlan(plan_id)

    params = _simulation_params(
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
        initial_balance=1000.0,
        base_currency="USD",
    )
    simulation_vm.runSimulation(plan_id, params)
    with qtbot.waitSignal(simulation_vm.resultChanged, timeout=5000):  # type: ignore[attr-defined]
        pass

    widget, balance_chart = _load_balance_chart_widget(simulation_vm)
    qtbot.addWidget(widget)  # type: ignore[attr-defined]

    mouse_area = _find_qml_child(balance_chart, _is_mouse_area)
    assert mouse_area is not None, "plot hover MouseArea not found in BalanceChart"

    overlay = mouse_area.parent()
    assert overlay is not None
    overlay_item = overlay if isinstance(overlay, QQuickItem) else None
    assert overlay_item is not None

    def plot_area_ready() -> bool:
        return overlay_item.width() > 0 and overlay_item.height() > 0

    qtbot.waitUntil(plot_area_ready, timeout=5000)  # type: ignore[attr-defined]

    center = QPoint(int(overlay_item.width() / 2), int(overlay_item.height() / 2))
    widget_pos = _map_to_widget(overlay_item, widget, center)
    qtbot.mouseMove(widget, widget_pos)  # type: ignore[attr-defined]

    def hover_active() -> bool:
        return bool(balance_chart.property("hoverActive"))

    qtbot.waitUntil(hover_active, timeout=3000)  # type: ignore[attr-defined]

    hover_date_text = str(balance_chart.property("hoverDateText"))
    hover_balance_text = str(balance_chart.property("hoverBalanceText"))
    hover_index = int(balance_chart.property("hoverIndex"))
    assert hover_index >= 0
    result = simulation_vm.result
    assert result is not None
    hovered_point = result["daily_balances"][hover_index]

    assert hovered_point["date"].startswith("2026-01-")
    assert hover_date_text
    assert hovered_point["date"][8:10] in hover_date_text
    assert "USD" in hover_balance_text
    expected_amount = simulation_vm.convertToDisplayAmount(float(hovered_point["closing_balance"]))
    assert _parse_tooltip_amount(hover_balance_text, "USD") == pytest.approx(expected_amount)
