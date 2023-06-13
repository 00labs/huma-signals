from __future__ import annotations

import decimal

import pydantic
import structlog

from huma_signals import models

logger = structlog.get_logger()


class RequestInvoiceSignals(models.HumaBaseModel):
    # transactions based features: Payer Quality
    payer_tenure: int = pydantic.Field(
        description="The number of days since the payer's first transaction"
    )
    payer_recent: int = pydantic.Field(
        description="The number of days since the payer's most recent transaction"
    )
    payer_count: int = pydantic.Field(
        description="The number of transactions the payer has made"
    )
    payer_total_amount: int = pydantic.Field(
        description="The total amount the payer has paid"
    )
    payer_unique_payees: int = pydantic.Field(
        description="The number of unique payees the payer has paid"
    )

    # transactions based features: Payee Quality
    payee_tenure: int = pydantic.Field(
        description="The number of days since the payee's first transaction"
    )
    payee_recent: int = pydantic.Field(
        description="The number of days since the payee's most recent transaction"
    )
    payee_count: int = pydantic.Field(
        description="The number of transactions the payee has made"
    )
    payee_total_amount: int = pydantic.Field(
        description="The total amount the payee has received"
    )
    payee_unique_payers: int = pydantic.Field(
        description="The number of unique payers the payee has received"
    )

    # transactions based features: Pair Quality
    mutual_count: int = pydantic.Field(
        description="The number of transactions between the payer and payee"
    )
    mutual_total_amount: int = pydantic.Field(
        description="The total amount the payer and payee have transacted"
    )

    # invoice based features
    payee_match_borrower: bool = pydantic.Field(
        description="Whether the borrower is the invoice's payee"
    )
    payer_match_payee: bool = pydantic.Field(
        description="Whether the payee is the invoice's payer"
    )
    borrower_own_invoice: bool = pydantic.Field(
        description="Whether the borrower own the invoice NFT token"
    )
    days_until_due_date: int = pydantic.Field(
        description="The number of days until the invoice's due date"
    )
    invoice_amount: decimal.Decimal = pydantic.Field(
        description="The amount of the invoice"
    )
    token_id: str = pydantic.Field(description="The ID of the invoice")


class RequestTransactionSignals(models.HumaBaseModel):
    # transactions based features: Payer Quality
    payer_tenure: int = pydantic.Field(
        description="The number of days since the payer's first transaction"
    )
    payer_recent: int = pydantic.Field(
        description="The number of days since the payer's most recent transaction"
    )
    payer_count: int = pydantic.Field(
        description="The number of transactions the payer has made"
    )
    payer_total_amount: int = pydantic.Field(
        description="The total amount the payer has paid"
    )
    payer_unique_payees: int = pydantic.Field(
        description="The number of unique payees the payer has paid"
    )

    # transactions based features: Payee Quality
    payee_tenure: int = pydantic.Field(
        description="The number of days since the payee's first transaction"
    )
    payee_recent: int = pydantic.Field(
        description="The number of days since the payee's most recent transaction"
    )
    payee_count: int = pydantic.Field(
        description="The number of transactions the payee has made"
    )
    payee_total_amount: int = pydantic.Field(
        description="The total amount the payee has received"
    )
    payee_unique_payers: int = pydantic.Field(
        description="The number of unique payers the payee has received"
    )

    # transactions based features: Pair Quality
    mutual_count: int = pydantic.Field(
        description="The number of transactions between the payer and payee"
    )
    mutual_total_amount: int = pydantic.Field(
        description="The total amount the payer and payee have transacted"
    )
