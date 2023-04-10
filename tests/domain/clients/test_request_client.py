import pytest

from huma_signals.domain.clients import request_client
from tests.helpers import vcr_helpers

_FIXTURE_BASE_PATH = "/domain/clients/request_client"


def describe_RequestClient() -> None:
    @pytest.fixture
    def client(rn_subgraph_endpoint_url: str) -> request_client.RequestClient:
        return request_client.RequestClient(
            rn_subgraph_endpoint_url=rn_subgraph_endpoint_url
        )

    def describe_get_payments() -> None:
        def when_to_address_is_none() -> None:
            async def it_returns_payment_history(
                client: request_client.RequestClient, from_address: str, to_address: str
            ) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_payments_no_to_address.yml"
                ):
                    payments = await client.get_payments(
                        from_address,
                        None,
                    )
                    assert len(payments) > 0
                    assert payments[-1]["from"] == from_address
                    assert payments[-1]["to"].startswith("0x")

        def when_from_address_is_none() -> None:
            async def it_returns_payment_history(
                client: request_client.RequestClient, from_address: str, to_address: str
            ) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_payments_no_from_address.yml"
                ):
                    payments = await client.get_payments(
                        None,
                        to_address,
                    )
                    assert len(payments) > 0
                    assert payments[-1]["to"] == to_address
                    assert payments[-1]["from"].startswith("0x")

        def when_both_addresses_are_present() -> None:
            async def it_returns_payment_history(
                client: request_client.RequestClient, from_address: str, to_address: str
            ) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_payments.yml"
                ):
                    payments = await client.get_payments(
                        from_address,
                        to_address,
                    )
                    assert len(payments) > 0
                    assert payments[-1]["to"] == to_address
                    assert payments[-1]["from"] == from_address
