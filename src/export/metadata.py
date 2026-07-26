from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from src.app.identity import PYPROJECT_NAME
from src.domain.entities import ExchangeRate
from src.export.models import ExportContext

_APP_NAME = PYPROJECT_NAME
METHODOLOGY_VERSION = "1.0"


@dataclass(frozen=True)
class ExportMetadata:
    app: str
    app_version: str
    exported_at: str
    methodology_version: str
    display_currency: str | None
    fx_rates: tuple[str, ...] = ()


def _format_fx_rate(rate: ExchangeRate) -> str:
    return f"{rate.from_currency}→{rate.to_currency}@{rate.rate}"


def build_export_metadata(
    *,
    app_version: str,
    display_currency: str | None = None,
    exchange_rates: list[ExchangeRate] | tuple[ExchangeRate, ...] | None = None,
    exported_at: str | None = None,
) -> ExportMetadata:
    rates = exchange_rates or ()
    return ExportMetadata(
        app=_APP_NAME,
        app_version=app_version,
        exported_at=exported_at or datetime.now(UTC).isoformat(),
        methodology_version=METHODOLOGY_VERSION,
        display_currency=display_currency,
        fx_rates=tuple(_format_fx_rate(rate) for rate in rates),
    )


def metadata_to_dict(meta: ExportMetadata) -> dict[str, str]:
    result: dict[str, str] = {
        "app": meta.app,
        "app_version": meta.app_version,
        "exported_at": meta.exported_at,
        "methodology_version": meta.methodology_version,
    }
    if meta.display_currency is not None:
        result["display_currency"] = meta.display_currency
    if meta.fx_rates:
        result["fx_rates"] = ";".join(meta.fx_rates)
    return result


def metadata_csv_comment_lines(meta: ExportMetadata) -> list[str]:
    """Return metadata as CSV comment rows (`# key: value`)."""
    lines: list[str] = []
    for key, value in metadata_to_dict(meta).items():
        if key == "fx_rates":
            for rate in meta.fx_rates:
                lines.append(f"# fx_rate: {rate}")
        else:
            lines.append(f"# {key}: {value}")
    return lines


def metadata_from_export_context(context: ExportContext) -> ExportMetadata:
    return build_export_metadata(
        app_version=context.app_version,
        display_currency=context.display_currency,
        exchange_rates=context.exchange_rates,
        exported_at=context.exported_at,
    )
