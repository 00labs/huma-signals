from typing import Any, ClassVar, Dict, List, Type
from unittest import mock

import pytest

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.api import views
from huma_signals.api.models import SignalFetchRequest


class DummySignals(models.HumaBaseModel):
    test_signal: str


class DummyAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "dummy_adapter"
    required_inputs: ClassVar[List[str]] = ["test_input"]
    signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())

    async def fetch(self, *args: Any, **kwargs: Any) -> Any:
        return DummySignals(test_signal=kwargs["test_input"])


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


def describe_post_fetch() -> None:
    async def it_returns_a_list_of_signals() -> None:
        with mock.patch.dict(
            "huma_signals.adapters.registry.ADAPTER_REGISTRY",
            {"dummy_adapter": DummyAdapter},
        ):
            response = await views.post_fetch(
                SignalFetchRequest(
                    signal_names=["dummy_adapter.test_signal"],
                    adapter_inputs={"test_input": "test"},
                )
            )

            assert response == {"signals": {"dummy_adapter.test_signal": "test"}}
