import datetime
import decimal
from unittest import mock

import pytest

from huma_signals.adapters.request_network import adapter, models


def describe_adapter() -> None:
    def describe_get_payments() -> None:
        @pytest.fixture(scope="session", autouse=True)
        def rn_subgraph_endpoint_url() -> str:
            return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-mainnet"

        @pytest.fixture(scope="session", autouse=True)
        def from_address() -> str:
            return "0x8d2aa089af73e788cf7afa1f94bf4cf2cde0db61".lower()

        @pytest.fixture(scope="session", autouse=True)
        def to_address() -> str:
            return (
                "0x63d6287d5b853ccfedba1247fbeb9a40512f709a".lower()
            )  # gitleaks:allow

        def it_returns_payer_payment_history(
            rn_subgraph_endpoint_url: str, from_address: str
        ) -> None:
            payments = adapter.RequestNetworkInvoiceAdapter._get_payments(
                from_address, None, rn_subgraph_endpoint_url
            )
            assert len(payments) > 0
            assert payments[-1]["from"] == from_address
            assert payments[-1]["to"].startswith("0x")

        def it_returns_payee_payment_history(
            rn_subgraph_endpoint_url: str, to_address: str
        ) -> None:
            payments = adapter.RequestNetworkInvoiceAdapter._get_payments(
                None, to_address, rn_subgraph_endpoint_url
            )
            assert len(payments) > 0
            assert payments[-1]["to"] == to_address
            assert payments[-1]["from"].startswith("0x")

        def it_returns_pair_payment_history(
            rn_subgraph_endpoint_url: str, from_address: str, to_address: str
        ) -> None:
            payments = adapter.RequestNetworkInvoiceAdapter._get_payments(
                from_address, to_address, rn_subgraph_endpoint_url
            )
            assert len(payments) > 0
            assert payments[-1]["to"] == to_address
            assert payments[-1]["from"] == from_address

    def describe_fetch() -> None:
        @pytest.fixture(scope="session", autouse=True)
        def rn_subgraph_endpoint_url() -> str:
            return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-goerli"

        @pytest.fixture(scope="session", autouse=True)
        def rn_invoice_api_url() -> str:
            return "https://goerli.api.huma.finance/invoice"

        @pytest.fixture(scope="session", autouse=True)
        def borrower_address() -> str:
            return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0".lower()

        @pytest.fixture(scope="session", autouse=True)
        def receivable_param() -> str:
            return "0xdf135697d5b8b0ead72f8a80131c25c6fdb140bdc17d75652675fe801d9a5ff0"

        @pytest.fixture(scope="session", autouse=True)
        def payer_wallet_address() -> str:
            return "0x8b99407A4395714B706415277f17b4d549608AFe".lower()

        @pytest.fixture(scope="session", autouse=True)
        def payee_wallet_address() -> str:
            return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0".lower()

        def it_can_fetch_signals(
            rn_subgraph_endpoint_url: str,
            rn_invoice_api_url: str,
            borrower_address: str,
            receivable_param: str,
        ) -> None:
            signals = adapter.RequestNetworkInvoiceAdapter.fetch(
                chain_name="goerli",
                borrower_wallet_address=borrower_address,
                receivable_param=receivable_param,
                rn_subgraph_endpoint_url=rn_subgraph_endpoint_url,
                rn_invoice_endpoint_url=rn_invoice_api_url,
            )
            assert signals.payer_tenure == 0
            assert signals.payer_recent == 999
            assert signals.payer_count == 0
            assert signals.payer_total_amount == decimal.Decimal("0")
            assert signals.payee_tenure == 0
            assert signals.payee_recent == 999
            assert signals.payee_count == 0
            assert signals.payee_total_amount == decimal.Decimal("0")
            assert signals.mutual_count == 0
            assert signals.mutual_total_amount == decimal.Decimal("0")
            assert signals.payee_match_borrower is True
            assert signals.borrower_own_invoice is True
            assert signals.payer_on_allowlist is False

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
        def it_can_calculate_signals_with_mocked_invoice(
            mocked_invoice: str,
            borrower_address: str,
            receivable_param: str,
            rn_invoice_api_url: str,
        ) -> None:
            """
            In this test we mocked the invoice with a very active pair from mainnet,
            so we can test the signals are calculated correctly.
            """
            # TODO: Use a proper data tape instead of of rely on live data for this test
            signals = adapter.RequestNetworkInvoiceAdapter.fetch(
                chain_name="mainnet",
                borrower_wallet_address=borrower_address,
                receivable_param=receivable_param,
                rn_subgraph_endpoint_url=None,
                rn_invoice_endpoint_url=rn_invoice_api_url,
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
            assert signals.payer_on_allowlist is False
