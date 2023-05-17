import pydantic
import pytest

from huma_signals.clients.polygon_client import polygon_client
from tests.helpers import vcr_helpers

_FIXTURE_BASE_PATH = "/clients/polygon_client"


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    polygonscan_base_url: str
    polygonscan_api_key: str


settings = Settings()


def describe_PolygonClient() -> None:
    @pytest.fixture
    def client() -> polygon_client.PolygonClient:
        return polygon_client.PolygonClient(
            polygonscan_base_url=settings.polygonscan_base_url,
            polygonscan_api_key=settings.polygonscan_api_key,
        )

    def describe_get_transactions() -> None:
        async def it_returns_the_transactions(
            client: polygon_client.PolygonClient, real_polygon_address: str
        ) -> None:
            with vcr_helpers.use_cassette(
                fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_transactions.yml"
            ):
                transactions = await client.get_transactions(real_polygon_address)
                assert len(transactions) > 1400

        def when_the_address_has_no_records() -> None:
            async def it_works_properly(client: polygon_client.PolygonClient) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_transactions_no_records.yml"
                ):
                    transactions = await client.get_transactions("0x1234")
                    assert len(transactions) == 0
