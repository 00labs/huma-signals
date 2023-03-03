import structlog
from typing import Any, ClassVar, List

from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.spectral.spectral_client import SpectralClient, SpectralWalletSignals

logger = structlog.get_logger()


class SpectralWalletAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "spectral_wallet"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address"]
    signals: ClassVar[List[str]] = list(SpectralWalletSignals.__fields__.keys())

    spectral_client: SpectralClient = SpectralClient()

    async def fetch(  # pylint: disable=arguments-differ
        self, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> SpectralWalletSignals:
        return await self.spectral_client.get_scores(borrower_wallet_address)
