# pylint: disable=too-few-public-methods
from typing import Any, Dict, List

from huma_signals import models


class SignalFetchRequest(models.HumaBaseModel):
    signal_names: List[str]
    adapter_inputs: Dict[str, Any]


class SignalFetchResponse(models.HumaBaseModel):
    signals: Dict[str, Any]
