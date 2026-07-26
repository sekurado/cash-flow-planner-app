from __future__ import annotations

import re
from re import Pattern

from PySide6.QtCore import QCoreApplication

_AUDIT_CONTEXT = "AuditLog"
_ENTRY_TYPE_CONTEXT = "EntriesPage"
_SEGMENT_SEPARATOR = "; "

_SEGMENT_PATTERNS: list[tuple[Pattern[str], str]] = [
    (re.compile(r"^Created forecast '(.+)'$"), "Created forecast '%1'"),
    (re.compile(r"^Deleted forecast '(.+)'$"), "Deleted forecast '%1'"),
    (re.compile(r"^Renamed forecast to '(.+)'$"), "Renamed forecast to '%1'"),
    (re.compile(r"^Updated opening balance to (.+)$"), "Updated opening balance to %1"),
    (re.compile(r"^Updated base currency to (.+)$"), "Updated base currency to %1"),
    (re.compile(r"^Updated forecast '(.+)'$"), "Updated forecast '%1'"),
    (
        re.compile(r"^Added cash flow '(.+)' \((income|expense)\)$"),
        "Added cash flow '%1' (%2)",
    ),
    (re.compile(r"^Removed cash flow '(.+)'$"), "Removed cash flow '%1'"),
    (re.compile(r"^Updated cash flow '(.+)': (.+)$"), "Updated cash flow '%1': %2"),
    (re.compile(r"^Updated cash flow '(.+)'$"), "Updated cash flow '%1'"),
]

_DETAIL_PATTERNS: list[tuple[Pattern[str], str]] = [
    (re.compile(r"^amount (.+) → (.+)$"), "amount %1 → %2"),
    (re.compile(r"^renamed to '(.+)'$"), "renamed to '%1'"),
    (
        re.compile(r"^type (income|expense) → (income|expense)$"),
        "type %1 → %2",
    ),
    (re.compile(r"^currency (.+) → (.+)$"), "currency %1 → %2"),
    (re.compile(r"^schedule updated$"), "schedule updated"),
    (re.compile(r"^category updated$"), "category updated"),
    (re.compile(r"^marked active$"), "marked active"),
    (re.compile(r"^marked inactive$"), "marked inactive"),
]


def _apply_placeholders(template: str, args: tuple[str, ...]) -> str:
    result = template
    for index, arg in enumerate(args, start=1):
        result = result.replace(f"%{index}", arg)
    return result


def _translate(context: str, source: str, *args: str) -> str:
    translated = QCoreApplication.translate(context, source)
    if not args:
        return translated
    return _apply_placeholders(translated, args)


def _translate_entry_type(value: str) -> str:
    label = value.capitalize()
    return QCoreApplication.translate(_ENTRY_TYPE_CONTEXT, label)


def _translate_detail_segment(segment: str) -> str:
    stripped = segment.strip()
    for pattern, template in _DETAIL_PATTERNS:
        match = pattern.fullmatch(stripped)
        if match is None:
            continue
        groups = match.groups()
        if template == "type %1 → %2":
            return _translate(
                _AUDIT_CONTEXT,
                template,
                _translate_entry_type(groups[0]),
                _translate_entry_type(groups[1]),
            )
        return _translate(_AUDIT_CONTEXT, template, *groups)
    return stripped


def _translate_detail_list(details: str) -> str:
    parts = [part.strip() for part in details.split(_SEGMENT_SEPARATOR) if part.strip()]
    if not parts:
        return details
    return _SEGMENT_SEPARATOR.join(_translate_detail_segment(part) for part in parts)


def _translate_segment(segment: str) -> str:
    stripped = segment.strip()
    for pattern, template in _SEGMENT_PATTERNS:
        match = pattern.fullmatch(stripped)
        if match is None:
            continue
        groups = match.groups()
        if template == "Added cash flow '%1' (%2)":
            return _translate(
                _AUDIT_CONTEXT,
                template,
                groups[0],
                _translate_entry_type(groups[1]),
            )
        if template == "Updated cash flow '%1': %2":
            return _translate(
                _AUDIT_CONTEXT,
                template,
                groups[0],
                _translate_detail_list(groups[1]),
            )
        return _translate(_AUDIT_CONTEXT, template, *groups)
    return stripped


def translate_audit_summary(summary: str) -> str:
    source = summary.strip()
    if not source:
        return ""

    translated_whole = _translate_segment(source)
    if translated_whole != source:
        return translated_whole

    segments = [segment.strip() for segment in source.split(_SEGMENT_SEPARATOR) if segment.strip()]
    if len(segments) <= 1:
        return translated_whole
    return _SEGMENT_SEPARATOR.join(_translate_segment(segment) for segment in segments)


def _register_i18n_catalog() -> None:
    """Literal translate() calls for pyside6-lupdate extraction only."""
    QCoreApplication.translate("AuditLog", "Created forecast '%1'")
    QCoreApplication.translate("AuditLog", "Deleted forecast '%1'")
    QCoreApplication.translate("AuditLog", "Renamed forecast to '%1'")
    QCoreApplication.translate("AuditLog", "Updated opening balance to %1")
    QCoreApplication.translate("AuditLog", "Updated base currency to %1")
    QCoreApplication.translate("AuditLog", "Updated forecast '%1'")
    QCoreApplication.translate("AuditLog", "Added cash flow '%1' (%2)")
    QCoreApplication.translate("AuditLog", "Removed cash flow '%1'")
    QCoreApplication.translate("AuditLog", "Updated cash flow '%1'")
    QCoreApplication.translate("AuditLog", "Updated cash flow '%1': %2")
    QCoreApplication.translate("AuditLog", "amount %1 → %2")
    QCoreApplication.translate("AuditLog", "renamed to '%1'")
    QCoreApplication.translate("AuditLog", "type %1 → %2")
    QCoreApplication.translate("AuditLog", "currency %1 → %2")
    QCoreApplication.translate("AuditLog", "schedule updated")
    QCoreApplication.translate("AuditLog", "category updated")
    QCoreApplication.translate("AuditLog", "marked active")
    QCoreApplication.translate("AuditLog", "marked inactive")
