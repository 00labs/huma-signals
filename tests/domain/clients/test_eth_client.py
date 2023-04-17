import pytest

from huma_signals.domain.clients.eth_client import eth_client
from tests.helpers import vcr_helpers

_FIXTURE_BASE_PATH = "/domain/clients/eth_client"


def describe_EthClient() -> None:
    @pytest.fixture
    def client() -> eth_client.EthClient:
        return eth_client.EthClient()

    def describe_get_transactions() -> None:
        async def it_returns_the_transactions(
            client: eth_client.EthClient, real_eth_address: str
        ) -> None:
            with vcr_helpers.use_cassette(
                fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_transactions.yml"
            ):
                transactions = await client.get_transactions(real_eth_address)
                assert len(transactions) > 1400

        def when_the_address_has_no_records() -> None:
            async def it_works_properly(client: eth_client.EthClient) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_transactions_no_records.yml"
                ):
                    transactions = await client.get_transactions("0x1234")
                    assert len(transactions) == 0