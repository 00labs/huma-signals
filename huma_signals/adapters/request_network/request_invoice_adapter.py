import datetime
from typing import Any, ClassVar

import pandas as pd
import structlog
import web3

from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.ethereum_wallet import adapter as ethereum_wallet_adapter
from huma_signals.adapters.polygon_wallet import adapter as polygon_wallet_adapter
from huma_signals.adapters.request_network import models
from huma_signals.commons import chains
from huma_signals.domain.clients.request_client import request_client
from huma_signals.settings import settings

_ALLOWED_PAYER_ADDRESSES = {"0x2177d6C4eC1a6511184CA6FfAb4FD1d1F5bFF39f".lower()}

logger = structlog.get_logger(__name__)


class RequestNetworkInvoiceAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "request_network"
    required_inputs: ClassVar[list[str]] = [
        "borrower_wallet_address",
        "receivable_param",
    ]
    signals: ClassVar[list[str]] = list(
        models.RequestNetworkInvoiceSignals.__fields__.keys()
    )

    def __init__(
        self,
        request_client_: request_client.BaseRequestClient | None = None,
        request_network_invoice_api_url: str = settings.request_network_invoice_api_url,
        request_network_subgraph_endpoint_url: str = settings.request_network_subgraph_endpoint_url,
        chain: chains.Chain = settings.chain,
    ) -> None:
        self.request_client = request_client_ or request_client.RequestClient()
        self.request_network_invoice_api_url = request_network_invoice_api_url
        self.request_network_subgraph_endpoint_url = (
            request_network_subgraph_endpoint_url
        )
        self.chain = chain

    async def fetch(  # pylint: disable=too-many-arguments, arguments-differ
        self,
        borrower_wallet_address: str,
        receivable_param: str,
        *args: Any,
        **kwargs: Any,
    ) -> models.RequestNetworkInvoiceSignals:
        if not web3.Web3.is_address(borrower_wallet_address):
            raise ValueError(
                f"Invalid borrower wallet address: {borrower_wallet_address}"
            )

        invoice = await models.Invoice.from_request_id(
            receivable_param, self.request_network_invoice_api_url
        )

        records = []
        records.extend(
            await self.request_client.get_payments(
                from_address=invoice.payer, to_address=None
            )
        )
        records.extend(
            await self.request_client.get_payments(
                from_address=None, to_address=invoice.payee
            )
        )
        payments_df = pd.DataFrame.from_records(records)
        enriched_payments_df = self.request_client.enrich_payments_data(
            payments_df, chain=self.chain
        )

        payer_stats = self.request_client.get_payment_stats(
            enriched_payments_df[enriched_payments_df["from"] == invoice.payer]
        )
        payee_stats = self.request_client.get_payment_stats(
            enriched_payments_df[enriched_payments_df["to"] == invoice.payee]
        )
        pair_stats = self.request_client.get_payment_stats(
            enriched_payments_df[
                (enriched_payments_df["from"] == invoice.payer)
                & (enriched_payments_df["to"] == invoice.payee)
            ]
        )

        # Fetch wallet tenure
        payee_wallet: ethereum_wallet_adapter.EthereumWalletSignals | polygon_wallet_adapter.PolygonWalletSignals
        payer_wallet: ethereum_wallet_adapter.EthereumWalletSignals | polygon_wallet_adapter.PolygonWalletSignals
        if self.chain in {chains.Chain.ETHEREUM, chains.Chain.GOERLI}:
            logger.info("Fetching wallet tenure for ethereum")
            payee_wallet = await ethereum_wallet_adapter.EthereumWalletAdapter().fetch(
                invoice.payee
            )
            payer_wallet = await ethereum_wallet_adapter.EthereumWalletAdapter().fetch(
                invoice.payer
            )
        elif self.chain == chains.Chain.POLYGON:
            logger.info("Fetching wallet tenure for polygon")
            payee_wallet = await polygon_wallet_adapter.PolygonWalletAdapter().fetch(
                invoice.payee
            )
            payer_wallet = await polygon_wallet_adapter.PolygonWalletAdapter().fetch(
                invoice.payer
            )
        else:
            raise ValueError(f"Unsupported chain for wallet tenure: {settings.chain}")

        return models.RequestNetworkInvoiceSignals(
            payer_tenure=payer_wallet.wallet_tenure_in_days,
            payer_recent=int(payer_stats.get("last_txn_age_in_days", 0)),
            payer_count=int(payer_stats.get("total_txns", 0)),
            payer_total_amount=int(payer_stats.get("total_amount", 0)),
            payer_unique_payees=int(payer_stats.get("unique_payees", 0)),
            payee_tenure=payee_wallet.wallet_tenure_in_days,
            payee_recent=int(payee_stats.get("last_txn_age_in_days", 0)),
            payee_count=int(payee_stats.get("total_txns", 0)),
            payee_total_amount=int(payee_stats.get("total_amount", 0)),
            payee_unique_payers=int(payee_stats.get("unique_payers", 0)),
            mutual_count=int(pair_stats.get("total_txns", 0)),
            mutual_total_amount=int(pair_stats.get("total_amount", 0)),
            payee_match_borrower=(
                invoice.payee.lower() == borrower_wallet_address.lower()
            ),
            borrower_own_invoice=(
                invoice.token_owner.lower() == borrower_wallet_address.lower()
            ),
            payer_match_payee=(invoice.payer.lower() == invoice.payee.lower()),
            days_until_due_date=(invoice.due_date - datetime.datetime.utcnow()).days,
            invoice_amount=invoice.amount,
            # payer_on_allowlist=(invoice.payer.lower() in _ALLOWED_PAYER_ADDRESSES),
            payer_on_allowlist=True,
        )
