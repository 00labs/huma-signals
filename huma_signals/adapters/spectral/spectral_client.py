from datetime import datetime

import httpx
import pydantic
import structlog

from huma_signals import models
from huma_signals.settings import settings

logger = structlog.get_logger()


class SpectralScoreIngredients(models.HumaBaseModel):
    credit_mix: int
    defi_actions: int
    health_and_risk: int
    liquidation: int
    market: float
    time: int
    wallet: int


class SpectralWalletSignals(models.HumaBaseModel):
    score: float
    score_ingredients: SpectralScoreIngredients
    score_timestamp: datetime
    probability_of_liquidation: float
    risk_level: str
    wallet_address: str


class SpectralClient(models.HumaBaseModel):
    """Spectral Client"""
    base_url: str = pydantic.Field(default='https://api.spectral.finance')
    api_key: str = pydantic.Field(
        default=settings.spectral_api_key,
        description="Ethereum private key of the Spectral client"
    )

    @pydantic.validator("base_url")
    def validate_pbase_url(cls, value: str) -> str:
        if not value:
            raise ValueError("spectral base_url is required")
        return value

    @pydantic.validator("api_key")
    def validate_api_key(cls, value: str) -> str:
        if not value:
            raise ValueError("spectral api_key is required")
        return value

    async def _create_score(self, wallet_address: str) -> None:
        try:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                request = (
                    f"/api/v1/addresses/{wallet_address}"
                    f"/calculate_score"
                )
                headers = {"Authorization": f"Bearer {self.api_key}"}
                resp = await client.post(request, headers=headers)
                resp.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error("Error fetching transactions", exc_info=True, request=request)

    async def get_scores(self, wallet_address: str) -> SpectralWalletSignals:
        await self._create_score(wallet_address)
        try:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                request = f"/api/v1/addresses/{wallet_address}"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                resp = await client.get(request, headers=headers)
                resp.raise_for_status()
                return SpectralWalletSignals(**resp.json())
        except httpx.HTTPStatusError:
            logger.error("Error fetching transactions", exc_info=True, request=request)
