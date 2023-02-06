from typing import ClassVar, Dict, List, Type

import pytest

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters import registry


class DummySignals(models.HumaBaseModel):
    test_signal: int
    test_signal2: str


class DummyAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "dummy_adapter"
    required_inputs: ClassVar[List[str]] = ["test_input"]
    signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())

    async def fetch(self, test_input: int) -> DummySignals:
        return DummySignals(
            test_signal=test_input,
            test_signal2=str(test_input * 2),
        )


@pytest.fixture
def dummy_registry() -> Dict[str, Type[adapter_models.SignalAdapterBase]]:
    return {"dummy_adapter": DummyAdapter}


def describe_ADAPTER_REGISTRY() -> None:
    assert registry.ADAPTER_REGISTRY is not None
    assert issubclass(
        list(registry.ADAPTER_REGISTRY.values())[0], adapter_models.SignalAdapterBase
    )


def describe_find_required_adapter() -> None:
    def it_returns_the_correct_adapter(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        adapters = registry.find_required_adapter(
            ["dummy_adapter.test_signal"], dummy_registry
        )
        assert adapters == [DummyAdapter]

    def it_returns_the_correct_adapter_with_multiple_signals(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        adapters = registry.find_required_adapter(
            ["dummy_adapter.test_signal", "dummy_adapter.test_signal2"], dummy_registry
        )
        assert adapters == [DummyAdapter]

    def it_returns_the_correct_adapter_with_multiple_adapters(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        class DummyAdapter2(adapter_models.SignalAdapterBase):
            name: ClassVar[str] = "dummy_adapter2"
            required_inputs: ClassVar[List[str]] = ["test_input"]
            signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())

        dummy_registry["dummy_adapter2"] = DummyAdapter2

        adapters = registry.find_required_adapter(
            ["dummy_adapter.test_signal", "dummy_adapter2.test_signal2"], dummy_registry
        )
        assert adapters == list({DummyAdapter, DummyAdapter2})

    def it_raises_key_error_if_adapter_not_found(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        with pytest.raises(KeyError):
            registry.find_required_adapter(
                ["dummy_adapter3.test_signal"], dummy_registry
            )

    def it_raises_key_error_if_signal_not_found(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        with pytest.raises(KeyError):
            registry.find_required_adapter(
                ["dummy_adapter.test_signal3"], dummy_registry
            )


def describe_adapter_registry() -> None:
    def all_adapters_are_subclasses_of_signal_adapter_base() -> None:
        assert all(
            [
                issubclass(adapter, adapter_models.SignalAdapterBase)
                for adapter in registry.ADAPTER_REGISTRY.values()
            ]
        )

    def all_adapters_have_a_name() -> None:
        assert all(
            [hasattr(adapter, "name") for adapter in registry.ADAPTER_REGISTRY.values()]
        )
        assert all(
            [
                isinstance(adapter.name, str)
                for adapter in registry.ADAPTER_REGISTRY.values()
            ]
        )

    def all_adapters_have_required_inputs() -> None:
        assert all(
            [
                hasattr(adapter, "required_inputs")
                for adapter in registry.ADAPTER_REGISTRY.values()
            ]
        )
        assert all(
            [
                isinstance(adapter.required_inputs, list)
                for adapter in registry.ADAPTER_REGISTRY.values()
            ]
        )

    def all_adapters_have_signals() -> None:
        assert all(
            [
                hasattr(adapter, "signals")
                for adapter in registry.ADAPTER_REGISTRY.values()
            ]
        )
        assert all(
            [
                isinstance(adapter.signals, list)
                for adapter in registry.ADAPTER_REGISTRY.values()
            ]
        )


def describe_fetch_signal() -> None:
    async def it_returns_the_correct_signal(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        signals = await registry.fetch_signal(
            ["dummy_adapter.test_signal"], {"test_input": 10}, dummy_registry
        )
        assert signals == {"dummy_adapter.test_signal": 10}

    async def it_returns_the_correct_signals_with_type_conversion(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        signals = await registry.fetch_signal(
            ["dummy_adapter.test_signal2"], {"test_input": 10}, dummy_registry
        )
        assert signals == {"dummy_adapter.test_signal2": "20"}

    async def it_returns_the_correct_signals_with_multiple_adapters(
        dummy_registry: Dict[str, Type[adapter_models.SignalAdapterBase]]
    ) -> None:
        class DummyAdapter2(adapter_models.SignalAdapterBase):
            name: ClassVar[str] = "dummy_adapter2"
            required_inputs: ClassVar[List[str]] = ["test_input"]
            signals: ClassVar[List[str]] = list(DummySignals.__fields__.keys())

            @classmethod
            async def fetch(cls, test_input: int) -> DummySignals:
                return DummySignals(
                    test_signal=test_input * 10,
                    test_signal2=str(test_input * 2),
                )

        dummy_registry["dummy_adapter2"] = DummyAdapter2

        signals = await registry.fetch_signal(
            ["dummy_adapter.test_signal", "dummy_adapter2.test_signal"],
            {"test_input": 10},
            dummy_registry,
        )
        assert signals == {
            "dummy_adapter.test_signal": 10,
            "dummy_adapter2.test_signal": 100,
        }
