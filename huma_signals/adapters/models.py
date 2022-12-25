from typing import ClassVar, List

from pydantic import Field

from huma_signals.models import HumaBaseModel


class SignalAdapterBase(HumaBaseModel):
    name: ClassVar[str] = Field(..., description="Signal Adapter's name")
    signals: ClassVar[List[str]] = Field(..., description="Signals that the adapter can fetch")
    required_inputs: ClassVar[List[str]] = Field(..., description="Inputs that the adapter requires")
