from __future__ import annotations

import pytest

from src.domain.entities import ExchangeRate
from src.export.metadata import (
    METHODOLOGY_VERSION,
    ExportMetadata,
    build_export_metadata,
    metadata_csv_comment_lines,
    metadata_to_dict,
)


@pytest.mark.unit
def test_build_export_metadata_sets_core_fields() -> None:
    meta = build_export_metadata(
        app_version="1.2.3",
        display_currency="USD",
        exported_at="2026-07-03T12:00:00+00:00",
    )

    assert meta.app == "cash-flow-planner-desktop"
    assert meta.app_version == "1.2.3"
    assert meta.exported_at == "2026-07-03T12:00:00+00:00"
    assert meta.methodology_version == METHODOLOGY_VERSION
    assert meta.display_currency == "USD"
    assert meta.fx_rates == ()


@pytest.mark.unit
def test_build_export_metadata_includes_fx_rate_snapshot() -> None:
    rates = [
        ExchangeRate(
            from_currency="EUR",
            to_currency="USD",
            rate=1.08,
            updated_at="2026-01-01T00:00:00+00:00",
        ),
        ExchangeRate(
            from_currency="GBP",
            to_currency="USD",
            rate=1.25,
            updated_at="2026-01-01T00:00:00+00:00",
        ),
    ]
    meta = build_export_metadata(
        app_version="0.1.0",
        display_currency="USD",
        exchange_rates=rates,
        exported_at="2026-07-03T12:00:00+00:00",
    )

    assert meta.fx_rates == ("EUR→USD@1.08", "GBP→USD@1.25")


@pytest.mark.unit
def test_metadata_to_dict_omits_empty_optional_fields() -> None:
    meta = ExportMetadata(
        app="cash-flow-planner-desktop",
        app_version="0.1.0",
        exported_at="2026-07-03T12:00:00+00:00",
        methodology_version=METHODOLOGY_VERSION,
        display_currency=None,
    )

    assert metadata_to_dict(meta) == {
        "app": "cash-flow-planner-desktop",
        "app_version": "0.1.0",
        "exported_at": "2026-07-03T12:00:00+00:00",
        "methodology_version": METHODOLOGY_VERSION,
    }


@pytest.mark.unit
def test_metadata_to_dict_joins_fx_rates() -> None:
    meta = ExportMetadata(
        app="cash-flow-planner-desktop",
        app_version="0.1.0",
        exported_at="2026-07-03T12:00:00+00:00",
        methodology_version=METHODOLOGY_VERSION,
        display_currency="USD",
        fx_rates=("EUR→USD@1.08",),
    )

    result = metadata_to_dict(meta)
    assert result["fx_rates"] == "EUR→USD@1.08"
    assert result["display_currency"] == "USD"


@pytest.mark.unit
def test_metadata_csv_comment_lines_format() -> None:
    meta = ExportMetadata(
        app="cash-flow-planner-desktop",
        app_version="0.1.0",
        exported_at="2026-07-03T12:00:00+00:00",
        methodology_version=METHODOLOGY_VERSION,
        display_currency="USD",
        fx_rates=("EUR→USD@1.08",),
    )

    lines = metadata_csv_comment_lines(meta)

    assert lines == [
        "# app: cash-flow-planner-desktop",
        "# app_version: 0.1.0",
        "# exported_at: 2026-07-03T12:00:00+00:00",
        "# methodology_version: 1.0",
        "# display_currency: USD",
        "# fx_rate: EUR→USD@1.08",
    ]
