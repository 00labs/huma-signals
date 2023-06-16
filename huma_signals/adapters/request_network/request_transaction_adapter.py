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


class RequestTransactionAdapter(adapter_models.SignalAdapterBase):
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

    async def fetch(  # pylint: disable=arguments-differ
        self,
        payer_address: str,
        payee_address: str,
        *args: Any,
        **kwargs: Any,
    ) -> models.RequestTransactionSignals:
        if not web3.Web3.is_address(payer_address):
            raise exceptions.InvalidAddressException(
                f"Invalid payer address: {payer_address}"
            )
        if not web3.Web3.is_address(payee_address):
            raise exceptions.InvalidAddressException(
                f"Invalid payee address: {payee_address}"
            )

        payer_payments = await self.request_client.get_payments(
            from_address=payer_address,
            to_address=None,
        )
        payee_payments = await self.request_client.get_payments(
            from_address=None,
            to_address=payee_address,
        )
        payments_df = pd.DataFrame.from_records([*payer_payments, *payee_payments])
        enriched_payments_df = self.request_client.enrich_payments_data(
            payments_df, self.chain
        )

        payer_stats = self.request_client.get_payment_stats(
            enriched_payments_df[enriched_payments_df["from"] == payer_address]
        )
        payee_stats = self.request_client.get_payment_stats(
            enriched_payments_df[enriched_payments_df["to"] == payee_address]
        )
        pair_stats = self.request_client.get_payment_stats(
            enriched_payments_df[
                (enriched_payments_df["from"] == payer_address)
                & (enriched_payments_df["to"] == payee_address)
            ]
        )

        payee_wallet: ethereum_wallet_adapter.EthereumWalletSignals | polygon_wallet_adapter.PolygonWalletSignals
        payer_wallet: ethereum_wallet_adapter.EthereumWalletSignals | polygon_wallet_adapter.PolygonWalletSignals
        payee_wallet = await self.wallet_adapter.fetch(payee_address)
        payer_wallet = await self.wallet_adapter.fetch(payer_address)

        return models.RequestTransactionSignals(
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
        )
