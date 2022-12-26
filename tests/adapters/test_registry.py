from typing import ClassVar, List

import pytest

from huma_signals.adapters.models import SignalAdapterBase
from huma_signals.adapters.registry import ADAPTER_REGISTRY, fetch_signal, find_required_adapter
from huma_signals.models import HumaBaseModel


class DummySignals(HumaBaseModel):
    test_signal: int
    test_signal2: str


class DummyAdapter(SignalAdapterBase):
    name: ClassVar[str] = "dummy_adapter"
    required_inputs: ClassVar[List[str]] = ["test_input"]
    signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())

    def fetch(self, test_input: int) -> DummySignals:
        return DummySignals(
            test_signal=test_input,
            test_signal2=test_input * 2,
        )


@pytest.fixture
def dummy_registry():
    return {"dummy_adapter": DummyAdapter}


def describe_ADAPTER_REGISTRY():
    assert ADAPTER_REGISTRY is not None
    assert issubclass(list(ADAPTER_REGISTRY.values())[0], SignalAdapterBase)


def describe_find_required_adapter():
    def it_returns_the_correct_adapter(dummy_registry):
        adapters = find_required_adapter(["dummy_adapter.test_signal"], dummy_registry)
        assert adapters == [DummyAdapter]

    def it_returns_the_correct_adapter_with_multiple_signals(dummy_registry):
        adapters = find_required_adapter(["dummy_adapter.test_signal", "dummy_adapter.test_signal2"], dummy_registry)
        assert adapters == [DummyAdapter]

    def it_returns_the_correct_adapter_with_multiple_adapters(dummy_registry):
        class DummyAdapter2(SignalAdapterBase):
            name: ClassVar[str] = "dummy_adapter2"
            required_inputs: ClassVar[List[str]] = ["test_input"]
            signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())

        dummy_registry["dummy_adapter2"] = DummyAdapter2

        adapters = find_required_adapter(["dummy_adapter.test_signal", "dummy_adapter2.test_signal2"], dummy_registry)
        assert adapters == list(set([DummyAdapter, DummyAdapter2]))

    def it_raises_key_error_if_adapter_not_found(dummy_registry):
        with pytest.raises(KeyError):
            find_required_adapter(["dummy_adapter3.test_signal"], dummy_registry)

    def it_raises_key_error_if_signal_not_found(dummy_registry):
        with pytest.raises(KeyError):
            find_required_adapter(["dummy_adapter.test_signal3"], dummy_registry)


def describe_fetch_signal():
    def it_returns_the_correct_signal(dummy_registry):
        signals = fetch_signal(["dummy_adapter.test_signal"], {"test_input": 10}, dummy_registry)
        assert signals == {"dummy_adapter.test_signal": 10}

    def it_returns_the_correct_signals_with_type_conversion(dummy_registry):
        signals = fetch_signal(["dummy_adapter.test_signal2"], {"test_input": 10}, dummy_registry)
        assert signals == {"dummy_adapter.test_signal2": "20"}

    def it_returns_the_correct_signals_with_multiple_adapters(dummy_registry):
        class DummyAdapter2(SignalAdapterBase):
            name: ClassVar[str] = "dummy_adapter2"
            required_inputs: ClassVar[List[str]] = ["test_input"]
            signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())

            def fetch(self, test_input: int) -> DummySignals:
                return DummySignals(
                    test_signal=test_input * 10,
                    test_signal2=str(test_input * 2),
                )

        dummy_registry["dummy_adapter2"] = DummyAdapter2

        signals = fetch_signal(
            ["dummy_adapter.test_signal", "dummy_adapter2.test_signal"], {"test_input": 10}, dummy_registry
        )
        assert signals == {"dummy_adapter.test_signal": 10, "dummy_adapter2.test_signal": 100}
