from decimal import Decimal

from huma_signals.adapters.lending_pools.adapter import LendingPoolAdapter


def describe_adapter():
    def it_returns_the_name():
        assert LendingPoolAdapter.name == "lending_pool"

    def it_returns_the_required_inputs():
        assert LendingPoolAdapter.required_inputs == ["pool_address"]

    def it_fetches_the_signals_from_creditline_pool():
        pool_address = "0xA22D20FB0c9980fb96A9B0B5679C061aeAf5dDE4"
        signals = LendingPoolAdapter.fetch(pool_address)
        assert signals.pool_address == pool_address
        assert signals.apr == Decimal("1000")
        assert signals.max_credit_amount == Decimal("10000000000")
        assert signals.token_name == "TestToken"
        assert signals.token_symbol == "USDC"
        assert signals.token_decimal == 6
        assert signals.interval_in_days_max == 90
        assert signals.interval_in_days_min == 0
        assert signals.invoice_amount_ratio == 0.8
        assert signals.is_testnet is True

    def it_fetches_the_signals_from_invoice_factoring_pool():
        pool_address = "0x11672c0bBFF498c72BC2200f42461c0414855042"
        signals = LendingPoolAdapter.fetch(pool_address)
        assert signals.pool_address == pool_address
        assert signals.apr == Decimal("0")
        assert signals.max_credit_amount == Decimal("1_000_000_000")
        assert signals.token_name == "TestToken"
        assert signals.token_symbol == "USDC"
        assert signals.token_decimal == 6
        assert signals.interval_in_days_max == 90
        assert signals.interval_in_days_min == 0
        assert signals.invoice_amount_ratio == 0.8
        assert signals.is_testnet is True
