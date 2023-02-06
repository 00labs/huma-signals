import os
from typing import Any, ClassVar, List

import httpx

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.commons import chains

ALLOW_LIST_ENDPOINT = os.getenv(
    "ALLOW_LIST_ENDPOINT", "https://dev.allowlist.huma.finance"
)


class AllowListSignal(models.HumaBaseModel):
    """
    Signals emitted by the allowlist adapter.

    Note this is a temporary adapter and will be removed once the allowlist is integrated into the EAs.
    """

    on_allowlist: bool = False


class AllowListAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "allowlist"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address", "chain_name"]
    signals: ClassVar[List[str]] = list(AllowListSignal.__fields__.keys())

    @classmethod
    async def fetch(  # pylint: disable=arguments-differ
        cls,
        borrower_wallet_address: str,
        chain_name: str,
        *args: Any,
        allowlist_endpoint: str = ALLOW_LIST_ENDPOINT,
        **kwargs: Any,
    ) -> AllowListSignal:
        chain = chains.Chain.from_chain_name(chain_name)
        url = f"/user/{'testnet' if chain.is_testnet() else 'mainnet'}/{borrower_wallet_address}"
        try:
            async with httpx.AsyncClient(base_url=allowlist_endpoint) as client:
                resp = await client.get(url=url)
                resp.raise_for_status()
                if resp.json().get("status") == "found":
                    return AllowListSignal(on_allowlist=True)
        except httpx.HTTPStatusError:
            pass

        return AllowListSignal(on_allowlist=False)
