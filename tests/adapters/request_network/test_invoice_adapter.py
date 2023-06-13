import pytest

from huma_signals import exceptions
from huma_signals.adapters.ethereum_wallet import adapter as ethereum_wallet_adapter
from huma_signals.adapters.polygon_wallet import adapter as polygon_wallet_adapter
from huma_signals.adapters.request_network import request_invoice_adapter
from huma_signals.clients.request_client import request_client, request_types
from huma_signals.commons import chains
from tests.fixtures.adapters import (
    fake_ethereum_wallet_adapter,
    fake_polygon_wallet_adapter,
)
from tests.fixtures.clients.request import fake_request_client, request_type_factories
from tests.helpers import address_helpers


def describe_RequestInvoiceAdapter() -> None:
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
    def request_id() -> str:
        return address_helpers.fake_hex_address()

    @pytest.fixture
    def invoice(
        payer_wallet_address: str, payee_wallet_address: str
    ) -> request_types.Invoice:
        return request_type_factories.InvoiceFactory.create(
            payer=payer_wallet_address,
            payee=payee_wallet_address,
            token_owner=payee_wallet_address,
        )

    @pytest.fixture
    def request_client_(
        invoice: request_types.Invoice,
    ) -> fake_request_client.FakeRequestClient:
        return fake_request_client.FakeRequestClient(invoice=invoice)

    @pytest.fixture
    def adapter(
        request_client_: request_client.BaseRequestClient,
        wallet_adapter: ethereum_wallet_adapter.BaseEthereumWalletAdapter
        | polygon_wallet_adapter.BasePolygonWalletAdapter,
        chain: chains.Chain,
    ) -> request_invoice_adapter.RequestInvoiceAdapter:
        return request_invoice_adapter.RequestInvoiceAdapter(
            request_client_=request_client_,
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
                adapter: request_invoice_adapter.RequestInvoiceAdapter,
                payee_wallet_address: str,
                payer_wallet_tenure: int,
                payee_wallet_tenure: int,
                request_id: str,
                invoice: request_types.Invoice,
            ) -> None:
                signals = await adapter.fetch(
                    borrower_wallet_address=payee_wallet_address,
                    receivable_param=request_id,
                )
                assert signals.payer_count == 10
                assert signals.payee_count == 10
                assert signals.mutual_count == 0
                assert signals.payer_tenure == payer_wallet_tenure
                assert signals.payee_tenure == payee_wallet_tenure
                assert signals.payee_match_borrower
                assert signals.borrower_own_invoice
                assert signals.payer_match_payee is False
                assert signals.invoice_amount == invoice.amount
                assert signals.token_id == invoice.token_id

            def when_payee_is_not_the_borrower() -> None:
                async def it_returns_false_for_the_signal_field(
                    adapter: request_invoice_adapter.RequestInvoiceAdapter,
                    request_id: str,
                ) -> None:
                    signals = await adapter.fetch(
                        borrower_wallet_address=address_helpers.fake_hex_address(),
                        receivable_param=request_id,
                    )
                    assert signals.payee_match_borrower is False

            def when_the_borrower_does_not_own_the_invoice() -> None:
                @pytest.fixture
                def invoice() -> request_types.Invoice:
                    return request_type_factories.InvoiceFactory.create()

                async def it_returns_false_for_the_signal_field(
                    adapter: request_invoice_adapter.RequestInvoiceAdapter,
                    payee_wallet_address: str,
                    request_id: str,
                ) -> None:
                    signals = await adapter.fetch(
                        borrower_wallet_address=payee_wallet_address,
                        receivable_param=request_id,
                    )
                    assert signals.borrower_own_invoice is False

            def when_payer_and_payee_have_the_same_address() -> None:
                @pytest.fixture
                def payee_wallet_address(payer_wallet_address: str) -> str:
                    return payer_wallet_address

                async def it_returns_true_for_the_signal_field(
                    adapter: request_invoice_adapter.RequestInvoiceAdapter,
                    payee_wallet_address: str,
                    request_id: str,
                ) -> None:
                    signals = await adapter.fetch(
                        borrower_wallet_address=payee_wallet_address,
                        receivable_param=request_id,
                    )
                    assert signals.payer_match_payee

            def with_invalid_borrower_address() -> None:
                @pytest.fixture
                def payee_wallet_address() -> str:
                    return "0xabc"

                async def it_throws_error(
                    adapter: request_invoice_adapter.RequestInvoiceAdapter,
                    payee_wallet_address: str,
                    request_id: str,
                ) -> None:
                    with pytest.raises(exceptions.InvalidAddressException):
                        await adapter.fetch(
                            borrower_wallet_address=payee_wallet_address,
                            receivable_param=request_id,
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
                adapter: request_invoice_adapter.RequestInvoiceAdapter,
                payee_wallet_address: str,
                payer_wallet_tenure: int,
                payee_wallet_tenure: int,
                request_id: str,
            ) -> None:
                signals = await adapter.fetch(
                    borrower_wallet_address=payee_wallet_address,
                    receivable_param=request_id,
                )
                assert signals.payer_count == 10
                assert signals.payee_count == 10
                assert signals.mutual_count == 0
                assert signals.payer_tenure == payer_wallet_tenure
                assert signals.payee_tenure == payee_wallet_tenure

            def with_invalid_borrower_address() -> None:
                @pytest.fixture
                def payee_wallet_address() -> str:
                    return "0xabc"

                async def it_throws_error(
                    adapter: request_invoice_adapter.RequestInvoiceAdapter,
                    payee_wallet_address: str,
                    request_id: str,
                ) -> None:
                    with pytest.raises(exceptions.InvalidAddressException):
                        await adapter.fetch(
                            borrower_wallet_address=payee_wallet_address,
                            receivable_param=request_id,
                        )
