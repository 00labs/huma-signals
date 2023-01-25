import os
from typing import Any, ClassVar, List

import requests

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
    def fetch(  # pylint: disable=arguments-differ
        cls,
        borrower_wallet_address: str,
        chain_name: str,
        *args: Any,
        allowlist_endpoint: str = ALLOW_LIST_ENDPOINT,
        **kwargs: Any,
    ) -> AllowListSignal:
        chain = chains.Chain.from_chain_name(chain_name)
        if chain.is_testnet():
            response = requests.get(
                f"{allowlist_endpoint}/user/testnet/{borrower_wallet_address}",
                timeout=10,
            )
        else:
            response = requests.get(
                f"{allowlist_endpoint}/user/mainnet/{borrower_wallet_address}",
                timeout=10,
            )
        if response.status_code == 200 and response.json().get("status") == "found":
            return AllowListSignal(
                on_allowlist=True,
            )
        return AllowListSignal(on_allowlist=False)
