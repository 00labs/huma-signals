from typing import Any, ClassVar, List

import structlog

from huma_signals.adapters import models
from huma_signals.adapters.spectral import spectral_client

logger = structlog.get_logger()


class SpectralWalletAdapter(models.SignalAdapterBase):
    name: ClassVar[str] = "spectral_wallet"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address"]
    signals: ClassVar[List[str]] = list(
        spectral_client.SpectralWalletSignals.__fields__.keys()
    )

    spectral_api_client: spectral_client.SpectralClient = (
        spectral_client.SpectralClient()
    )

    async def fetch(  # pylint: disable=arguments-differ
        self, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> spectral_client.SpectralWalletSignals:
        return await self.spectral_api_client.get_scores(borrower_wallet_address)
