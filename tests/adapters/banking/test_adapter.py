import decimal
import string

import faker
import pytest

from huma_signals.adapters.banking import adapter
from tests.helpers import vcr_helpers

fake = faker.Faker()


def describe_adapter() -> None:
    @pytest.fixture
    def plaid_public_token() -> str:
        return "public-sandbox-1fc00cdc-96b0-4668-b6cd-4a4aec9f576d"

    @pytest.fixture
    def wallet_address() -> str:
        return fake.lexify(text=f"0x{'?' * 40}", letters="abcdefABCDEF" + string.digits)

    def it_returns_the_name() -> None:
        assert adapter.BankingAdapter.name == "banking"

    def it_returns_the_required_inputs() -> None:
        assert adapter.BankingAdapter.required_inputs == [
            "wallet_address",
            "plaid_public_token",
        ]

    async def it_fetches_signals_from_plaid(
        wallet_address: str,
        plaid_public_token: str,
    ) -> None:
        with vcr_helpers.use_cassette(fixture_file_path="adapters/banking.yml"):
            signals = await adapter.BankingAdapter().fetch(
                wallet_address=wallet_address, plaid_public_token=plaid_public_token
            )
            assert signals.income.total_income == decimal.Decimal("24000")
            assert signals.current_account_balance == 0
