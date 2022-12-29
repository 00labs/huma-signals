from typing import ClassVar, List

import requests

from huma_signals.models import HumaBaseModel
from huma_signals.adapters.models import SignalAdapterBase



class AllowListSignal(HumaBaseModel):
    on_allowlist: bool = False


class AllowListAdapter(SignalAdapterBase):
    name: ClassVar[str] = "allowlist"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address", "chain_name"]
    signals: ClassVar[List[str]] = AllowListSignal.__fields__.keys()

    @classmethod
    def fetch(cls, borrower_wallet_address: str, pool_address: str) -> AllowListSignal:
        response = requests.get(f"{settings.allowlist_endpoint}/user/{borrower_wallet_address}/{pool_address}")
        if response.status_code == 200 and response.json().get("status") == "found":
            return AllowListSignal(
                on_allowlist=True,
            )
        return AllowListSignal(on_allowlist=False)
