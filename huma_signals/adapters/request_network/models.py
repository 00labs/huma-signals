from datetime import datetime, timedelta
from decimal import Decimal

import requests
from pydantic import Field
from web3 import Web3

from huma_signals.models import HumaBaseModel


class RequestNetworkInvoiceSignals(HumaBaseModel):
    # transactions based features: Payer Quality
    payer_tenure: int = Field(..., description="The number of days since the payer's first transaction")
    payer_recent: int = Field(..., description="The number of days since the payer's most recent transaction")
    payer_count: int = Field(..., description="The number of transactions the payer has made")
    payer_total_amount: Decimal = Field(..., description="The total amount the payer has paid")
    payer_unique_payees: int = Field(..., description="The number of unique payees the payer has paid")

    # transactions based features: Payee Quality
    payee_tenure: int = Field(..., description="The number of days since the payee's first transaction")
    payee_recent: int = Field(..., description="The number of days since the payee's most recent transaction")
    payee_count: int = Field(..., description="The number of transactions the payee has made")
    payee_total_amount: Decimal = Field(..., description="The total amount the payee has received")
    payee_unique_payers: int = Field(..., description="The number of unique payers the payee has received")

    # transactions based features: Pair Quality
    mutual_count: int = Field(..., description="The number of transactions between the payer and payee")
    mutual_total_amount: Decimal = Field(..., description="The total amount the payer and payee have transacted")

    # invoice based features
    payee_match_borrower: bool = Field(..., description="Whether the borrower is the invoice's payee")
    borrower_own_invoice: bool = Field(..., description="Whether the borrower own the invoice NFT token")
    days_until_due_date: int = Field(..., description="The number of days until the invoice's due date")
    invoice_amount: Decimal = Field(..., description="The amount of the invoice")

    # allowlist feature
    payer_on_allowlist: bool = Field(..., description="Whether the payer is on the allowlist")


class Invoice(HumaBaseModel):
    token_owner: str = Field(..., description="The address of the token owner")
    currency: str = Field(..., description="The currency of the invoice (e.g. USDC, ETH, etc.)")
    amount: Decimal = Field(..., description="The amount of the invoice (e.g. 100)")
    status: str = Field(..., description="The status of the invoice (e.g. PAID, UNPAID, etc.")
    payer: str = Field(..., description="The payer's address")
    payee: str = Field(..., description="The payee's address")
    creation_date: datetime = Field(..., description="The date the invoice was created")
    due_date: datetime = Field(..., description="The date the invoice is due")

    # TODO: Support the balance field, 0 means it's not paid
    @classmethod
    def from_request_id(cls, receivable_param: str, invoice_api_url: str):
        response = requests.get(f"{invoice_api_url}?id={receivable_param}")
        if response.status_code == 200:
            invoice_info = response.json()
            if not Web3.isAddress(invoice_info["owner"]):
                raise Exception(f"Invoice's owner is not a valid address: {invoice_info['owner']}")
            if not Web3.isAddress(invoice_info["payer"]):
                raise Exception(f"Invoice's payer is not a valid address: {invoice_info['payer']}")
            if not Web3.isAddress(invoice_info["payee"]):
                raise Exception(f"Invoice's payee is not a valid address: {invoice_info['payee']}")

            return cls(
                token_owner=invoice_info["owner"].lower(),
                currency=invoice_info.get("currencyInfo").get("symbol"),
                amount=Decimal(invoice_info["expectedAmount"]),
                status="",
                payer=invoice_info["payer"].lower(),
                payee=invoice_info["payee"].lower(),
                creation_date=datetime.fromtimestamp(invoice_info["creationDate"]),
                # TODO: Figure out way to get real due date
                due_date=datetime.fromtimestamp(invoice_info["creationDate"]) + timedelta(days=30),
            )
        else:
            raise Exception(f"Request Network subgraph returned status code {response.status_code}")
