from typing import Any, ClassVar, Dict, List, Type

import pytest

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.api import views


class DummySignals(models.HumaBaseModel):
    test_signal: str


class DummyAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "dummy_adapter"
    required_inputs: ClassVar[List[str]] = ["test_input"]
    signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())

    @classmethod
    def fetch(cls, *args: Any, **kwargs: Any) -> Any:
        pass


@pytest.fixture
def dummy_registry() -> Dict[str, Type[adapter_models.SignalAdapterBase]]:
    return {"dummy_adapter": DummyAdapter}


def describe_get_list_adapters() -> None:
    def it_returns_a_list_of_adapters(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        response = views._list_adapters(dummy_registry)

        assert response["adapters"] == [
            {
                "name": "dummy_adapter",
                "required_inputs": ["test_input"],
                "signals": ["test_signal"],
            }
        ]
