import decimal

import pytest

from huma_signals.adapters.bulla_network import adapter


def describe_adapter() -> None:
    def it_validate_bn_subgraph_endpoint_url() -> None:
        with pytest.raises(ValueError):
            adapter.BullaNetworkInvoiceAdapter(bulla_network_subgraph_endpoint_url="")

    def describe_get_claim_payments() -> None:
        @pytest.fixture
        def bn_subgraph_endpoint_url() -> str:
            return "https://api.thegraph.com/subgraphs/name/bulla-network/bulla-contracts-goerli"

        @pytest.fixture
        def from_address() -> str:
            return "0xcd003c72BF78F9C56C8eDB9DC4d450be8292d339".lower()

        @pytest.fixture
        def to_address() -> str:
            return (
                "0xf734908501a0B8d8d57C291ea1849490ccEdc16D".lower()
            )  # gitleaks:allow

        async def it_returns_claim_payment_history(
            bn_subgraph_endpoint_url: str, from_address: str, to_address: str
        ) -> None:
            claim_payments = (
                await adapter.BullaNetworkInvoiceAdapter._get_claim_payments(
                    to_address, None, bn_subgraph_endpoint_url
                )
            )
            assert len(claim_payments) > 0
            assert claim_payments[-1]["claim"]["creditor"]["id"] == to_address
            assert claim_payments[-1]["debtor"].startswith("0x")

            claim_payments = (
                await adapter.BullaNetworkInvoiceAdapter._get_claim_payments(
                    None, from_address, bn_subgraph_endpoint_url
                )
            )
            assert len(claim_payments) > 0
            assert claim_payments[-1]["debtor"] == from_address
            assert claim_payments[-1]["claim"]["creditor"]["id"].startswith("0x")

            claim_payments = (
                await adapter.BullaNetworkInvoiceAdapter._get_claim_payments(
                    to_address, from_address, bn_subgraph_endpoint_url
                )
            )
            assert len(claim_payments) > 0
            assert claim_payments[-1]["claim"]["creditor"]["id"] == to_address
            assert claim_payments[-1]["debtor"] == from_address

    def describe_fetch() -> None:
        @pytest.fixture
        def bn_subgraph_endpoint_url() -> str:
            return "https://api.thegraph.com/subgraphs/name/bulla-network/bulla-contracts-goerli"

        @pytest.fixture
        def borrower_address() -> str:
            return "0xf734908501a0B8d8d57C291ea1849490ccEdc16D".lower()

        @pytest.fixture
        def claim_id() -> int:
            return 234

        @pytest.fixture
        def payer_wallet_address() -> str:
            return "0xcd003c72BF78F9C56C8eDB9DC4d450be8292d339".lower()

        @pytest.fixture
        def payee_wallet_address() -> str:
            return "0xf734908501a0B8d8d57C291ea1849490ccEdc16D".lower()

        async def it_can_fetch_signals(
            bn_subgraph_endpoint_url: str,
            borrower_address: str,
            claim_id: int,
        ) -> None:
            signals = await adapter.BullaNetworkInvoiceAdapter(
                bulla_network_subgraph_url=bn_subgraph_endpoint_url,
            ).fetch(
                borrower_wallet_address=borrower_address,
                claim_id=claim_id,
            )

            assert signals.payee_match_borrower is True
            assert signals.invoice_amount == decimal.Decimal("1_000_000")
            assert signals.borrower_own_invoice is True
            assert signals.payer_on_allowlist is True
