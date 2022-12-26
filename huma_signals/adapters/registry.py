from typing import Any, Dict, List

from .lending_pools.adapter import LendingPoolAdapter
from .models import SignalAdapterBase

ADAPTER_REGISTRY = {LendingPoolAdapter.name: LendingPoolAdapter}


def find_required_adapter(
    signal_names: List[str], adapter_registry: Dict[str, SignalAdapterBase] = ADAPTER_REGISTRY
) -> List[SignalAdapterBase]:
    """Find the adapter required to fetch the signals"""
    adapters = []
    for signal_name in signal_names:
        adapter_name = signal_name.split(".")[0]
        adapter = adapter_registry.get(adapter_name)
        if adapter is None:
            raise KeyError(f"Signal Adapter {adapter_name} not found in registry")
        if signal_name.split(".")[1] not in adapter.signals:
            raise KeyError(f"Signal {signal_name} not found in adapter {adapter_name}")
        adapters.append(adapter_registry[adapter_name])
    return list(set(adapters))


def fetch_signal(
    signal_names: List[str], adapter_inputs: Dict[str, Any], registry: Dict[str, SignalAdapterBase] = ADAPTER_REGISTRY
) -> Dict[str, Any]:
    """Fetch signals from the signal adapters"""
    adapters = find_required_adapter(signal_names, registry)
    all_signals = {}
    for adapter in adapters:
        inputs = {k: adapter_inputs[k] for k in adapter.required_inputs}
        signals = adapter().fetch(**inputs).dict()
        all_signals |= {f"{adapter.name}.{signal}": value for signal, value in signals.items()}
    return {k: v for k, v in all_signals.items() if k in signal_names}
