from __future__ import annotations

import json
from importlib import resources
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from src.domain.date_pattern import parse_pattern
from src.domain.entities import EntryCreateDTO, EntryType
from src.domain.exceptions import (
    DatePatternParseError,
    TemplateNotFoundError,
    TemplateValidationError,
)

_SCHEMA_FILE = "schema.json"


class ForecastTemplate(BaseModel):
    model_config = ConfigDict(frozen=True)

    template_id: str
    name: str
    description: str
    suggested_initial_balance: float
    suggested_base_currency: str
    entries: tuple[EntryCreateDTO, ...]


class _TemplateRawEntry(BaseModel):
    entry_type: EntryType
    name: str
    date_pattern: str
    amount: float
    currency: str
    category: str | None = None
    is_active: bool = True

    @field_validator("date_pattern")
    @classmethod
    def _validate_date_pattern(cls, value: str) -> str:
        try:
            parse_pattern(value)
        except DatePatternParseError as exc:
            raise ValueError(str(exc)) from exc
        return value

    @field_validator("currency")
    @classmethod
    def _normalize_currency(cls, value: str) -> str:
        return value.upper()


class _TemplateRaw(BaseModel):
    template_id: str
    name: str
    description: str
    suggested_initial_balance: float
    suggested_base_currency: str
    entries: list[_TemplateRawEntry]


class TemplateService:
    @staticmethod
    def list_templates() -> list[ForecastTemplate]:
        return [TemplateService.load(template_id) for template_id in _template_ids()]

    @staticmethod
    def load(template_id: str) -> ForecastTemplate:
        if template_id not in _template_ids():
            raise TemplateNotFoundError(template_id)

        raw_data = TemplateService._read_template_json(template_id)
        return TemplateService._parse_template(raw_data, template_id)

    @staticmethod
    def _read_template_json(template_id: str) -> dict[str, Any]:
        try:
            text = (
                resources.files("src.templates")
                .joinpath(f"{template_id}.json")
                .read_text(encoding="utf-8")
            )
        except FileNotFoundError as exc:
            raise TemplateNotFoundError(template_id) from exc

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            msg = f"Invalid JSON in template {template_id!r}: {exc}"
            raise TemplateValidationError(msg) from exc

        if not isinstance(parsed, dict):
            msg = f"Template {template_id!r} must be a JSON object"
            raise TemplateValidationError(msg)

        return parsed

    @staticmethod
    def _parse_template(raw_data: dict[str, Any], template_id: str) -> ForecastTemplate:
        try:
            raw = _TemplateRaw.model_validate(raw_data)
        except ValidationError as exc:
            msg = f"Template {template_id!r} validation failed: {exc}"
            raise TemplateValidationError(msg) from exc

        if raw.template_id != template_id:
            msg = f"Template file {template_id!r} has mismatched template_id {raw.template_id!r}"
            raise TemplateValidationError(msg)

        entries = tuple(
            EntryCreateDTO(
                entry_type=entry.entry_type,
                name=entry.name,
                date_pattern=entry.date_pattern,
                amount=entry.amount,
                currency=entry.currency,
                category=entry.category,
                is_active=entry.is_active,
            )
            for entry in raw.entries
        )

        return ForecastTemplate(
            template_id=raw.template_id,
            name=raw.name,
            description=raw.description,
            suggested_initial_balance=raw.suggested_initial_balance,
            suggested_base_currency=raw.suggested_base_currency,
            entries=entries,
        )


def _template_ids() -> tuple[str, ...]:
    package = resources.files("src.templates")
    return tuple(
        sorted(
            path.name.removesuffix(".json")
            for path in package.iterdir()
            if path.name.endswith(".json") and path.name != _SCHEMA_FILE
        )
    )
