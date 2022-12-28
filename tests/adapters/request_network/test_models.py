from datetime import datetime
from decimal import Decimal

import pytest
from web3 import Web3

from huma_signals.adapters.request_network.models import Invoice


@pytest.fixture(scope="session", autouse=True)
def receivable_param():
    return "0xdf135697d5b8b0ead72f8a80131c25c6fdb140bdc17d75652675fe801d9a5ff0"


@pytest.fixture(scope="session", autouse=True)
def payer_wallet_address():
    return "0x8b99407A4395714B706415277f17b4d549608AFe"


@pytest.fixture(scope="session", autouse=True)
def payee_wallet_address():
    return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0"


@pytest.fixture(scope="session", autouse=True)
def rn_invoice_api_url():
    return "https://goerli.api.huma.finance/invoice"


def describe_invoice():
    def it_can_be_initialized_with_a_receivable_param(
        receivable_param, rn_invoice_api_url, payee_wallet_address, payer_wallet_address
    ):
        invoice = Invoice.from_request_id(receivable_param, rn_invoice_api_url)
        assert Web3.toChecksumAddress(invoice.token_owner) == payee_wallet_address
        assert Web3.toChecksumAddress(invoice.payer) == payer_wallet_address
        assert invoice.currency == "USDC"
        assert invoice.amount == Decimal("100_000_000")
        assert Web3.toChecksumAddress(invoice.payee) == payee_wallet_address
        assert invoice.creation_date > datetime(2022, 12, 25)
        assert invoice.due_date > datetime(2023, 1, 25)
