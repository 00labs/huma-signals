from typing import Any, ClassVar, Dict, List

import pydantic

from huma_signals import models


class SignalAdapterBase(models.HumaBaseModel):
    name: ClassVar[str] = pydantic.Field(..., description="Signal Adapter's name")
    signals: ClassVar[List[str]] = pydantic.Field(
        ..., description="Signals that the adapter can fetch"
    )
    required_inputs: ClassVar[List[str]] = pydantic.Field(
        ..., description="Inputs that the adapter requires"
    )

    @classmethod
    def definition(cls) -> Dict[str, str | List[str]]:
        return {
            "name": cls.name,
            "signals": cls.signals,
            "required_inputs": cls.required_inputs,
        }

    async def fetch(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
