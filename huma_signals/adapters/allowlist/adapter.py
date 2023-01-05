import os
from typing import ClassVar, List

import requests

from huma_signals.adapters.models import SignalAdapterBase
from huma_signals.commons.chains import Chain
from huma_signals.models import HumaBaseModel

ALLOW_LIST_ENDPOINT = os.getenv("ALLOW_LIST_ENDPOINT", "https://dev.allowlist.huma.finance")


class AllowListSignal(HumaBaseModel):
    """
    Signals emitted by the allowlist adapter.

    Note this is a temporary adapter and will be removed once the allowlist is integrated into the EAs.
    """

    on_allowlist: bool = False


class AllowListAdapter(SignalAdapterBase):
    name: ClassVar[str] = "allowlist"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address", "chain_name"]
    signals: ClassVar[List[str]] = list(AllowListSignal.__fields__.keys())

    @classmethod
    def fetch(
        cls, borrower_wallet_address: str, chain_name: str, allowlist_endpoint: str = ALLOW_LIST_ENDPOINT
    ) -> AllowListSignal:
        chain = Chain.from_chain_name(chain_name)
        if chain.is_testnet():
            response = requests.get(f"{allowlist_endpoint}/user/testnet/{borrower_wallet_address}")
        else:
            response = requests.get(f"{allowlist_endpoint}/user/mainnet/{borrower_wallet_address}")
        if response.status_code == 200 and response.json().get("status") == "found":
            return AllowListSignal(
                on_allowlist=True,
            )
        return AllowListSignal(on_allowlist=False)
