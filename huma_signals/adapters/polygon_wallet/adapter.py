import datetime
from typing import Any, ClassVar, List

import httpx
import pandas as pd
import pydantic
import structlog

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.settings import settings

logger = structlog.get_logger()


class PolygonWalletSignals(models.HumaBaseModel):
    total_transactions: int
    total_sent: int
    total_received: int
    wallet_tenure_in_days: int
    total_income_90days: float
    total_transactions_90days: int


class PolygonWalletAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "polygon_wallet"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address"]
    signals: ClassVar[List[str]] = list(PolygonWalletSignals.__fields__.keys())

    polygonscan_base_url: str = pydantic.Field(default=settings.polygonscan_base_url)
    polygonscan_api_key: str = pydantic.Field(default=settings.polygonscan_api_key)

    @pydantic.validator("polygonscan_base_url")
    def validate_polygonscan_base_url(cls, value: str) -> str:
        if not value:
            raise ValueError("polygonscan_base_url is required")
        return value

    @pydantic.validator("polygonscan_api_key")
    def validate_polygonscan_api_key(cls, value: str) -> str:
        if not value:
            raise ValueError("polygonscan_api_key is required")
        return value

    @classmethod
    async def _node_get_transactions(
        cls, wallet_address: str, polygonscan_base_url: str, polygonscan_api_key: str
    ) -> List[Any]:
        try:
            async with httpx.AsyncClient(base_url=polygonscan_base_url) as client:
                request = (
                    f"/api?module=account&action=txlist"
                    f"&address={wallet_address}"
                    f"&startblock=0&endblock=99999999"
                    f"&sort=asc"
                    f"&apikey={polygonscan_api_key}"
                )
                resp = await client.get(request)

                resp.raise_for_status()
                payload = resp.json()
                if payload["status"] == "1":
                    return payload["result"]
        except httpx.HTTPStatusError:
            logger.error("Error fetching transactions", exc_info=True, request=request)

        return []

    async def fetch(  # pylint: disable=arguments-differ
        self, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> PolygonWalletSignals:
        raw_txns = await self._node_get_transactions(
            borrower_wallet_address,
            polygonscan_base_url=self.polygonscan_base_url,
            polygonscan_api_key=self.polygonscan_api_key,
        )
        txn_df = pd.DataFrame.from_records(raw_txns)
        if len(txn_df) == 0:
            return PolygonWalletSignals(
                total_transactions=0,
                total_sent=0,
                total_received=0,
                wallet_tenure_in_days=0,
                total_income_90days=0,
                total_transactions_90days=0,
            )
        txn_df["timeStamp"] = pd.to_datetime(txn_df["timeStamp"], unit="s")
        txn_df["value"] = txn_df["value"].astype(float)
        txn_df["from"] = txn_df["from"].str.lower()
        txn_df["to"] = txn_df["to"].str.lower()
        txn_df["is_sent"] = txn_df["from"] == borrower_wallet_address.lower()
        txn_df["is_received"] = txn_df["to"] == borrower_wallet_address.lower()
        txn_df["in_90days"] = txn_df[
            "timeStamp"
        ] > datetime.datetime.now() - pd.Timedelta(days=90)
        # TODO: Limit to selected set of tokens
        txn_df["income"] = txn_df["value"] * txn_df["is_received"].astype(float)

        return PolygonWalletSignals(
            total_transactions=len(txn_df),
            total_sent=sum(txn_df["is_sent"]),
            total_received=sum(txn_df["is_received"]),
            wallet_tenure_in_days=(
                datetime.datetime.now() - txn_df["timeStamp"].min()
            ).days,
            total_income_90days=sum(txn_df["income"] * txn_df["in_90days"]),
            total_transactions_90days=sum(txn_df["in_90days"]),
        )
