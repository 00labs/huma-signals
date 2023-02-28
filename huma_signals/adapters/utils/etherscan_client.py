import pydantic
import httpx

from huma_signals import models
from huma_signals.settings import settings


class EtherscanClient(models.HumaBaseModel):
    base_url: str = pydantic.Field(default=settings.etherscan_base_url)
    api_key: str = pydantic.Field(default=settings.etherscan_api_key)

    async def get_contract_abi(self, address: str) -> str:
        try:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                resp = await client.get(
                    f"{self.base_url}/api?"
                    f"module=contract&"
                    f"action=getabi&"
                    f"address={address}&"
                    f"apikey={self.api_key}",
                )
                resp.raise_for_status()
                payload = resp.json()
                if payload["status"] == "1":
                    return payload["result"]
        except httpx.HTTPStatusError as e:
            raise e
