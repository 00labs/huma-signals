import pytest

from huma_signals.adapters.ethereum_wallet import adapter


@pytest.fixture
def valid_address() -> str:
    # vitalik.eth
    return "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


def describe_wallet_eth_txns_adapter() -> None:
    async def it_works_e2e(valid_address: str) -> None:
        result = await adapter.EthereumWalletAdapter().fetch(valid_address)
        assert result is not None
        assert result.total_transactions > 1400
        assert result.total_sent > 900
        assert result.total_received > 400
        assert result.total_transactions == result.total_sent + result.total_received
        assert result.wallet_tenure_in_days > 2600
        assert result.total_income_90days > 0
        assert result.total_transactions_90days > 0

    def it_validate_etherscan_base_url() -> None:
        with pytest.raises(ValueError):
            adapter.EthereumWalletAdapter(etherscan_base_url="")

    def it_validate_etherscan_api_key() -> None:
        with pytest.raises(ValueError):
            adapter.EthereumWalletAdapter(etherscan_api_key="")

    async def it_handles_address_with_no_records() -> None:
        result = await adapter.EthereumWalletAdapter().fetch("0x1234")
        assert result is not None
        assert result.total_transactions == 0
        assert result.total_sent == 0
        assert result.total_received == 0
        assert result.wallet_tenure_in_days == 0
        assert result.total_income_90days == 0
        assert result.total_transactions_90days == 0
