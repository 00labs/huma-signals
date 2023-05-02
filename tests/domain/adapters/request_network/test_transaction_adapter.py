import pytest

from huma_signals import exceptions
from huma_signals.commons import chains
from huma_signals.domain.adapters.ethereum_wallet import (
    adapter as ethereum_wallet_adapter,
)
from huma_signals.domain.adapters.polygon_wallet import (
    adapter as polygon_wallet_adapter,
)
from huma_signals.domain.adapters.request_network import request_transaction_adapter
from huma_signals.domain.clients.request_client import request_client
from huma_signals.settings import settings
from tests.fixtures.adapters import (
    fake_ethereum_wallet_adapter,
    fake_polygon_wallet_adapter,
)
from tests.fixtures.clients.request import fake_request_client
from tests.helpers import address_helpers


def describe_RequestTransactionAdapter() -> None:
    @pytest.fixture
    def payer_wallet_address() -> str:
        return address_helpers.fake_hex_address()

    @pytest.fixture
    def payee_wallet_address() -> str:
        return address_helpers.fake_hex_address()

    @pytest.fixture
    def payee_wallet_tenure() -> int:
        return 42

    @pytest.fixture
    def payer_wallet_tenure() -> int:
        return 24

    @pytest.fixture
    def request_client_() -> fake_request_client.FakeRequestClient:
        return fake_request_client.FakeRequestClient()

    @pytest.fixture
    def adapter(
        request_client_: request_client.BaseRequestClient,
        wallet_adapter: ethereum_wallet_adapter.BaseEthereumWalletAdapter
        | polygon_wallet_adapter.BasePolygonWalletAdapter,
        chain: chains.Chain,
    ) -> request_transaction_adapter.RequestTransactionAdapter:
        return request_transaction_adapter.RequestTransactionAdapter(
            request_client_=request_client_,
            request_network_subgraph_endpoint_url=settings.request_network_subgraph_endpoint_url,
            wallet_adapter=wallet_adapter,
            chain=chain,
        )

    def describe_fetch() -> None:
        def with_eth_chain() -> None:
            @pytest.fixture
            def chain() -> chains.Chain:
                return chains.Chain.ETHEREUM

            @pytest.fixture
            def signals(
                payee_wallet_address: str,
                payer_wallet_address: str,
                payee_wallet_tenure: int,
                payer_wallet_tenure: int,
            ) -> dict[str, ethereum_wallet_adapter.EthereumWalletSignals]:
                return {
                    payee_wallet_address: fake_ethereum_wallet_adapter.EthereumWalletSignalsFactory.create(
                        wallet_tenure_in_days=payee_wallet_tenure
                    ),
                    payer_wallet_address: fake_ethereum_wallet_adapter.EthereumWalletSignalsFactory.create(
                        wallet_tenure_in_days=payer_wallet_tenure
                    ),
                }

            @pytest.fixture
            def wallet_adapter(
                signals: dict[str, ethereum_wallet_adapter.EthereumWalletSignals]
            ) -> ethereum_wallet_adapter.BaseEthereumWalletAdapter:
                return fake_ethereum_wallet_adapter.FakeEthereumWalletAdapter(
                    output_signals=signals
                )

            async def it_fetches_the_signals(
                adapter: request_transaction_adapter.RequestTransactionAdapter,
                payer_wallet_address: str,
                payee_wallet_address: str,
                payer_wallet_tenure: int,
                payee_wallet_tenure: int,
            ) -> None:
                signals = await adapter.fetch(
                    payer_address=payer_wallet_address,
                    payee_address=payee_wallet_address,
                )
                assert signals.payer_count == 10
                assert signals.payee_count == 10
                assert signals.mutual_count == 0
                assert signals.payer_tenure == payer_wallet_tenure
                assert signals.payee_tenure == payee_wallet_tenure

            def with_invalid_payer_addresses() -> None:
                @pytest.fixture
                def payer_wallet_address() -> str:
                    return "0xabc"

                async def it_throws_error(
                    adapter: request_transaction_adapter.RequestTransactionAdapter,
                    payee_wallet_address: str,
                    payer_wallet_address: str,
                ) -> None:
                    with pytest.raises(exceptions.InvalidAddressException):
                        await adapter.fetch(
                            payer_address=payer_wallet_address,
                            payee_address=payee_wallet_address,
                        )

            def with_invalid_payee_addresses() -> None:
                @pytest.fixture
                def payee_wallet_address() -> str:
                    return "0xabc"

                async def it_throws_error(
                    adapter: request_transaction_adapter.RequestTransactionAdapter,
                    payee_wallet_address: str,
                    payer_wallet_address: str,
                ) -> None:
                    with pytest.raises(exceptions.InvalidAddressException):
                        await adapter.fetch(
                            payer_address=payer_wallet_address,
                            payee_address=payee_wallet_address,
                        )

        def with_polygon_chain() -> None:
            @pytest.fixture
            def chain() -> chains.Chain:
                return chains.Chain.POLYGON

            @pytest.fixture
            def signals(
                payee_wallet_address: str,
                payer_wallet_address: str,
                payee_wallet_tenure: int,
                payer_wallet_tenure: int,
            ) -> dict[str, polygon_wallet_adapter.PolygonWalletSignals]:
                return {
                    payee_wallet_address: fake_polygon_wallet_adapter.PolygonWalletSignalsFactory.create(
                        wallet_tenure_in_days=payee_wallet_tenure
                    ),
                    payer_wallet_address: fake_polygon_wallet_adapter.PolygonWalletSignalsFactory.create(
                        wallet_tenure_in_days=payer_wallet_tenure
                    ),
                }

            @pytest.fixture
            def wallet_adapter(
                signals: dict[str, polygon_wallet_adapter.PolygonWalletSignals]
            ) -> polygon_wallet_adapter.BasePolygonWalletAdapter:
                return fake_polygon_wallet_adapter.FakePolygonWalletAdapter(
                    output_signals=signals
                )

            async def it_fetches_the_signals(
                adapter: request_transaction_adapter.RequestTransactionAdapter,
                payer_wallet_address: str,
                payee_wallet_address: str,
                payer_wallet_tenure: int,
                payee_wallet_tenure: int,
            ) -> None:
                signals = await adapter.fetch(
                    payer_address=payer_wallet_address,
                    payee_address=payee_wallet_address,
                )
                assert signals.payer_count == 10
                assert signals.payee_count == 10
                assert signals.mutual_count == 0
                assert signals.payer_tenure == payer_wallet_tenure
                assert signals.payee_tenure == payee_wallet_tenure

            def with_invalid_payer_addresses() -> None:
                @pytest.fixture
                def payer_wallet_address() -> str:
                    return "0xabc"

                async def it_throws_error(
                    adapter: request_transaction_adapter.RequestTransactionAdapter,
                    payee_wallet_address: str,
                    payer_wallet_address: str,
                ) -> None:
                    with pytest.raises(exceptions.InvalidAddressException):
                        await adapter.fetch(
                            payer_address=payer_wallet_address,
                            payee_address=payee_wallet_address,
                        )

            def with_invalid_payee_addresses() -> None:
                @pytest.fixture
                def payee_wallet_address() -> str:
                    return "0xabc"

                async def it_throws_error(
                    adapter: request_transaction_adapter.RequestTransactionAdapter,
                    payee_wallet_address: str,
                    payer_wallet_address: str,
                ) -> None:
                    with pytest.raises(exceptions.InvalidAddressException):
                        await adapter.fetch(
                            payer_address=payer_wallet_address,
                            payee_address=payee_wallet_address,
                        )
