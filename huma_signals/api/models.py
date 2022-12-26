from typing import Any, Dict, List

from huma_signals.models import HumaBaseModel


class SignalFetchRequest(HumaBaseModel):
    signal_names: List[str]
    adapter_inputs: Dict[str, Any]


class SignalFetchResponse(HumaBaseModel):
    signals: Dict[str, Any]
