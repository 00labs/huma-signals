import pytest

from huma_signals.adapters.request_network import request_transaction_adapter
from huma_signals.domain.clients.request_client import request_client
from huma_signals.settings import settings
from tests.fixtures.request import fake_request_client
from tests.helpers import address_helpers


def describe_RequestTransactionAdapter() -> None:
    @pytest.fixture
    def payer_wallet_address() -> str:
        return address_helpers.fake_hex_address()

    @pytest.fixture
    def payee_wallet_address() -> str:
        return address_helpers.fake_hex_address()

    @pytest.fixture
    def request_client_() -> fake_request_client.FakeRequestClient:
        return fake_request_client.FakeRequestClient()

    @pytest.fixture
    def adapter(
        request_client_: request_client.BaseRequestClient,
    ) -> request_transaction_adapter.RequestTransactionAdapter:
        return request_transaction_adapter.RequestTransactionAdapter(
            request_client_=request_client_,
            request_network_subgraph_endpoint_url=settings.request_network_subgraph_endpoint_url,
            chain=settings.chain,
        )

    def describe_fetch() -> None:
        async def it_fetches_the_signals(
            adapter: request_transaction_adapter.RequestTransactionAdapter,
            payer_wallet_address: str,
            payee_wallet_address: str,
        ) -> None:
            signals = await adapter.fetch(
                payer_address=payer_wallet_address,
                payee_address=payee_wallet_address,
            )
            assert signals.payer_count == 10
            assert signals.payee_count == 10
            assert signals.mutual_count == 0
