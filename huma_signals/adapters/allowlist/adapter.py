from typing import Any, ClassVar, List

import httpx
import pydantic

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.commons import chains
from huma_signals.settings import settings


class AllowListSignal(models.HumaBaseModel):
    """
    Signals emitted by the allowlist adapter.

    Note this is a temporary adapter and will be removed once the allowlist is integrated into the EAs.
    """

    on_allowlist: bool = False


class AllowListAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "allowlist"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address"]
    signals: ClassVar[List[str]] = list(AllowListSignal.__fields__.keys())

    chain: chains.Chain = pydantic.Field(default=settings.chain)
    allowlist_endpoint: str = pydantic.Field(default=settings.allow_list_endpoint)

    @pydantic.validator("allowlist_endpoint")
    def validate_allowlist_endpoint(cls, value: str) -> str:
        if not value:
            raise ValueError("allowlist_endpoint is required")
        return value

    async def fetch(  # pylint: disable=arguments-differ
        self,
        borrower_wallet_address: str,
        *args: Any,
        **kwargs: Any,
    ) -> AllowListSignal:
        url = f"/user/{'testnet' if self.chain.is_testnet() else 'mainnet'}/{borrower_wallet_address}"
        try:
            async with httpx.AsyncClient(base_url=self.allowlist_endpoint) as client:
                resp = await client.get(url=url)
                resp.raise_for_status()
                if resp.json().get("status") == "found":
                    return AllowListSignal(on_allowlist=True)
        except httpx.HTTPStatusError:
            pass

        return AllowListSignal(on_allowlist=False)
