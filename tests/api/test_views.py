from typing import ClassVar, List

import pytest

from huma_signals.adapters.models import SignalAdapterBase
from huma_signals.api.views import _list_adapters
from huma_signals.models import HumaBaseModel


class DummySignals(HumaBaseModel):
    test_signal: str


class DummyAdapter(SignalAdapterBase):
    name: ClassVar[str] = "dummy_adapter"
    required_inputs: ClassVar[List[str]] = ["test_input"]
    signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())


@pytest.fixture
def dummy_registry():
    return {"dummy_adapter": DummyAdapter}


def describe_get_list_adapters():
    def it_returns_a_list_of_adapters(dummy_registry):
        response = _list_adapters(dummy_registry)

        assert response["adapters"] == [
            {
                "name": "dummy_adapter",
                "required_inputs": ["test_input"],
                "signals": ["test_signal"],
            }
        ]
