import datetime
import decimal
from unittest import mock

import pytest

from huma_signals.adapters.request_network import adapter, models
from huma_signals.commons import chains


def describe_adapter() -> None:
    def it_validate_rn_invoice_api_url() -> None:
        with pytest.raises(ValueError):
            adapter.RequestNetworkInvoiceAdapter(request_network_invoice_api_url="")

    def it_validate_rn_subgraph_endpoint_url() -> None:
        with pytest.raises(ValueError):
            adapter.RequestNetworkInvoiceAdapter(
                request_network_subgraph_endpoint_url=""
            )

    def describe_get_payments() -> None:
        @pytest.fixture
        def rn_subgraph_endpoint_url() -> str:
            return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-mainnet"

        @pytest.fixture
        def from_address() -> str:
            return "0x8d2aa089af73e788cf7afa1f94bf4cf2cde0db61".lower()

        @pytest.fixture
        def to_address() -> str:
            return (
                "0x63d6287d5b853ccfedba1247fbeb9a40512f709a".lower()
            )  # gitleaks:allow

        @pytest.fixture
        def adapter_(
            rn_subgraph_endpoint_url: str,
        ) -> adapter.RequestNetworkInvoiceAdapter:
            return adapter.RequestNetworkInvoiceAdapter(
                request_network_subgraph_endpoint_url=rn_subgraph_endpoint_url,
            )

        async def it_returns_payment_history(
            from_address: str,
            to_address: str,
            adapter_: adapter.RequestNetworkInvoiceAdapter,
        ) -> None:
            payments = await adapter_._get_payments(from_address, None)
            assert len(payments) > 0
            assert payments[-1]["from"] == from_address
            assert payments[-1]["to"].startswith("0x")

            payments = await adapter_._get_payments(None, to_address)
            assert len(payments) > 0
            assert payments[-1]["to"] == to_address
            assert payments[-1]["from"].startswith("0x")

            payments = await adapter_._get_payments(from_address, to_address)
            assert len(payments) > 0
            assert payments[-1]["to"] == to_address
            assert payments[-1]["from"] == from_address

    def describe_fetch() -> None:
        @pytest.fixture
        def rn_subgraph_endpoint_url() -> str:
            return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-goerli"

        @pytest.fixture
        def rn_invoice_api_url() -> str:
            return "https://dev.goerli.rnreader.huma.finance/invoice"

        @pytest.fixture
        def borrower_address() -> str:
            return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0".lower()

        @pytest.fixture
        def receivable_param() -> str:
            return "0x0235"

        @pytest.fixture
        def payer_wallet_address() -> str:
            return "0x8b99407A4395714B706415277f17b4d549608AFe".lower()

        @pytest.fixture
        def payee_wallet_address() -> str:
            return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0".lower()

        @pytest.fixture
        def adapter_(
            rn_invoice_api_url: str, rn_subgraph_endpoint_url: str
        ) -> adapter.RequestNetworkInvoiceAdapter:
            return adapter.RequestNetworkInvoiceAdapter(
                request_network_invoice_api_url=rn_invoice_api_url,
                request_network_subgraph_endpoint_url=rn_subgraph_endpoint_url,
            )

        async def it_can_fetch_signals(
            borrower_address: str,
            receivable_param: str,
            adapter_: adapter.RequestNetworkInvoiceAdapter,
        ) -> None:
            signals = await adapter_.fetch(
                borrower_wallet_address=borrower_address,
                receivable_param=receivable_param,
            )
            assert signals.payer_tenure == 0
            assert signals.payer_recent == 999
            assert signals.payer_count == 0
            assert signals.payer_total_amount == decimal.Decimal("0")
            assert signals.payee_tenure > 750
            assert signals.payee_recent == 999
            assert signals.payee_count == 0
            assert signals.payee_total_amount == decimal.Decimal("0")
            assert signals.mutual_count == 0
            assert signals.mutual_total_amount == decimal.Decimal("0")
            assert signals.payee_match_borrower is False
            assert signals.borrower_own_invoice is False
            assert signals.payer_on_allowlist is True

        @mock.patch(
            "huma_signals.adapters.request_network.models.Invoice.from_request_id",
            return_value=models.Invoice(
                token_owner="0x63d6287d5b853ccfedba1247fbeb9a40512f709a",  # gitleaks:allow
                payer="0x8d2aa089af73e788cf7afa1f94bf4cf2cde0db61",  # gitleaks:allow
                payee="0x63d6287d5b853ccfedba1247fbeb9a40512f709a",  # gitleaks:allow
                amount=decimal.Decimal("100"),
                currency="USDC",
                status="UNPAID",
                creation_date=datetime.datetime(2022, 12, 25),
                due_date=datetime.datetime(2023, 1, 25),
            ),
        )
        async def it_can_calculate_signals_with_mocked_invoice(
            borrower_address: str,
            receivable_param: str,
        ) -> None:
            """
            In this test we mocked the invoice with a very active pair from mainnet,
            so we can test the signals are calculated correctly.

            # TODO: Use a proper data tape instead of of rely on live data for this test
            """
            mainnet_subgraph = "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-mainnet"
            signals = await adapter.RequestNetworkInvoiceAdapter(
                chain=chains.Chain.ETHEREUM,
                request_network_subgraph_endpoint_url=mainnet_subgraph,
                request_network_invoice_api_url="https://dev.goerli.rnreader.huma.finance/invoice",
            ).fetch(
                borrower_wallet_address=borrower_address,
                receivable_param=receivable_param,
            )
            assert signals.payer_tenure > 600
            assert signals.payer_recent < 999
            assert signals.payer_count > 830
            assert signals.payer_total_amount > decimal.Decimal("100_000_000")
            assert signals.payee_tenure > 600
            assert signals.payee_recent < 999
            assert signals.payee_count > 30
            assert signals.payee_total_amount >= decimal.Decimal("6_000_000")
            assert signals.mutual_count > 35
            assert signals.mutual_total_amount >= decimal.Decimal("6_000_000")
            assert signals.payee_match_borrower is False
            assert signals.borrower_own_invoice is False
            assert signals.payer_on_allowlist is True
            assert signals.payer_match_payee is False
