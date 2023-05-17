import datetime

import pytest

from huma_signals.adapters.ethereum_wallet import adapter
from huma_signals.clients.eth_client import eth_types
from huma_signals.commons import datetime_utils
from tests.fixtures.clients.eth import eth_type_factories, fake_eth_client
from tests.helpers import address_helpers


def describe_EthereumWalletAdapter() -> None:
    @pytest.fixture
    def borrower_wallet_address() -> str:
        return address_helpers.fake_hex_address()

    @pytest.fixture
    def wallet_tenure_in_days() -> int:
        return 760

    @pytest.fixture
    def earliest_tx_timestamp(wallet_tenure_in_days: int) -> int:
        a_long_time_ago = datetime_utils.tz_aware_utc_now() - datetime.timedelta(
            days=wallet_tenure_in_days
        )
        return int(a_long_time_ago.timestamp())

    @pytest.fixture
    def timestamp_45_days_ago() -> int:
        past = datetime_utils.tz_aware_utc_now() - datetime.timedelta(days=45)
        return int(past.timestamp())

    @pytest.fixture
    def amount_in_wei() -> int:
        return 9_000_000_000_000_000_000

    @pytest.fixture
    def transactions(
        borrower_wallet_address: str,
        earliest_tx_timestamp: int,
        timestamp_45_days_ago: int,
        amount_in_wei: int,
    ) -> list[eth_types.EthTransaction]:
        return [
            # Sent transactions.
            # This is the earliest transaction by timestamp.
            eth_type_factories.EthTransactionFactory.create(
                from_=borrower_wallet_address,
                time_stamp=str(earliest_tx_timestamp),
                value=str(amount_in_wei + 1),
            ),
            eth_type_factories.EthTransactionFactory.create(
                from_=borrower_wallet_address,
                time_stamp=str(timestamp_45_days_ago),
                value=str(amount_in_wei + 2),
            ),
            eth_type_factories.EthTransactionFactory.create(
                from_=borrower_wallet_address,
                time_stamp=str(earliest_tx_timestamp + 2),
                value=str(amount_in_wei + 3),
            ),
            # Received transactions.
            eth_type_factories.EthTransactionFactory.create(
                to=borrower_wallet_address,
                time_stamp=str(timestamp_45_days_ago),
                value=str(amount_in_wei),
            ),
            eth_type_factories.EthTransactionFactory.create(
                to=borrower_wallet_address,
                time_stamp=str(earliest_tx_timestamp + 200),
                value=str(amount_in_wei + 4),
            ),
        ]

    @pytest.fixture
    def adapter_(
        transactions: list[eth_types.EthTransaction],
    ) -> adapter.EthereumWalletAdapter:
        eth_client_ = fake_eth_client.FakeEthClient(transactions=transactions)
        return adapter.EthereumWalletAdapter(eth_client_=eth_client_)

    async def it_fetches_the_signals(
        adapter_: adapter.EthereumWalletAdapter,
        borrower_wallet_address: str,
        wallet_tenure_in_days: int,
        transactions: list[eth_types.EthTransaction],
        amount_in_wei: int,
    ) -> None:
        result = await adapter_.fetch(borrower_wallet_address)
        assert result is not None
        assert result.total_transactions == len(transactions)
        assert result.total_sent == 3
        assert result.total_received == 2
        assert result.wallet_tenure_in_days == wallet_tenure_in_days
        assert result.total_income_90days == amount_in_wei
        assert result.total_transactions_90days == 2

    def when_there_are_no_transactions() -> None:
        @pytest.fixture
        def transactions() -> list[eth_types.EthTransaction]:
            return []

        async def it_returns_the_correct_signals(
            adapter_: adapter.EthereumWalletAdapter, borrower_wallet_address: str
        ) -> None:
            result = await adapter_.fetch(borrower_wallet_address)
            assert result is not None
            assert result.total_transactions == 0
            assert result.total_sent == 0
            assert result.total_received == 0
            assert result.wallet_tenure_in_days == 0
            assert result.total_income_90days == 0
            assert result.total_transactions_90days == 0
