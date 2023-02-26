import decimal

import pytest

from huma_signals.adapters.banking import adapter
from tests.helpers import vcr_helpers


def describe_adapter() -> None:
    @pytest.fixture
    def plaid_public_token() -> str:
        return "public-sandbox-88a2c0a1-48fb-4ca4-89a2-f9205951f43d"

    def it_returns_the_name() -> None:
        assert adapter.BankingAdapter.name == "banking"

    def it_returns_the_required_inputs() -> None:
        assert adapter.BankingAdapter.required_inputs == [
            "plaid_bank_account_id",
            "plaid_public_token",
        ]

    async def it_fetches_signals_from_plaid(
        plaid_public_token: str,
    ) -> None:
        with vcr_helpers.use_cassette(fixture_file_path="adapters/banking.yml"):
            signals = await adapter.BankingAdapter().fetch(
                plaid_public_token=plaid_public_token
            )
            assert signals.income.total_income == decimal.Decimal("24000")
            assert signals.current_account_balance == 0
