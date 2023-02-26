from __future__ import annotations

import datetime
import decimal

import httpx
import pydantic
import structlog
import web3

from huma_signals import models

logger = structlog.get_logger()


class RequestNetworkInvoiceSignals(models.HumaBaseModel):
    # transactions based features: Payer Quality
    payer_tenure: int = pydantic.Field(
        ..., description="The number of days since the payer's first transaction"
    )
    payer_recent: int = pydantic.Field(
        ..., description="The number of days since the payer's most recent transaction"
    )
    payer_count: int = pydantic.Field(
        ..., description="The number of transactions the payer has made"
    )
    payer_total_amount: int = pydantic.Field(
        ..., description="The total amount the payer has paid"
    )
    payer_unique_payees: int = pydantic.Field(
        ..., description="The number of unique payees the payer has paid"
    )

    # transactions based features: Payee Quality
    payee_tenure: int = pydantic.Field(
        ..., description="The number of days since the payee's first transaction"
    )
    payee_recent: int = pydantic.Field(
        ..., description="The number of days since the payee's most recent transaction"
    )
    payee_count: int = pydantic.Field(
        ..., description="The number of transactions the payee has made"
    )
    payee_total_amount: int = pydantic.Field(
        ..., description="The total amount the payee has received"
    )
    payee_unique_payers: int = pydantic.Field(
        ..., description="The number of unique payers the payee has received"
    )

    # transactions based features: Pair Quality
    mutual_count: int = pydantic.Field(
        ..., description="The number of transactions between the payer and payee"
    )
    mutual_total_amount: int = pydantic.Field(
        ..., description="The total amount the payer and payee have transacted"
    )

    # invoice based features
    payee_match_borrower: bool = pydantic.Field(
        ..., description="Whether the borrower is the invoice's payee"
    )
    payer_match_payee: bool = pydantic.Field(
        ..., description="Whether the payee is the invoice's payer"
    )
    borrower_own_invoice: bool = pydantic.Field(
        ..., description="Whether the borrower own the invoice NFT token"
    )
    days_until_due_date: int = pydantic.Field(
        ..., description="The number of days until the invoice's due date"
    )
    invoice_amount: decimal.Decimal = pydantic.Field(
        ..., description="The amount of the invoice"
    )

    # allowlist feature
    payer_on_allowlist: bool = pydantic.Field(
        ..., description="Whether the payer is on the allowlist"
    )


class Invoice(models.HumaBaseModel):
    token_owner: str = pydantic.Field(..., description="The address of the token owner")
    currency: str = pydantic.Field(
        ..., description="The currency of the invoice (e.g. USDC, ETH, etc.)"
    )
    amount: decimal.Decimal = pydantic.Field(
        ..., description="The amount of the invoice (e.g. 100)"
    )
    status: str = pydantic.Field(
        ..., description="The status of the invoice (e.g. PAID, UNPAID, etc."
    )
    payer: str = pydantic.Field(..., description="The payer's address")
    payee: str = pydantic.Field(..., description="The payee's address")
    creation_date: datetime.datetime = pydantic.Field(
        ..., description="The date the invoice was created"
    )
    due_date: datetime.datetime = pydantic.Field(
        ..., description="The date the invoice is due"
    )

    # TODO: Support the balance field, 0 means it's not paid
    @classmethod
    async def from_request_id(
        cls, receivable_param: str, invoice_api_url: str
    ) -> Invoice:
        try:
            async with httpx.AsyncClient(base_url=invoice_api_url) as client:
                resp = await client.get(f"?id={receivable_param}")
                resp.raise_for_status()
                invoice_info = resp.json()
                if not web3.Web3.is_address(invoice_info["owner"]):
                    raise ValueError(
                        f"Invoice's owner is not a valid address: {invoice_info['owner']}"
                    )
                if not web3.Web3.is_address(invoice_info["payer"]):
                    raise ValueError(
                        f"Invoice's payer is not a valid address: {invoice_info['payer']}"
                    )
                if not web3.Web3.is_address(invoice_info["payee"]):
                    raise ValueError(
                        f"Invoice's payee is not a valid address: {invoice_info['payee']}"
                    )

                return cls(
                    token_owner=invoice_info["owner"].lower(),
                    currency=invoice_info.get("currencyInfo").get("symbol"),
                    amount=decimal.Decimal(invoice_info["expectedAmount"]),
                    status="",
                    payer=invoice_info["payer"].lower(),
                    payee=invoice_info["payee"].lower(),
                    creation_date=datetime.datetime.fromtimestamp(
                        invoice_info["creationDate"]
                    ),
                    # TODO: Figure out way to get real due date
                    due_date=datetime.datetime.fromtimestamp(
                        invoice_info["creationDate"]
                    )
                    + datetime.timedelta(days=30),
                )
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Request Network API returned status code {e.response.status_code}",
                exc_info=True,
                base_url=invoice_api_url,
                receivable_param=receivable_param,
            )

            raise Exception(
                f"Request Network API returned status code {e.response.status_code}",
            ) from e
