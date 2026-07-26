from __future__ import annotations


class DatePatternParseError(ValueError):
    """Raised when a date-pattern string cannot be parsed."""


class CurrencyConversionError(ValueError):
    """Raised when no applicable exchange rate exists for currency conversion."""


class InvalidExchangeRateTargetError(ValueError):
    """Raised when an exchange rate pair is invalid (e.g. same source and target)."""


class SimulationOverflowError(ValueError):
    """Raised when the simulation date range exceeds the 10-year hard limit."""


class ExportError(OSError):
    """Raised when a simulation export cannot be written to disk."""


class PlanExportError(Exception):
    """Raised when a plan bundle export fails."""


class PlanImportError(Exception):
    """Raised when a plan bundle import fails."""


class DuplicatePlanNameError(ValueError):
    """Raised when a plan name is already used by another plan."""


class FetchRatesError(OSError):
    """Raised when live exchange rates cannot be fetched from the configured API."""


class TemplateNotFoundError(LookupError):
    """Raised when a forecast template ID is not found."""

    def __init__(self, template_id: str) -> None:
        self.template_id = template_id
        super().__init__(f"Forecast template not found: {template_id!r}")


class TemplateValidationError(ValueError):
    """Raised when a forecast template file fails validation."""


class SuggestionAnalysisError(ValueError):
    """Raised when suggestion analysis cannot proceed (e.g. missing simulation result)."""
