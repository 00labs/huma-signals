from __future__ import annotations

import datetime
import decimal

import httpx
import pydantic
import structlog
import web3

from huma_signals import models

logger = structlog.get_logger()


class BullaNetworkInvoiceSignals(models.HumaBaseModel):
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
    invoice_status: str = pydantic.Field(
        ...,
        description="The status of the invoice (Paid, Pending, Repaying, Rejected, Rescinded)",
    )
    payer_has_accepted_invoice: bool = pydantic.Field(
        ..., description="Whether the payer has paid at least 1 wei of the invoice"
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
    async def from_claim_id(cls, claim_id: int, subgraph_url: str) -> Invoice:
        try:
            async with httpx.AsyncClient(base_url=subgraph_url) as client:
                query = f"""
                    query BullaNetworkClaimRequest {{
                        claims(
                            where: {{id: "{claim_id}"}}
                        ) {{
                            id
                            token {{ symbol }}
                            creditor {{ id }}
                            debtor {{ id }}
                            transactionHash
                            amount
                            created
                            dueBy
                            status
                        }}
                    }}
                    """
                resp = await client.post(
                    subgraph_url,
                    json={"query": query},
                )
                resp.raise_for_status()

                response_json = resp.json()
                claims = response_json["data"]["claims"]
                if len(claims) != 1:
                    raise ValueError(f"Claim not found with Id: {claim_id}")

                claim = claims[0]

                creditor = claim["creditor"]["id"].lower()
                debtor = claim["debtor"]["id"].lower()

                if not web3.Web3.is_address(creditor):
                    raise ValueError(
                        f"Invoice's creditor is not a valid address: {creditor}"
                    )
                if not web3.Web3.is_address(debtor):
                    raise ValueError(
                        f"Invoice's debtor is not a valid address: {debtor}"
                    )

                return cls(
                    token_owner=creditor,
                    currency=claim["token"]["symbol"],
                    amount=decimal.Decimal(claim["amount"]),
                    status=claim["status"],
                    payer=debtor,
                    payee=creditor,
                    creation_date=datetime.datetime.fromtimestamp(
                        int(claim["created"])
                    ),
                    due_date=datetime.datetime.fromtimestamp(int(claim["dueBy"])),
                )
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Bulla Network Subgragh API returned status code {e.response.status_code}",
                exc_info=True,
                base_url=subgraph_url,
                claim_id=claim_id,
            )

            raise Exception(
                f"Bulla Network Subgraph API returned status code {e.response.status_code}",
            ) from e
