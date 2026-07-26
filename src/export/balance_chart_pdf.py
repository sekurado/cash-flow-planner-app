from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date

from reportlab.graphics.shapes import (  # type: ignore[import-untyped]
    Drawing,
    Group,
    Line,
    Polygon,
    PolyLine,
    String,
)
from reportlab.lib import colors  # type: ignore[import-untyped]

from src.export.pdf_colors import PRIMARY
from src.export.pdf_fonts import pdf_font_name

_CHART_AXIS_FONT = pdf_font_name()

_CHART_POSITIVE_FILL = colors.HexColor("#336366F1")
_CHART_DEFICIT_FILL = colors.HexColor("#80EF4444")
_AXIS_COLOR = colors.HexColor("#9CA3AF")
_ZERO_LINE_COLOR = colors.HexColor("#D1D5DB")

_MARGIN_LEFT = 52.0
_MARGIN_RIGHT = 8.0
_MARGIN_TOP = 8.0
_MARGIN_BOTTOM = 28.0
_MAX_POINTS = 500
_LINE_WIDTH = 1.75


def _round_money(value: float) -> float:
    return round(value, 2)


def _format_axis_money(value: float, currency: str) -> str:
    return f"{_round_money(value):.0f} {currency}"


def _format_axis_date(value: date) -> str:
    return value.strftime("%d %b %y")


