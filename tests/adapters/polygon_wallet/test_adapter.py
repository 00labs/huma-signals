import pytest

from huma_signals.adapters.polygon_wallet import adapter


@pytest.fixture
def valid_address() -> str:
    return "0xe22434cca7f03cb4d3d26029e1df16487e83fca1"


def describe_polygon_wallet_adapter() -> None:
    async def it_works_e2e(valid_address: str) -> None:
        result = await adapter.PolygonWalletAdapter().fetch(valid_address)
        assert result is not None
        assert result.total_transactions > 37
        assert result.total_sent > 5
        assert result.total_received > 400
        assert result.total_transactions == result.total_sent + result.total_received
        assert result.wallet_tenure_in_days > 180
        assert result.total_income_90days > 0
        assert result.total_transactions_90days > 0

    def it_validate_etherscan_base_url() -> None:
        with pytest.raises(ValueError):
            adapter.PolygonWalletAdapter(polygonscan_base_url="")

    def it_validate_etherscan_api_key() -> None:
        with pytest.raises(ValueError):
            adapter.PolygonWalletAdapter(polygonscan_api_key="")

    async def it_handles_address_with_no_records() -> None:
        result = await adapter.PolygonWalletAdapter().fetch("0x1234")
        assert result is not None
        assert result.total_transactions == 0
        assert result.total_sent == 0
        assert result.total_received == 0
        assert result.wallet_tenure_in_days == 0
        assert result.total_income_90days == 0
        assert result.total_transactions_90days == 0
