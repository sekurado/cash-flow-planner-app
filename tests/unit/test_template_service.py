from __future__ import annotations

import json
from typing import Any

import pytest

from src.domain.entities import EntryType
from src.domain.exceptions import TemplateNotFoundError, TemplateValidationError
from src.domain.template_service import ForecastTemplate, TemplateService


def test_list_templates_returns_all_bundled_templates() -> None:
    templates = TemplateService.list_templates()

    assert len(templates) == 3
    assert {template.template_id for template in templates} == {
        "consulting_firm",
        "retail_shop",
        "saas_startup",
    }
    for template in templates:
        assert template.name
        assert template.description
        assert template.entries


def test_load_saas_startup_returns_validated_template() -> None:
    template = TemplateService.load("saas_startup")

    assert isinstance(template, ForecastTemplate)
    assert template.template_id == "saas_startup"
    assert template.name == "SaaS startup"
    assert template.suggested_initial_balance == 50000.0
    assert template.suggested_base_currency == "USD"
    assert len(template.entries) >= 6

    first_entry = template.entries[0]
    assert first_entry.entry_type == EntryType.INCOME
    assert first_entry.name == "MRR — Subscriptions"
    assert first_entry.date_pattern == "01.."
    assert first_entry.amount == 12000.0
    assert first_entry.currency == "USD"
    assert first_entry.category == "revenue"
    assert first_entry.is_active is True


def test_load_unknown_template_raises_not_found() -> None:
    with pytest.raises(TemplateNotFoundError, match="not_a_template"):
        TemplateService.load("not_a_template")


def test_parse_template_invalid_entry_raises_validation_error() -> None:
    raw_data: dict[str, Any] = {
        "template_id": "saas_startup",
        "name": "SaaS startup",
        "description": "Test template",
        "suggested_initial_balance": 1000.0,
        "suggested_base_currency": "USD",
        "entries": [
            {
                "entry_type": "income",
                "name": "Bad pattern",
                "date_pattern": "not-a-pattern",
                "amount": 100.0,
                "currency": "USD",
            }
        ],
    }

    with pytest.raises(TemplateValidationError, match="validation failed"):
        TemplateService._parse_template(raw_data, "saas_startup")


def test_parse_template_mismatched_id_raises_validation_error() -> None:
    raw_data: dict[str, Any] = {
        "template_id": "other_id",
        "name": "SaaS startup",
        "description": "Test template",
        "suggested_initial_balance": 1000.0,
        "suggested_base_currency": "USD",
        "entries": [
            {
                "entry_type": "income",
                "name": "Salary",
                "date_pattern": "01..",
                "amount": 100.0,
                "currency": "USD",
            }
        ],
    }

    with pytest.raises(TemplateValidationError, match="mismatched template_id"):
        TemplateService._parse_template(raw_data, "saas_startup")


def test_load_malformed_json_raises_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _bad_loads(_text: str) -> dict[str, Any]:
        msg = "Expecting value"
        raise json.JSONDecodeError(msg, "{bad", 0)

    monkeypatch.setattr(json, "loads", _bad_loads)

    with pytest.raises(TemplateValidationError, match="Invalid JSON"):
        TemplateService.load("saas_startup")


def test_load_non_object_json_raises_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _list_loads(_text: str) -> list[str]:
        return ["not", "an", "object"]

    monkeypatch.setattr(json, "loads", _list_loads)

    with pytest.raises(TemplateValidationError, match="must be a JSON object"):
        TemplateService.load("saas_startup")


def test_read_template_missing_file_raises_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    from importlib import resources

    real_files = resources.files

    def _files(package: str) -> object:
        pkg = real_files(package)
        if package != "src.templates":
            return pkg

        class _Pkg:
            def iterdir(self) -> object:
                return pkg.iterdir()

            def joinpath(self, name: str) -> object:
                if name == "saas_startup.json":

                    class _MissingPath:
                        def read_text(self, *, encoding: str) -> str:
                            raise FileNotFoundError("missing")

                    return _MissingPath()
                return pkg.joinpath(name)

        return _Pkg()

    monkeypatch.setattr("src.domain.template_service.resources.files", _files)

    with pytest.raises(TemplateNotFoundError, match="saas_startup"):
        TemplateService.load("saas_startup")
