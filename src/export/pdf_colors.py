from __future__ import annotations

from reportlab.lib import colors  # type: ignore[import-untyped]

# Hex values aligned with qml/components/ThemeTokens.qml (light / print palette).
INCOME_GREEN = colors.HexColor("#10B981")
EXPENSE_RED = colors.HexColor("#EF4444")
DEFICIT_AMBER_BG = colors.HexColor("#FEF3C7")
PRIMARY = colors.HexColor("#6366F1")
TABLE_HEADER_BG = colors.grey
NEUTRAL_TEXT = colors.black


def money_text_color(value: float) -> colors.Color:
    """Return green for positive amounts, red for zero or negative."""
    if value > 0:
        return INCOME_GREEN
    return EXPENSE_RED


def delta_text_color(delta: float, *, higher_is_better: bool = True) -> colors.Color:
    """Return semantic color for a numeric delta (neutral when zero)."""
    if delta == 0:
        return NEUTRAL_TEXT
    favorable = delta > 0 if higher_is_better else delta < 0
    return INCOME_GREEN if favorable else EXPENSE_RED
