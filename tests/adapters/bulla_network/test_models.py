import datetime
import decimal

import pytest
import web3

from huma_signals.adapters.bulla_network import models


@pytest.fixture
def claim_id() -> int:
    return 234


@pytest.fixture
def payer_wallet_address() -> str:
    return "0xcd003c72BF78F9C56C8eDB9DC4d450be8292d339"


@pytest.fixture
def payee_wallet_address() -> str:
    return "0xf734908501a0B8d8d57C291ea1849490ccEdc16D"


@pytest.fixture
def subgraph_url() -> str:
    return (
        "https://api.thegraph.com/subgraphs/name/bulla-network/bulla-contracts-goerli"
    )


def describe_invoice() -> None:
    async def it_can_be_initialized_with_a_claim_id(
        claim_id: int,
        subgraph_url: str,
        payee_wallet_address: str,
        payer_wallet_address: str,
    ) -> None:
        invoice = await models.Invoice.from_claim_id(claim_id, subgraph_url)
        assert (
            web3.Web3.to_checksum_address(invoice.token_owner) == payee_wallet_address
        )
        assert web3.Web3.to_checksum_address(invoice.payer) == payer_wallet_address
        assert invoice.currency == "USDC"
        assert invoice.amount == decimal.Decimal("1_000_000")
        assert web3.Web3.to_checksum_address(invoice.payee) == payee_wallet_address
        assert invoice.creation_date > datetime.datetime(2023, 2, 28)
        assert invoice.due_date > datetime.datetime(2023, 3, 6)
