import datetime
import decimal
from typing import Any, Protocol

import httpx
import pandas as pd
import structlog

from huma_signals import exceptions
from huma_signals.commons import chains, tokens
from huma_signals.settings import settings

logger = structlog.get_logger(__name__)

_DEFAULT_GRAPHQL_CHUNK_SIZE = 1000


class BaseRequestClient(Protocol):
    async def get_payments(
        self,
        from_address: str | None,
        to_address: str | None,
    ) -> list[dict[str, Any]]:
        pass

    @classmethod
    def enrich_payments_data(
        cls, payments_raw_df: pd.DataFrame, chain: chains.Chain
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
        rn_subgraph_endpoint_url: str = settings.request_network_subgraph_endpoint_url,
    ) -> None:
        self.rn_subgraph_endpoint_url = rn_subgraph_endpoint_url

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
                        self.rn_subgraph_endpoint_url,
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
