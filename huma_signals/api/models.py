# pylint: disable=too-few-public-methods
from typing import Any

from huma_signals import models


class SignalFetchRequest(models.HumaBaseModel):
    signal_names: list[str]
    adapter_inputs: dict[str, Any]


class SignalFetchResponse(models.HumaBaseModel):
    signals: dict[str, Any]