def _downsample_daily_balances(
    points: Sequence[tuple[date, float]],
    *,
    max_points: int = _MAX_POINTS,
) -> list[tuple[date, float]]:
    if len(points) <= max_points:
        return list(points)

    indices_to_keep: set[int] = {0, len(points) - 1}
    for index in range(1, len(points)):
        previous_balance = points[index - 1][1]
        current_balance = points[index][1]
        if (previous_balance >= 0) != (
            current_balance >= 0
        ) and previous_balance != current_balance:
            indices_to_keep.add(index - 1)
            indices_to_keep.add(index)

    for index in range(1, len(points) - 1):
        balance = points[index][1]
        if balance <= points[index - 1][1] and balance <= points[index + 1][1]:
            indices_to_keep.add(index)
        if balance >= points[index - 1][1] and balance >= points[index + 1][1]:
            indices_to_keep.add(index)

    step = max(1, len(points) // max_points)
    for index in range(0, len(points), step):
        indices_to_keep.add(index)

    return [points[index] for index in sorted(indices_to_keep)]


def _y_axis_ticks(y_min: float, y_max: float, *, tick_count: int = 5) -> list[float]:
    if y_min == y_max:
        return [y_min]
    ticks: list[float] = []
    for tick_index in range(tick_count):
        ratio = tick_index / (tick_count - 1)
        ticks.append(y_min + ratio * (y_max - y_min))
    return ticks


def _x_label_indices(point_count: int, *, max_labels: int = 5) -> list[int]:
    if point_count <= max_labels:
        return list(range(point_count))
    if max_labels == 1:
        return [0]
    step = (point_count - 1) / (max_labels - 1)
    return [round(label_index * step) for label_index in range(max_labels)]


def _date_to_x(
    point_date: date,
    *,
    min_date: date,
    max_date: date,
    plot_left: float,
    plot_width: float,
) -> float:
    min_ordinal = min_date.toordinal()
    max_ordinal = max_date.toordinal()
    if max_ordinal == min_ordinal:
        return plot_left + plot_width / 2
    ratio = (point_date.toordinal() - min_ordinal) / (max_ordinal - min_ordinal)
    return plot_left + ratio * plot_width


def _balance_to_y(
    balance: float,
    *,
    y_min: float,
    y_max: float,
    plot_bottom: float,
    plot_height: float,
) -> float:
    if y_max == y_min:
        return plot_bottom + plot_height / 2
    ratio = (balance - y_min) / (y_max - y_min)
    return plot_bottom + ratio * plot_height


def _flatten_points(points: Sequence[tuple[float, float]]) -> list[float]:
    flat: list[float] = []
    for x_value, y_value in points:
        flat.extend((x_value, y_value))
    return flat


def _area_polygon_points(
    points: Sequence[tuple[date, float]],
    *,
    upper_value: Callable[[float], float],
    lower_value: Callable[[float], float],
    min_date: date,
    max_date: date,
    y_min: float,
    y_max: float,
    plot_left: float,
    plot_bottom: float,
    plot_width: float,
    plot_height: float,
) -> list[tuple[float, float]]:
    polygon: list[tuple[float, float]] = []
    for point_date, balance in points:
        x_value = _date_to_x(
            point_date,
            min_date=min_date,
            max_date=max_date,
            plot_left=plot_left,
            plot_width=plot_width,
        )
        upper_balance = upper_value(balance)
        lower_balance = lower_value(balance)
        polygon.append(
            (
                x_value,
                _balance_to_y(
                    upper_balance,
                    y_min=y_min,
                    y_max=y_max,
                    plot_bottom=plot_bottom,
                    plot_height=plot_height,
                ),
            )
        )
    for point_date, balance in reversed(points):
        x_value = _date_to_x(
            point_date,
            min_date=min_date,
            max_date=max_date,
            plot_left=plot_left,
            plot_width=plot_width,
        )
        lower_balance = lower_value(balance)
        polygon.append(
            (
                x_value,
                _balance_to_y(
                    lower_balance,
                    y_min=y_min,
                    y_max=y_max,
                    plot_bottom=plot_bottom,
                    plot_height=plot_height,
                ),
            )
        )
    return polygon


def build_balance_chart_drawing(
    daily_balances: Sequence[tuple[date, float]],
    *,
    currency: str,
    width: float,
    height: float,
) -> Drawing:
    """Render a static daily balance chart as a ReportLab Drawing flowable."""
    drawing = Drawing(width, height)
    if not daily_balances:
        return drawing

    points = _downsample_daily_balances(daily_balances)
    balances = [balance for _, balance in points]
    min_balance = min(balances)
    max_balance = max(balances)
    axis_min = min(min_balance, 0.0)
    axis_max = max(max_balance, 0.0)
    span = axis_max - axis_min
    if span == 0:
        span = abs(axis_max) or 1.0
    padding = span * 0.1
    y_min = axis_min - padding
    y_max = axis_max + padding

    plot_left = _MARGIN_LEFT
    plot_bottom = _MARGIN_BOTTOM
    plot_width = width - _MARGIN_LEFT - _MARGIN_RIGHT
    plot_height = height - _MARGIN_TOP - _MARGIN_BOTTOM
    min_date = points[0][0]
    max_date = points[-1][0]

    zero_y = _balance_to_y(
        0.0,
        y_min=y_min,
        y_max=y_max,
        plot_bottom=plot_bottom,
        plot_height=plot_height,
    )

    chart_group = Group()
    chart_group.add(
        Line(
            plot_left,
            zero_y,
            plot_left + plot_width,
            zero_y,
            strokeColor=_ZERO_LINE_COLOR,
            strokeWidth=0.75,
            strokeDashArray=[2, 2],
        )
    )

    positive_polygon = _area_polygon_points(
        points,
        upper_value=lambda balance: max(0.0, balance),
        lower_value=lambda _balance: 0.0,
        min_date=min_date,
        max_date=max_date,
        y_min=y_min,
        y_max=y_max,
        plot_left=plot_left,
        plot_bottom=plot_bottom,
        plot_width=plot_width,
        plot_height=plot_height,
    )
    if any(balance > 0 for _, balance in points):
        chart_group.add(
            Polygon(
                _flatten_points(positive_polygon),
                fillColor=_CHART_POSITIVE_FILL,
                strokeColor=None,
                strokeWidth=0,
            )
        )

    deficit_polygon = _area_polygon_points(
        points,
        upper_value=lambda _balance: 0.0,
        lower_value=lambda balance: min(0.0, balance),
        min_date=min_date,
        max_date=max_date,
        y_min=y_min,
        y_max=y_max,
        plot_left=plot_left,
        plot_bottom=plot_bottom,
        plot_width=plot_width,
        plot_height=plot_height,
    )
    if any(balance < 0 for _, balance in points):
        chart_group.add(
            Polygon(
                _flatten_points(deficit_polygon),
                fillColor=_CHART_DEFICIT_FILL,
                strokeColor=None,
                strokeWidth=0,
            )
        )

    line_points: list[tuple[float, float]] = []
    for point_date, balance in points:
        line_points.append(
            (
                _date_to_x(
                    point_date,
                    min_date=min_date,
                    max_date=max_date,
                    plot_left=plot_left,
                    plot_width=plot_width,
                ),
                _balance_to_y(
                    balance,
                    y_min=y_min,
                    y_max=y_max,
                    plot_bottom=plot_bottom,
                    plot_height=plot_height,
                ),
            )
        )
    chart_group.add(
        PolyLine(
            line_points,
            strokeColor=PRIMARY,
            strokeWidth=_LINE_WIDTH,
        )
    )

    for tick_value in _y_axis_ticks(y_min, y_max):
        tick_y = _balance_to_y(
            tick_value,
            y_min=y_min,
            y_max=y_max,
            plot_bottom=plot_bottom,
            plot_height=plot_height,
        )
        chart_group.add(
            Line(
                plot_left - 3,
                tick_y,
                plot_left,
                tick_y,
                strokeColor=_AXIS_COLOR,
                strokeWidth=0.5,
            )
        )
        chart_group.add(
            String(
                plot_left - 6,
                tick_y - 3,
                _format_axis_money(tick_value, currency),
                fontName=_CHART_AXIS_FONT,
                fontSize=7,
                fillColor=_AXIS_COLOR,
                textAnchor="end",
            )
        )

    for label_index in _x_label_indices(len(points)):
        point_date, _balance = points[label_index]
        label_x = _date_to_x(
            point_date,
            min_date=min_date,
            max_date=max_date,
            plot_left=plot_left,
            plot_width=plot_width,
        )
        chart_group.add(
            String(
                label_x,
                plot_bottom - 14,
                _format_axis_date(point_date),
                fontName=_CHART_AXIS_FONT,
                fontSize=7,
                fillColor=_AXIS_COLOR,
                textAnchor="middle",
            )
        )

    chart_group.add(
        Line(
            plot_left,
            plot_bottom,
            plot_left + plot_width,
            plot_bottom,
            strokeColor=_AXIS_COLOR,
            strokeWidth=0.5,
        )
    )
    chart_group.add(
        Line(
            plot_left,
            plot_bottom,
            plot_left,
            plot_bottom + plot_height,
            strokeColor=_AXIS_COLOR,
            strokeWidth=0.5,
        )
    )

    drawing.add(chart_group)
    return drawing
