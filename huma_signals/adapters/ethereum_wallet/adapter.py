import datetime
from typing import Any

from huma_utils import datetime_utils

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.ethereum_wallet.settings import settings
from huma_signals.clients.eth_client import eth_client, eth_types


class EthereumWalletSignals(models.HumaBaseModel):
    total_transactions: int
    total_sent: int
    total_received: int
    wallet_tenure_in_days: int
    total_income_90days: int
    total_transactions_90days: int


class BaseEthereumWalletAdapter(adapter_models.SignalAdapterBase):
    async def fetch(  # pylint: disable=arguments-differ
        self, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> EthereumWalletSignals:
        raise NotImplementedError


class EthereumWalletAdapter(BaseEthereumWalletAdapter):
    def __init__(
        self,
        eth_client_: eth_client.BaseEthClient | None = None,
        etherscan_base_url: str = settings.etherscan_base_url,
        etherscan_api_key: str = settings.etherscan_api_key,
    ) -> None:
        self.eth_client = eth_client_ or eth_client.EthClient(
            etherscan_base_url=etherscan_base_url,
            etherscan_api_key=etherscan_api_key,
        )

    async def fetch(
        self, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> EthereumWalletSignals:
        transactions = await self.eth_client.get_transactions(
            borrower_wallet_address,
        )
        now = datetime_utils.tz_aware_utc_now()
        min_tx_timestamp = (
            None
            if len(transactions) == 0
            else min(tx.time_stamp for tx in transactions)
        )

        return EthereumWalletSignals(
            total_transactions=len(transactions),
            total_sent=len(
                [
                    tx
                    for tx in transactions
                    if tx.from_ == borrower_wallet_address.lower()
                ]
            ),
            total_received=len(
                [tx for tx in transactions if tx.to == borrower_wallet_address.lower()]
            ),
            wallet_tenure_in_days=0
            if min_tx_timestamp is None
            else (
                now
                - datetime_utils.timestamp_to_tz_aware_utc_datetime(min_tx_timestamp)
            ).days,
            total_income_90days=sum(
                int(tx.value)
                for tx in transactions
                if _is_transaction_within_90_days(now=now, transaction=tx)
                and tx.to == borrower_wallet_address.lower()
            ),
            total_transactions_90days=len(
                [
                    tx
                    for tx in transactions
                    if _is_transaction_within_90_days(now=now, transaction=tx)
                ]
            ),
        )


def _is_transaction_within_90_days(
    now: datetime.datetime, transaction: eth_types.EthTransaction
) -> bool:
    return (
        now - datetime_utils.timestamp_to_tz_aware_utc_datetime(transaction.time_stamp)
    ).days < 90
