import pytest

from huma_signals.adapters.ethereum_wallet.adapter import EthereumWalletAdapter


@pytest.fixture(scope="session", autouse=True)
def valid_address() -> str:
    # vitalik.eth
    return "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


def describe_wallet_eth_txns_adapter():
    def it_works_e2e(valid_address):
        result = EthereumWalletAdapter.fetch(valid_address)
        assert result is not None
        assert result.total_transactions > 1400
        assert result.total_sent > 900
        assert result.total_received > 400
        assert result.total_transactions == result.total_sent + result.total_received
        assert result.wallet_teneur_in_days > 2600
        assert result.total_income_90days > 0
        assert result.total_transactions_90days > 0
