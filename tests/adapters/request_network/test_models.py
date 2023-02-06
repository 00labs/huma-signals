import datetime
import decimal

import pytest
import web3

from huma_signals.adapters.request_network import models


@pytest.fixture
def receivable_param() -> str:
    return "0xdf135697d5b8b0ead72f8a80131c25c6fdb140bdc17d75652675fe801d9a5ff0"


@pytest.fixture
def payer_wallet_address() -> str:
    return "0x8b99407A4395714B706415277f17b4d549608AFe"


@pytest.fixture
def payee_wallet_address() -> str:
    return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0"


@pytest.fixture
def rn_invoice_api_url() -> str:
    return "https://goerli.api.huma.finance/invoice"


def describe_invoice() -> None:
    async def it_can_be_initialized_with_a_receivable_param(
        receivable_param: str,
        rn_invoice_api_url: str,
        payee_wallet_address: str,
        payer_wallet_address: str,
    ) -> None:
        invoice = await models.Invoice.from_request_id(
            receivable_param, rn_invoice_api_url
        )
        assert (
            web3.Web3.to_checksum_address(invoice.token_owner) == payee_wallet_address
        )
        assert web3.Web3.to_checksum_address(invoice.payer) == payer_wallet_address
        assert invoice.currency == "USDC"
        assert invoice.amount == decimal.Decimal("100_000_000")
        assert web3.Web3.to_checksum_address(invoice.payee) == payee_wallet_address
        assert invoice.creation_date > datetime.datetime(2022, 12, 25)
        assert invoice.due_date > datetime.datetime(2023, 1, 25)
