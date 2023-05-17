from typing import Protocol

import httpx
import structlog

from huma_signals.clients.eth_client import eth_types

logger = structlog.get_logger(__name__)


class BaseEthClient(Protocol):
    async def get_transactions(
        self, wallet_address: str
    ) -> list[eth_types.EthTransaction]:
        pass


class EthClient:
    def __init__(
        self,
        etherscan_base_url: str,
        etherscan_api_key: str,
    ) -> None:
        self.etherscan_base_url = etherscan_base_url
        self.etherscan_api_key = etherscan_api_key

    async def get_transactions(
        self, wallet_address: str
    ) -> list[eth_types.EthTransaction]:
        try:
            async with httpx.AsyncClient(base_url=self.etherscan_base_url) as client:
                request = (
                    f"/api?module=account&action=txlist"
                    f"&address={wallet_address}"
                    f"&startblock=0&endblock=99999999"
                    f"&sort=asc"
                    f"&apikey={self.etherscan_api_key}"
                )
                resp = await client.get(request)
                resp.raise_for_status()
                payload = eth_types.EthTransactionResponse(**resp.json())
                if payload.status == "1":
                    return payload.result
        except httpx.HTTPStatusError:
            logger.exception("Error fetching transactions", request=request)

        return []
