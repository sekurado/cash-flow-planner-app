from __future__ import annotations

import pytest

from src.app.i18n.methodology_content import (
    methodology_intro,
    methodology_sections,
)
from src.export.metadata import METHODOLOGY_VERSION


@pytest.mark.unit
def test_methodology_version_matches_metadata() -> None:
    assert METHODOLOGY_VERSION == "1.0"


@pytest.mark.unit
def test_methodology_sections_count_and_order() -> None:
    sections = methodology_sections()
    assert len(sections) == 6
    assert sections[0].heading == "Daily running balance"
    assert sections[1].heading == "First cash shortfall"
    assert sections[2].heading == "How cash flows are scheduled"
    assert sections[4].heading == "Exchange rate sources"
    assert sections[5].heading == "Temporary overrides"


@pytest.mark.unit
def test_methodology_english_strings_use_glossary_terms() -> None:
    intro = methodology_intro()
    bodies = [section.body for section in methodology_sections()]
    combined = " ".join([intro, *bodies]).lower()

    assert "forecast" in combined
    assert "cash flow" in combined
    assert "cash shortfall" in combined
