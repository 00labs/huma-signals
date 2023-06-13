import datetime
import decimal

import pydantic

from huma_signals import models


class Invoice(models.HumaBaseModel):
    token_id: str = pydantic.Field(description="The ID of the invoice token")
    token_owner: str = pydantic.Field(description="The address of the token owner")
    currency: str = pydantic.Field(
        description="The currency of the invoice (e.g. USDC, ETH, etc.)"
    )
    amount: decimal.Decimal = pydantic.Field(
        description="The amount of the invoice (e.g. 100)"
    )
    status: str = pydantic.Field(
        description="The status of the invoice (e.g. PAID, UNPAID, etc.)"
    )
    payer: str = pydantic.Field(description="The payer's address")
    payee: str = pydantic.Field(description="The payee's address")
    creation_date: datetime.datetime = pydantic.Field(
        description="The date the invoice was created"
    )
    due_date: datetime.datetime = pydantic.Field(
        description="The date the invoice is due"
    )
