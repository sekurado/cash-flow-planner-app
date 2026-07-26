from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from src.app.models.exchange_rate_list_model import ExchangeRateListModel
from src.app.viewmodels.error_support import ErrorSupport
from src.data.repositories.exchange_rate_repo import (
    AbstractExchangeRateRepository,
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.domain.entities import ExchangeRate
from src.domain.exceptions import InvalidExchangeRateTargetError


def _rate_to_dict(rate: ExchangeRate) -> dict[str, Any]:
    return rate.model_dump(mode="json")


def _validate_rate_pair(from_currency: str, to_currency: str) -> None:
    from_code = from_currency.strip()
    to_code = to_currency.strip()
    if not from_code or not to_code:
        msg = "Exchange rate currencies must be non-empty"
        raise InvalidExchangeRateTargetError(msg)
    if from_code == to_code:
        msg = f"Exchange rate source and target must differ, got {from_code}"
        raise InvalidExchangeRateTargetError(msg)


class CurrencyViewModel(QObject):
    """Exposes global exchange-rate CRUD to QML."""

    ratesChanged = Signal()
    errorChanged = Signal()

    def __init__(
        self,
        exchange_rate_repo: AbstractExchangeRateRepository,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._repo = exchange_rate_repo
        self._list_model = ExchangeRateListModel(parent=self)
        self._rates: list[dict[str, Any]] = []
        self._loaded_base_currency = ""
        self._errors = ErrorSupport(self)

    @Property("QVariantList", notify=ratesChanged)  # type: ignore[arg-type]
    def rates(self) -> list[dict[str, Any]]:
        return self._rates

    @Property(QObject, constant=True)
    def rateListModel(self) -> ExchangeRateListModel:
        return self._list_model

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Slot(str)
    def loadRates(self, base_currency: str) -> None:
        try:
            self._clear_error()
            target = base_currency.strip()
            loaded = [
                rate for rate in self._repo.get_all() if target and rate.to_currency == target
            ]
            self._loaded_base_currency = target
            self._list_model.reset(loaded)
            self._rates = [_rate_to_dict(rate) for rate in loaded]
            self.ratesChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, str, float)
    def createRate(
        self,
        from_currency: str,
        to_currency: str,
        rate: float,
    ) -> None:
        try:
            self._clear_error()
            _validate_rate_pair(from_currency, to_currency)
            created = self._repo.upsert(
                ExchangeRateUpsertDto(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate,
                    updated_at=SqliteExchangeRateRepository.utc_now_iso(),
                )
            )
            if created.to_currency != self._loaded_base_currency:
                return
            existing_index = next(
                (
                    index
                    for index, item in enumerate(self._rates)
                    if item.get("from_currency") == from_currency
                    and item.get("to_currency") == to_currency
                ),
                None,
            )
            if existing_index is None:
                self._list_model.append(created)
                self._rates = [*self._rates, _rate_to_dict(created)]
            else:
                self._list_model.update(from_currency, to_currency, created)
                self._rates = [
                    _rate_to_dict(created)
                    if item.get("from_currency") == from_currency
                    and item.get("to_currency") == to_currency
                    else item
                    for item in self._rates
                ]
            self.ratesChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, str, float)
    def updateRate(self, from_currency: str, to_currency: str, rate: float) -> None:
        try:
            self._clear_error()
            _validate_rate_pair(from_currency, to_currency)
            updated = self._repo.upsert(
                ExchangeRateUpsertDto(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate,
                    updated_at=SqliteExchangeRateRepository.utc_now_iso(),
                )
            )
            if updated.to_currency != self._loaded_base_currency:
                return
            self._list_model.update(from_currency, to_currency, updated)
            self._rates = [
                _rate_to_dict(updated)
                if item.get("from_currency") == from_currency
                and item.get("to_currency") == to_currency
                else item
                for item in self._rates
            ]
            self.ratesChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def deleteAllRates(self) -> None:
        try:
            self._clear_error()
            self._repo.delete_all()
            self._list_model.reset([])
            self._rates = []
            self.ratesChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot(str, str)
    def deleteRate(self, from_currency: str, to_currency: str) -> None:
        try:
            self._clear_error()
            self._repo.delete(from_currency, to_currency)
            if to_currency != self._loaded_base_currency:
                return
            self._list_model.remove(from_currency, to_currency)
            self._rates = [
                item
                for item in self._rates
                if not (
                    item.get("from_currency") == from_currency
                    and item.get("to_currency") == to_currency
                )
            ]
            self.ratesChanged.emit()
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
