import decimal

from huma_signals.adapters.lending_pools import adapter
from tests.helpers import vcr_helpers

_FIXTURE_BASE_PATH = "/domain/adapters/lending_pools"
# Don't match on path since the API key is embedded in the path.
_VCR_MATCH_ON = ["method", "scheme", "host", "port", "query"]


def describe_adapter() -> None:
    def it_returns_the_name() -> None:
        assert adapter.LendingPoolAdapter.name == "lending_pool"

    def it_returns_the_required_inputs() -> None:
        assert adapter.LendingPoolAdapter.required_inputs == ["pool_address"]

    async def it_fetches_the_signals_from_creditline_pool() -> None:
        with vcr_helpers.use_cassette(
            fixture_file_path=f"{_FIXTURE_BASE_PATH}/credit_line_pool_signals.yml",
            match_on=_VCR_MATCH_ON,
        ):
            pool_address = "0xA22D20FB0c9980fb96A9B0B5679C061aeAf5dDE4"
            signals = await adapter.LendingPoolAdapter().fetch(pool_address)
            assert signals.pool_address == pool_address
            assert signals.apr == decimal.Decimal("1000")
            assert signals.max_credit_amount == decimal.Decimal("10000000000")
            assert signals.token_name == "TestToken"
            assert signals.token_symbol == "USDC"
            assert signals.token_decimal == 6
            assert signals.interval_in_days_max == 90
            assert signals.interval_in_days_min == 0
            assert signals.invoice_amount_ratio == 0.8
            assert signals.is_testnet is True

    async def it_fetches_the_signals_from_invoice_factoring_pool() -> None:
        with vcr_helpers.use_cassette(
            fixture_file_path=f"{_FIXTURE_BASE_PATH}/invoice_factoring_pool_signals.yml",
            match_on=_VCR_MATCH_ON,
        ):
            pool_address = "0x11672c0bBFF498c72BC2200f42461c0414855042"
            signals = await adapter.LendingPoolAdapter().fetch(pool_address)
            assert signals.pool_address == pool_address
            assert signals.apr == decimal.Decimal("0")
            assert signals.max_credit_amount == decimal.Decimal("1_000_000_000")
            assert signals.token_name == "TestToken"
            assert signals.token_symbol == "USDC"
            assert signals.token_decimal == 6
            assert signals.interval_in_days_max == 90
            assert signals.interval_in_days_min == 0
            assert signals.invoice_amount_ratio == 0.8
            assert signals.is_testnet is True
