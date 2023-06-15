import datetime
from typing import Any

import pandas as pd
import structlog
import web3
from huma_utils import chain_utils

from huma_signals import exceptions
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.ethereum_wallet import adapter as ethereum_wallet_adapter
from huma_signals.adapters.polygon_wallet import adapter as polygon_wallet_adapter
from huma_signals.adapters.request_network import models
from huma_signals.adapters.request_network.settings import settings
from huma_signals.clients.request_client import request_client

logger = structlog.get_logger(__name__)

_WALLET_ADAPTER_BY_CHAIN = {
    chain_utils.Chain.ETHEREUM: ethereum_wallet_adapter.EthereumWalletAdapter,
    chain_utils.Chain.GOERLI: ethereum_wallet_adapter.EthereumWalletAdapter,
    chain_utils.Chain.POLYGON: polygon_wallet_adapter.PolygonWalletAdapter,
}


class RequestInvoiceAdapter(adapter_models.SignalAdapterBase):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        request_client_: request_client.BaseRequestClient | None = None,
        wallet_adapter: ethereum_wallet_adapter.BaseEthereumWalletAdapter
        | polygon_wallet_adapter.BasePolygonWalletAdapter
        | None = None,
        request_network_subgraph_endpoint_url: str = settings.request_network_subgraph_endpoint_url,
        invoice_api_url: str = settings.request_network_invoice_api_url,
        chain: chain_utils.Chain = settings.chain,
    ) -> None:
        self.request_client = request_client_ or request_client.RequestClient(
            request_network_subgraph_endpoint_url=request_network_subgraph_endpoint_url,
            invoice_api_url=invoice_api_url,
        )
        self.chain = chain
        if wallet_adapter is not None:
            self.wallet_adapter = wallet_adapter
        else:
            try:
                self.wallet_adapter = _WALLET_ADAPTER_BY_CHAIN[self.chain]()
            except KeyError as e:
                raise ValueError(
                    f"Unsupported chain for wallet tenure: {self.chain}"
                ) from e

    async def fetch(  # pylint: disable=too-many-arguments, arguments-differ
        self,
        borrower_wallet_address: str,
        receivable_param: str,
        *args: Any,
        **kwargs: Any,
    ) -> models.RequestInvoiceSignals:
        if not web3.Web3.is_address(borrower_wallet_address):
            raise exceptions.InvalidAddressException(
                f"Invalid borrower wallet address: {borrower_wallet_address}"
            )

        invoice = await self.request_client.get_invoice(request_id=receivable_param)
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
        payee_wallet = await self.wallet_adapter.fetch(invoice.payee)
        payer_wallet = await self.wallet_adapter.fetch(invoice.payer)

        return models.RequestInvoiceSignals(
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
            token_id=invoice.token_id,
        )
