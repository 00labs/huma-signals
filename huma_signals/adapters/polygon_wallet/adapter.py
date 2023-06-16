import datetime
from typing import Any

import structlog
from huma_utils import datetime_utils

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.polygon_wallet.settings import settings
from huma_signals.clients.polygon_client import polygon_client, polygon_types

logger = structlog.get_logger()


class PolygonWalletSignals(models.HumaBaseModel):
    total_transactions: int
    total_sent: int
    total_received: int
    wallet_tenure_in_days: int
    total_income_90days: float
    total_transactions_90days: int


class BasePolygonWalletAdapter(adapter_models.SignalAdapterBase):
    async def fetch(  # pylint: disable=arguments-differ
        self, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> PolygonWalletSignals:
        raise NotImplementedError


class PolygonWalletAdapter(BasePolygonWalletAdapter):
    def __init__(
        self,
        polygon_client_: polygon_client.BasePolygonClient | None = None,
        polygonscan_base_url: str = settings.polygonscan_base_url,
        polygonscan_api_key: str = settings.polygonscan_api_key,
    ) -> None:
        self.polygon_client = polygon_client_ or polygon_client.PolygonClient(
            polygonscan_base_url=polygonscan_base_url,
            polygonscan_api_key=polygonscan_api_key,
        )

    async def fetch(
        self, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> PolygonWalletSignals:
        transactions = await self.polygon_client.get_transactions(
            borrower_wallet_address,
        )
        now = datetime_utils.tz_aware_utc_now()
        min_tx_timestamp = (
            None
            if len(transactions) == 0
            else min(tx.time_stamp for tx in transactions)
        )

        return PolygonWalletSignals(
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
    now: datetime.datetime, transaction: polygon_types.PolygonTransaction
) -> bool:
    return (
        now - datetime_utils.timestamp_to_tz_aware_utc_datetime(transaction.time_stamp)
    ).days < 90
