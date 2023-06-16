import datetime
import decimal
from typing import Any, Protocol

import httpx
import pandas as pd
import structlog
import web3
from huma_utils import chain_utils

from huma_signals import exceptions
from huma_signals.clients.request_client import request_types
from huma_signals.commons import tokens

logger = structlog.get_logger(__name__)

_DEFAULT_GRAPHQL_CHUNK_SIZE = 1000


class BaseRequestClient(Protocol):
    async def get_payments(
        self,
        from_address: str | None,
        to_address: str | None,
    ) -> list[dict[str, Any]]:
        pass

    async def get_invoice(self, request_id: str) -> request_types.Invoice:
        pass

    @classmethod
    def enrich_payments_data(
        cls, payments_raw_df: pd.DataFrame, chain: chain_utils.Chain
    ) -> pd.DataFrame:
        """
        Enriches the raw payments data with additional information
        """
        if len(payments_raw_df) == 0:
            return pd.DataFrame(
                columns=[
                    "id",
                    "contractAddress",
                    "tokenAddress",
                    "to",
                    "from",
                    "timestamp",
                    "txHash",
                    "amount",
                    "currency",
                    "amountInCrypto",
                    "txn_time",
                    "token_symbol",
                    "token_usd_price",
                    "amount_usd",
                ]
            )
        df = payments_raw_df.copy().drop_duplicates("id")
        df["txn_time"] = pd.to_datetime(df.timestamp, unit="s")
        df["token_symbol"] = df.tokenAddress.map(
            tokens.TOKEN_ADDRESS_MAPPING.get(chain)
        ).fillna("Other")
        df["amount"] = df.amount.astype(float)
        df["token_usd_price"] = df.token_symbol.map(
            tokens.TOKEN_USD_PRICE_MAPPING
        ).fillna(0)
        df["amount_usd"] = (df.amount * df.token_usd_price).astype(int)
        return df

    @classmethod
    def get_payment_stats(
        cls, enriched_df: pd.DataFrame
    ) -> dict[str, int | decimal.Decimal]:
        """
        Calculate some basic stats from the enriched payments data
        """
        if len(enriched_df) == 0:
            return {
                "total_amount": 0,
                "total_txns": 0,
                "earliest_txn_age_in_days": 0,
                "last_txn_age_in_days": 999,
                "unique_payees": 0,
                "unique_payers": 0,
            }
        return {
            "total_amount": enriched_df.amount_usd.sum(),
            "total_txns": len(enriched_df),
            "earliest_txn_age_in_days": (
                datetime.datetime.now() - enriched_df.txn_time.min()
            ).days,
            "last_txn_age_in_days": (
                datetime.datetime.now() - enriched_df.txn_time.max()
            ).days,
            "unique_payees": enriched_df["to"].nunique(),
            "unique_payers": enriched_df["from"].nunique(),
        }


class RequestClient(BaseRequestClient):
    """
    Translation layer for interacting with the Request Network/Request Finance API.
    """

    def __init__(
        self,
        request_network_subgraph_endpoint_url: str,
        invoice_api_url: str,
    ) -> None:
        self.request_network_subgraph_endpoint_url = (
            request_network_subgraph_endpoint_url
        )
        self.invoice_api_url = invoice_api_url

    async def get_payments(
        self,
        from_address: str | None,
        to_address: str | None,
    ) -> list[dict[str, Any]]:
        where_clause = ""
        if from_address:
            where_clause += f'from: "{from_address}",\n'
        if to_address:
            where_clause += f'to: "{to_address}",\n'

        payments = []
        last_chunk_size = _DEFAULT_GRAPHQL_CHUNK_SIZE
        last_id = ""
        try:
            async with httpx.AsyncClient() as client:
                while last_chunk_size == _DEFAULT_GRAPHQL_CHUNK_SIZE:
                    query = f"""
                        query HumaRequestNetworkPayments {{
                            payments(
                                first: {_DEFAULT_GRAPHQL_CHUNK_SIZE},
                                where: {{
                                    {where_clause}
                                    id_gt: "{last_id}"
                                }}
                                orderBy: id,
                                orderDirection: asc
                            ) {{
                                id
                                contractAddress
                                tokenAddress
                                to
                                from
                                timestamp
                                txHash
                                amount
                                currency
                                amountInCrypto
                            }}
                        }}
                        """
                    resp = await client.post(
                        self.request_network_subgraph_endpoint_url,
                        json={"query": query},
                    )
                    new_chunk = resp.json()["data"]["payments"]
                    payments.extend(new_chunk)
                    last_chunk_size = len(new_chunk)
                    if len(payments) > 0:
                        last_id = payments[-1]["id"]
        except KeyError as e:
            message = "No data returned from query"
            logger.exception(message, resp_body=resp.json())
            raise exceptions.RequestException(message=message) from e
        except Exception as e:
            message = f"Error fetching payments: {e}"
            logger.exception(message)
            raise exceptions.RequestException(message=message) from e

        return payments

    async def get_invoice(self, request_id: str) -> request_types.Invoice:
        try:
            async with httpx.AsyncClient(base_url=self.invoice_api_url) as client:
                resp = await client.get(f"?id={request_id}")
                resp.raise_for_status()
                invoice_info = resp.json()
                if not web3.Web3.is_address(invoice_info["owner"]):
                    raise exceptions.InvalidAddressException(
                        f"Invoice's owner is not a valid address: {invoice_info['owner']}"
                    )
                if not web3.Web3.is_address(invoice_info["payer"]):
                    raise exceptions.InvalidAddressException(
                        f"Invoice's payer is not a valid address: {invoice_info['payer']}"
                    )
                if not web3.Web3.is_address(invoice_info["payee"]):
                    raise exceptions.InvalidAddressException(
                        f"Invoice's payee is not a valid address: {invoice_info['payee']}"
                    )

                return request_types.Invoice(
                    token_owner=invoice_info["owner"].lower(),
                    currency=invoice_info.get("currencyInfo").get("symbol"),
                    amount=decimal.Decimal(invoice_info["expectedAmount"]),
                    status="",
                    payer=invoice_info["payer"].lower(),
                    payee=invoice_info["payee"].lower(),
                    # TODO(jiatu): do we need to add tz info here?
                    creation_date=datetime.datetime.fromtimestamp(
                        invoice_info["creationDate"]
                    ),
                    # TODO: Figure out way to get real due date
                    due_date=datetime.datetime.fromtimestamp(
                        invoice_info["creationDate"]
                    )
                    + datetime.timedelta(days=30),
                    token_id=invoice_info["tokenId"],
                )
        except httpx.HTTPStatusError as e:
            logger.exception(
                f"Request Network API returned status code {e.response.status_code}",
                base_url=self.invoice_api_url,
                receivable_param=request_id,
            )
            raise exceptions.RequestException(
                f"Request Network API returned status code {e.response.status_code}",
            ) from e
