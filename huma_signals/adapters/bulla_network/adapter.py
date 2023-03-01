import datetime
import decimal
from typing import Any, ClassVar, Dict, List, Optional

import httpx
import pandas as pd
import pydantic
import structlog
import web3
import json

from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.bulla_network import models
from huma_signals.adapters.ethereum_wallet import adapter as ethereum_wallet_adapter
from huma_signals.adapters.polygon_wallet import adapter as polygon_wallet_adapter
from huma_signals.commons import chains, tokens
from huma_signals.settings import settings

_DEFAULT_GRAPHQL_CHUNK_SIZE = 1000

logger = structlog.get_logger(__name__)


class BullaNetworkInvoiceAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "bulla_network"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address", "claim_id"]
    signals: ClassVar[List[str]] = list(
        models.BullaNetworkInvoiceSignals.__fields__.keys()
    )
    bulla_network_subgraph_endpoint_url: str = pydantic.Field(
        default=settings.bulla_network_subgraph_endpoint_url
    )

    @pydantic.validator("bulla_network_subgraph_endpoint_url")
    def validate_bulla_network_subgraph_endpoint_url(cls, value: str) -> str:
        if not value:
            raise ValueError("bulla_network_subgraph_endpoint_url is required")
        return value

    @classmethod
    async def _get_claim_payments(
        cls,
        creditor_address: Optional[str],
        debtor_address: Optional[str],
        bn_subgraph_endpoint_url: str,
    ) -> List[Any]:
        where_clause = ""
        if creditor_address:
            where_clause += f'claim_: {{creditor: "{creditor_address}"}},\n'
        if debtor_address:
            where_clause += f'debtor: "{debtor_address}",\n'

        claim_payments = []
        last_chunk_size = _DEFAULT_GRAPHQL_CHUNK_SIZE
        last_id = ""
        async with httpx.AsyncClient() as client:
            while last_chunk_size == _DEFAULT_GRAPHQL_CHUNK_SIZE:
                query = f"""
                    query HumaBullaNetworkClaims {{
                        claimPaymentEvents(
                            first: {_DEFAULT_GRAPHQL_CHUNK_SIZE},
                            where: {{
                                {where_clause}
                                id_gt: "{last_id}"
                            }}
                            orderBy: id,
                            orderDirection: asc
                        ) {{
                            id
                            debtor
                            claim {{
                                id
                                creditor {{id}}
                                token {{symbol}}}}
                            paymentAmount
                            timestamp
                            transactionHash
                        }}
                    }}
                    """
                resp = await client.post(
                    bn_subgraph_endpoint_url,
                    json={"query": query},
                )
                response_json = resp.json()
                new_chunk = response_json["data"]["claimPaymentEvents"]
                claim_payments.extend(new_chunk)
                last_chunk_size = len(new_chunk)
                if len(claim_payments) > 0:
                    last_id = claim_payments[-1]["id"]

        return claim_payments

    @classmethod
    def enrich_claim_payments_data(cls, claims_raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches the raw claims data with additional information
        """
        if len(claims_raw_df) == 0:
            return pd.DataFrame(
                columns=[
                    "id",
                    "token_symbol",
                    "creditor_address",
                    "debtor_address",
                    "timestamp",
                    "transactionHash",
                    "amount",
                ]
            )
        df = claims_raw_df.copy().drop_duplicates("id")
        df["creditor"] = df.claim.apply(lambda x: x["creditor"]["id"])
        df["token_symbol"] = df.claim.apply(lambda x: x["token"]["symbol"])
        df["txn_time"] = pd.to_datetime(df.timestamp, unit="s")
        df["amount"] = df.paymentAmount.astype(float)
        df["token_usd_price"] = df['token_symbol'].map(
            tokens.TOKEN_USD_PRICE_MAPPING
        ).fillna(0)
        df["amount_usd"] = (df.amount * df.token_usd_price).astype(int)
        return df

    @classmethod
    def get_claim_payment_stats(
        cls, enriched_df: pd.DataFrame
    ) -> Dict[str, int | decimal.Decimal]:
        """
        Calculate some basic stats from the enriched claim data
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
            "unique_payees": enriched_df["creditor"].nunique(),
            "unique_payers": enriched_df["debtor"].nunique(),
        }

    async def fetch(  # pylint: disable=too-many-arguments, arguments-differ
        self,
        borrower_wallet_address: str,
        claim_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> models.BullaNetworkInvoiceSignals:
        if not web3.Web3.is_address(borrower_wallet_address):
            raise ValueError(
                f"Invalid borrower wallet address: {borrower_wallet_address}"
            )

        invoice = await models.Invoice.from_claim_id(
            claim_id, self.bulla_network_subgraph_endpoint_url
        )

        records = []
        records.extend(
            await self._get_claim_payments(
                None, invoice.payer, self.bulla_network_subgraph_endpoint_url
            )
        )
        records.extend(
            await self._get_claim_payments(
                invoice.payee, None , self.bulla_network_subgraph_endpoint_url
            )
        )
        claim_payments_df = pd.DataFrame.from_records(records)
        enriched_claim_payments_df = self.enrich_claim_payments_data(claim_payments_df)

        payer_stats = self.get_claim_payment_stats(
            enriched_claim_payments_df[
                enriched_claim_payments_df["debtor"] == invoice.payer
            ]
        )
        payee_stats = self.get_claim_payment_stats(
            enriched_claim_payments_df[
                enriched_claim_payments_df["creditor"] == invoice.payee
            ]
        )
        pair_stats = self.get_claim_payment_stats(
            enriched_claim_payments_df[
                (enriched_claim_payments_df["debtor"] == invoice.payer)
                & (enriched_claim_payments_df["creditor"] == invoice.payee)
            ]
        )

        # Fetch wallet tenure
        if settings.chain in {chains.Chain.ETHEREUM, chains.Chain.GOERLI}:
            logger.info("Fetching wallet tenure for ethereum")
            payee_wallet = await ethereum_wallet_adapter.EthereumWalletAdapter().fetch(
                invoice.payee
            )  # type: Any
            payer_wallet = await ethereum_wallet_adapter.EthereumWalletAdapter().fetch(
                invoice.payer
            )  # type: Any
        elif settings.chain == chains.Chain.POLYGON:
            logger.info("Fetching wallet tenure for polygon")
            payee_wallet = await polygon_wallet_adapter.PolygonWalletAdapter().fetch(
                invoice.payee
            )
            payer_wallet = await polygon_wallet_adapter.PolygonWalletAdapter().fetch(
                invoice.payer
            )
        else:
            raise ValueError(f"Unsupported chain for wallet tenure: {settings.chain}")

        return models.BullaNetworkInvoiceSignals(
            payer_tenure=payer_wallet.wallet_tenure_in_days,
            payer_recent=payer_stats.get("last_txn_age_in_days", 0),
            payer_count=payer_stats.get("total_txns", 0),
            payer_total_amount=payer_stats.get("total_amount", 0),
            payer_unique_payees=payer_stats.get("unique_payees", 0),
            payee_tenure=payee_wallet.wallet_tenure_in_days,
            payee_recent=payee_stats.get("last_txn_age_in_days", 0),
            payee_count=payee_stats.get("total_txns", 0),
            payee_total_amount=payee_stats.get("total_amount", 0),
            payee_unique_payers=payee_stats.get("unique_payers", 0),
            mutual_count=pair_stats.get("total_txns", 0),
            mutual_total_amount=pair_stats.get("total_amount", 0),
            payee_match_borrower=(
                invoice.payee.lower() == borrower_wallet_address.lower()
            ),
            borrower_own_invoice=(
                invoice.token_owner.lower() == borrower_wallet_address.lower()
            ),
            payer_match_payee=(invoice.payer.lower() == invoice.payee.lower()),
            days_until_due_date=((invoice.due_date - datetime.datetime.utcnow()).days),
            invoice_amount=invoice.amount,
            # payer_on_allowlist=(invoice.payer.lower() in _ALLOWED_PAYER_ADDRESSES),
            payer_on_allowlist=True,
        )
