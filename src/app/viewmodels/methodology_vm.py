from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from src.app.i18n.methodology_content import (
    is_date_patterns_group,
    methodology_intro,
    methodology_pattern_descriptions,
    methodology_pattern_examples_heading,
    methodology_sections,
)
from src.export.metadata import METHODOLOGY_VERSION

_PATTERN_LITERALS = ("...", "10..", "15.03.", "15.03.2026")


def _section_to_dict(section_heading: str, body: str) -> dict[str, str]:
    return {"heading": section_heading, "body": body}


def _build_groups() -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current_title = ""
    current_sections: list[dict[str, str]] = []

    for section in methodology_sections():
        if section.group_title != current_title:
            if current_title:
                groups.append(
                    {
                        "title": current_title,
                        "sections": current_sections,
                        "hasPatternExamples": is_date_patterns_group(current_title),
                    }
                )
            current_title = section.group_title
            current_sections = []
        current_sections.append(_section_to_dict(section.heading, section.body))

    if current_title:
        groups.append(
            {
                "title": current_title,
                "sections": current_sections,
                "hasPatternExamples": is_date_patterns_group(current_title),
            }
        )
    return groups


def _build_pattern_examples() -> list[dict[str, str]]:
    descriptions = methodology_pattern_descriptions()
    return [
        {"pattern": pattern, "description": description}
        for pattern, description in zip(_PATTERN_LITERALS, descriptions, strict=True)
    ]


class MethodologyViewModel(QObject):
    """Exposes shared methodology copy to the Methodology QML page."""

    introChanged = Signal()
    versionChanged = Signal()
    groupsChanged = Signal()
    patternExamplesHeadingChanged = Signal()
    patternExamplesChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._intro = methodology_intro()
        self._version = METHODOLOGY_VERSION
        self._groups = _build_groups()
        self._pattern_examples_heading = methodology_pattern_examples_heading()
        self._pattern_examples = _build_pattern_examples()

    @Property(str, notify=introChanged)
    def intro(self) -> str:
        return self._intro

    @Property(str, notify=versionChanged)
    def version(self) -> str:
        return self._version

    @Property("QVariantList", notify=groupsChanged)  # type: ignore[arg-type]
    def groups(self) -> list[dict[str, Any]]:
        return self._groups

    @Property(str, notify=patternExamplesHeadingChanged)
    def patternExamplesHeading(self) -> str:
        return self._pattern_examples_heading

    @Property("QVariantList", notify=patternExamplesChanged)  # type: ignore[arg-type]
    def patternExamples(self) -> list[dict[str, str]]:
        return self._pattern_examples

    @Slot()
    def retranslate(self) -> None:
        self._intro = methodology_intro()
        self._groups = _build_groups()
        self._pattern_examples_heading = methodology_pattern_examples_heading()
        self._pattern_examples = _build_pattern_examples()
        self.introChanged.emit()
        self.groupsChanged.emit()
        self.patternExamplesHeadingChanged.emit()
        self.patternExamplesChanged.emit()
