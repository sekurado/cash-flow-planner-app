from __future__ import annotations

import pytest

from src.domain.currencies import COMMON_CURRENCIES
from src.integrations.exchange_rate_fetcher import _MOCK_USD_RATES


@pytest.mark.unit
def test_common_currencies_are_unique_three_letter_codes() -> None:
    assert len(COMMON_CURRENCIES) == len(set(COMMON_CURRENCIES))
    for code in COMMON_CURRENCIES:
        assert len(code) == 3
        assert code.isalpha()
        assert code.isupper()


@pytest.mark.unit
def test_common_currencies_include_requested_regions() -> None:
    required = {"USD", "EUR", "KZT", "UZS", "AED", "SAR", "TRY", "ILS"}
    assert required.issubset(set(COMMON_CURRENCIES))


@pytest.mark.unit
def test_mock_usd_rates_cover_all_common_currencies() -> None:
    assert set(_MOCK_USD_RATES) == set(COMMON_CURRENCIES)
