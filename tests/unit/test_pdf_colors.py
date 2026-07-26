from __future__ import annotations

import pytest
from reportlab.lib import colors  # type: ignore[import-untyped]

from src.export.pdf_colors import (
    DEFICIT_AMBER_BG,
    EXPENSE_RED,
    INCOME_GREEN,
    NEUTRAL_TEXT,
    PRIMARY,
    delta_text_color,
    money_text_color,
)


@pytest.mark.unit
def test_palette_matches_theme_tokens() -> None:
    assert INCOME_GREEN.hexval() == "0x10b981"
    assert EXPENSE_RED.hexval() == "0xef4444"
    assert DEFICIT_AMBER_BG.hexval() == "0xfef3c7"
    assert PRIMARY.hexval() == "0x6366f1"
    assert NEUTRAL_TEXT == colors.black


@pytest.mark.unit
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (100.0, INCOME_GREEN),
        (0.01, INCOME_GREEN),
        (0.0, EXPENSE_RED),
        (-50.0, EXPENSE_RED),
    ],
)
def test_money_text_color(value: float, expected: colors.Color) -> None:
    assert money_text_color(value) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("delta", "higher_is_better", "expected"),
    [
        (10.0, True, INCOME_GREEN),
        (-10.0, True, EXPENSE_RED),
        (10.0, False, EXPENSE_RED),
        (-10.0, False, INCOME_GREEN),
        (0.0, True, NEUTRAL_TEXT),
        (0.0, False, NEUTRAL_TEXT),
    ],
)
def test_delta_text_color(
    delta: float,
    higher_is_better: bool,
    expected: colors.Color,
) -> None:
    assert delta_text_color(delta, higher_is_better=higher_is_better) == expected
