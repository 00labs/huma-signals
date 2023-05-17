from typing import Protocol

import httpx
import structlog

from huma_signals.clients.polygon_client import polygon_types

logger = structlog.get_logger(__name__)


class BasePolygonClient(Protocol):
    async def get_transactions(
        self, wallet_address: str
    ) -> list[polygon_types.PolygonTransaction]:
        pass


class PolygonClient(BasePolygonClient):
    def __init__(
        self,
        polygonscan_base_url: str,
        polygonscan_api_key: str,
    ) -> None:
        self.polygonscan_base_url = polygonscan_base_url
        self.polygonscan_api_key = polygonscan_api_key

    async def get_transactions(
        self, wallet_address: str
    ) -> list[polygon_types.PolygonTransaction]:
        try:
            async with httpx.AsyncClient(base_url=self.polygonscan_base_url) as client:
                request = (
                    f"/api?module=account&action=txlist"
                    f"&address={wallet_address}"
                    f"&startblock=0&endblock=99999999"
                    f"&sort=asc"
                    f"&apikey={self.polygonscan_api_key}"
                )
                resp = await client.get(request)

                resp.raise_for_status()
                payload = polygon_types.PolygonTransactionResponse(**resp.json())
                if payload.status == "1":
                    return payload.result
        except httpx.HTTPStatusError:
            logger.exception("Error fetching transactions", request=request)

        return []
