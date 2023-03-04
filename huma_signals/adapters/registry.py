from typing import Any, Dict, List, Optional, Type

from huma_signals.adapters import models
from huma_signals.adapters.allowlist import adapter as allowlist_adapter
from huma_signals.adapters.bulla_network import adapter as bulla_network_adapter
from huma_signals.adapters.ethereum_wallet import adapter as ethereum_wallet_adapter
from huma_signals.adapters.lending_pools import adapter as lending_pools_adapter
from huma_signals.adapters.polygon_wallet import adapter as polygon_wallet_adapter
from huma_signals.adapters.request_network import adapter as request_network_adapter

ADAPTER_REGISTRY: Dict[str, Type[models.SignalAdapterBase]] = {
    lending_pools_adapter.LendingPoolAdapter.name: lending_pools_adapter.LendingPoolAdapter,
    request_network_adapter.RequestNetworkInvoiceAdapter.name: request_network_adapter.RequestNetworkInvoiceAdapter,
    bulla_network_adapter.BullaNetworkInvoiceAdapter.name: bulla_network_adapter.BullaNetworkInvoiceAdapter,
    allowlist_adapter.AllowListAdapter.name: allowlist_adapter.AllowListAdapter,
    ethereum_wallet_adapter.EthereumWalletAdapter.name: ethereum_wallet_adapter.EthereumWalletAdapter,
    polygon_wallet_adapter.PolygonWalletAdapter.name: polygon_wallet_adapter.PolygonWalletAdapter,
}


def find_required_adapter(
    signal_names: List[str],
    adapter_registry: Optional[Dict[str, Type[models.SignalAdapterBase]]] = None,
) -> List[Type[models.SignalAdapterBase]]:
    """Find the adapter required to fetch the signals"""
    if adapter_registry is None:
        adapter_registry = ADAPTER_REGISTRY

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


async def fetch_signal(
    signal_names: List[str],
    adapter_inputs: Dict[str, Any],
    registry: Optional[Dict[str, Type[models.SignalAdapterBase]]] = None,
) -> Dict[str, Any]:
    """Fetch signals from the signal adapters"""
    if registry is None:
        registry = ADAPTER_REGISTRY

    adapters = find_required_adapter(signal_names, registry)
    all_signals: Dict[str, Any] = {}
    for adapter in adapters:
        inputs = {k: adapter_inputs[k] for k in adapter.required_inputs}
        signals = (await adapter().fetch(**inputs)).dict()
        all_signals |= {
            f"{adapter.name}.{signal}": value for signal, value in signals.items()
        }
    return {k: v for k, v in all_signals.items() if k in signal_names}
