from datetime import datetime
from decimal import Decimal
from typing import ClassVar, Dict, List

import pandas as pd
import requests
from web3 import Web3

from huma_signals.adapters.models import SignalAdapterBase
from huma_signals.commons.chains import Chain
from huma_signals.commons.tokens import TOKEN_ADDRESS_MAPPING, TOKEN_USD_PRICE_MAPPING

from .models import Invoice, RequestNetworkInvoiceSignals
from .settings import get_rn_invoice_api_url, get_rn_subgraph_endpoint_url

_ALLOWED_PAYER_ADDRESSES = {"0x2177d6C4eC1a6511184CA6FfAb4FD1d1F5bFF39f".lower()}
DEFAULT_GRAPHQL_CHUNK_SIZE = 1000


class RequestNetworkInvoiceAdapter(SignalAdapterBase):
    name: ClassVar[str] = "request_network"
    required_inputs: ClassVar[List[str]] = [
        "chain_name",
        "borrower_wallet_address",
        "receivable_param",
    ]
    signals: ClassVar[List[str]] = list(RequestNetworkInvoiceSignals.__fields__.keys())

    def _get_payments(from_address: str, to_address: str, rn_subgraph_endpoint_url: str):
        where_clause = ""
        if from_address:
            where_clause += f'from: "{from_address}",\n'
        if to_address:
            where_clause += f'to: "{to_address}",\n'

        payments = []
        last_chunk_size = DEFAULT_GRAPHQL_CHUNK_SIZE
        last_id = ""
        while last_chunk_size == DEFAULT_GRAPHQL_CHUNK_SIZE:
            query = f"""
                query {{
                payments(first: {DEFAULT_GRAPHQL_CHUNK_SIZE},
                    where: {{
                        {where_clause}
                        id_gt: "{last_id}"
                    }}
                    orderBy: id, orderDirection: asc
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
            r = requests.post(rn_subgraph_endpoint_url, json={"query": query})
            new_chunk = r.json()["data"]["payments"]
            payments.extend(new_chunk)
            last_chunk_size = len(new_chunk)
            if len(payments) > 0:
                last_id = payments[-1]["id"]

        return payments

    def enrich_payments_data(payments_raw_df: pd.DataFrame, chain_name: str) -> pd.DataFrame:
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
                    "token_name",
                    "token_usd_price",
                    "amount_usd",
                ]
            )
        chain = Chain.from_chain_name(chain_name)
        df = payments_raw_df.copy().drop_duplicates("id")
        df["txn_time"] = pd.to_datetime(df.timestamp, unit="s")
        df["token_name"] = df.tokenAddress.map(TOKEN_ADDRESS_MAPPING.get(chain)).fillna("Other")
        df["amount"] = df.amount.astype(float)
        df["token_usd_price"] = df.token_name.map(TOKEN_USD_PRICE_MAPPING).fillna(0)
        df["amount_usd"] = (df.amount * df.token_usd_price).astype(int)
        return df

    def get_payment_stats(enriched_df: pd.DataFrame) -> Dict[str, int | Decimal]:
        """
        Calcluate some basic stats from the enriched payments data
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
            "earliest_txn_age_in_days": (datetime.now() - enriched_df.txn_time.min()).days,
            "last_txn_age_in_days": (datetime.now() - enriched_df.txn_time.max()).days,
            "unique_payees": enriched_df["to"].nunique(),
            "unique_payers": enriched_df["from"].nunique(),
        }

    @classmethod
    def fetch(
        cls,
        chain_name: str,
        borrower_wallet_address: str,
        receivable_param: str,
        rn_subgraph_endpoint_url: str = None,
        rn_invoice_endpoint_url: str = None,
    ) -> RequestNetworkInvoiceSignals:
        if rn_subgraph_endpoint_url is None:
            rn_subgraph_endpoint_url = get_rn_subgraph_endpoint_url(chain_name)
        if rn_invoice_endpoint_url is None:
            rn_invoice_endpoint_url = get_rn_invoice_api_url(chain_name)

        if not Web3.isAddress(borrower_wallet_address):
            raise ValueError(f"Invalid borrower wallet address: {borrower_wallet_address}")

        invoice = Invoice.from_request_id(receivable_param, rn_invoice_endpoint_url)

        records = []
        records.extend(cls._get_payments(invoice.payer, None, rn_subgraph_endpoint_url))
        records.extend(cls._get_payments(None, invoice.payee, rn_subgraph_endpoint_url))
        payments_df = pd.DataFrame.from_records(records)
        enriched_payments_df = cls.enrich_payments_data(payments_df, chain_name)

        payer_stats = cls.get_payment_stats(enriched_payments_df[enriched_payments_df["from"] == invoice.payer])
        payee_stats = cls.get_payment_stats(enriched_payments_df[enriched_payments_df["to"] == invoice.payee])
        pair_stats = cls.get_payment_stats(
            enriched_payments_df[
                (enriched_payments_df["from"] == invoice.payer) & (enriched_payments_df["to"] == invoice.payee)
            ]
        )

        return RequestNetworkInvoiceSignals(
            payer_tenure=payer_stats.get("earliest_txn_age_in_days", 0),
            payer_recent=payer_stats.get("last_txn_age_in_days", 0),
            payer_count=payer_stats.get("total_txns", 0),
            payer_total_amount=payer_stats.get("total_amount", 0),
            payer_unique_payees=payer_stats.get("unique_payees", 0),
            payee_tenure=payee_stats.get("earliest_txn_age_in_days", 0),
            payee_recent=payee_stats.get("last_txn_age_in_days", 0),
            payee_count=payee_stats.get("total_txns", 0),
            payee_total_amount=payee_stats.get("total_amount", 0),
            payee_unique_payers=payee_stats.get("unique_payers", 0),
            mutual_count=pair_stats.get("total_txns", 0),
            mutual_total_amount=pair_stats.get("total_amount", 0),
            payee_match_borrower=(invoice.payee.lower() == borrower_wallet_address.lower()),
            borrower_own_invoice=(invoice.token_owner.lower() == borrower_wallet_address.lower()),
            days_until_due_date=((invoice.due_date - datetime.utcnow()).days),
            invoice_amount=invoice.amount,
            payer_on_allowlist=(invoice.payer.lower() in _ALLOWED_PAYER_ADDRESSES),
        )
