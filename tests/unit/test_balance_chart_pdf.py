from __future__ import annotations

from datetime import date, timedelta

import pytest
from reportlab.graphics.shapes import Drawing, Polygon, PolyLine  # type: ignore[import-untyped]
from reportlab.lib import colors  # type: ignore[import-untyped]

from src.export.balance_chart_pdf import (
    _downsample_daily_balances,
    build_balance_chart_drawing,
)
from src.export.pdf_colors import PRIMARY


def _daily_series(
    start: date,
    *,
    count: int | None = None,
    balances: list[float] | None = None,
) -> list[tuple[date, float]]:
    if balances is None:
        if count is None:
            raise ValueError("count or balances is required")
        balances = [100.0 + index * 10.0 for index in range(count)]
    return [(start + timedelta(days=index), balance) for index, balance in enumerate(balances)]


@pytest.mark.unit
def test_build_balance_chart_drawing_returns_empty_drawing_for_no_data() -> None:
    drawing = build_balance_chart_drawing((), currency="USD", width=400.0, height=200.0)

    assert isinstance(drawing, Drawing)
    assert len(drawing.contents) == 0


@pytest.mark.unit
def test_build_balance_chart_drawing_includes_line_for_sample_series() -> None:
    points = _daily_series(date(2026, 1, 1), count=5)
    drawing = build_balance_chart_drawing(points, currency="USD", width=400.0, height=200.0)

    assert len(drawing.contents) == 1
    chart_group = drawing.contents[0]
    shape_types = {type(shape) for shape in chart_group.contents}
    assert PolyLine in shape_types


@pytest.mark.unit
def test_build_balance_chart_drawing_adds_deficit_polygon_when_series_crosses_zero() -> None:
    points = _daily_series(
        date(2026, 1, 1),
        balances=[100.0, 50.0, -25.0, -75.0, -50.0],
    )
    drawing = build_balance_chart_drawing(points, currency="USD", width=400.0, height=200.0)

    chart_group = drawing.contents[0]
    polygons = [shape for shape in chart_group.contents if isinstance(shape, Polygon)]
    assert len(polygons) >= 1
    deficit_fill = colors.HexColor("#80EF4444")
    assert any(polygon.fillColor == deficit_fill for polygon in polygons)


@pytest.mark.unit
def test_build_balance_chart_drawing_uses_primary_stroke_for_balance_line() -> None:
    points = _daily_series(date(2026, 1, 1), count=3, balances=[10.0, 20.0, 30.0])
    drawing = build_balance_chart_drawing(points, currency="USD", width=400.0, height=200.0)

    chart_group = drawing.contents[0]
    polylines = [shape for shape in chart_group.contents if isinstance(shape, PolyLine)]
    assert polylines
    assert polylines[0].strokeColor == PRIMARY


@pytest.mark.unit
def test_downsample_daily_balances_preserves_endpoints_and_zero_crossings() -> None:
    balances = [100.0] * 200 + [-50.0] * 200 + [25.0] * 200
    points = _daily_series(date(2026, 1, 1), balances=balances)
    downsampled = _downsample_daily_balances(points, max_points=50)

    assert downsampled[0] == points[0]
    assert downsampled[-1] == points[-1]
    has_negative = any(balance < 0 for _, balance in downsampled)
    has_positive = any(balance > 0 for _, balance in downsampled)
    assert has_negative
    assert has_positive


@pytest.mark.unit
def test_downsample_daily_balances_keeps_local_extrema_shape() -> None:
    balances = [0.0]
    for index in range(1, 120):
        balances.append(50.0 if index % 2 else -50.0)
    points = _daily_series(date(2026, 1, 1), balances=balances)
    downsampled = _downsample_daily_balances(points, max_points=30)

    assert downsampled[0][1] == 0.0
    assert any(balance == 50.0 for _, balance in downsampled)
    assert any(balance == -50.0 for _, balance in downsampled)


@pytest.mark.unit
def test_downsample_daily_balances_reduces_long_smooth_series() -> None:
    balances = [1000.0 + index * 0.1 for index in range(800)]
    points = _daily_series(date(2026, 1, 1), balances=balances)
    downsampled = _downsample_daily_balances(points, max_points=50)

    assert downsampled[0] == points[0]
    assert downsampled[-1] == points[-1]
    assert len(downsampled) < len(points)
