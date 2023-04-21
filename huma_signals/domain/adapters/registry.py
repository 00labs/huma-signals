from typing import Any, Type

from huma_signals.domain.adapters import models
from huma_signals.domain.adapters.allowlist import adapter as allowlist_adapter
from huma_signals.domain.adapters.ethereum_wallet import (
    adapter as ethereum_wallet_adapter,
)
from huma_signals.domain.adapters.lending_pools import adapter as lending_pools_adapter
from huma_signals.domain.adapters.polygon_wallet import (
    adapter as polygon_wallet_adapter,
)
from huma_signals.domain.adapters.request_network import (
    request_invoice_adapter,
    request_transaction_adapter,
)

ADAPTER_REGISTRY: dict[str, Type[models.SignalAdapterBase]] = {
    lending_pools_adapter.LendingPoolAdapter.name: lending_pools_adapter.LendingPoolAdapter,
    request_invoice_adapter.RequestInvoiceAdapter.name: request_invoice_adapter.RequestInvoiceAdapter,
    request_transaction_adapter.RequestTransactionAdapter.name: request_transaction_adapter.RequestTransactionAdapter,
    allowlist_adapter.AllowListAdapter.name: allowlist_adapter.AllowListAdapter,
    ethereum_wallet_adapter.EthereumWalletAdapter.name: ethereum_wallet_adapter.EthereumWalletAdapter,
    polygon_wallet_adapter.PolygonWalletAdapter.name: polygon_wallet_adapter.PolygonWalletAdapter,
}


def find_required_adapter(
    signal_names: list[str],
    adapter_registry: dict[str, Type[models.SignalAdapterBase]] | None = None,
) -> list[Type[models.SignalAdapterBase]]:
    """Find the adapter required to fetch the signals"""
    if adapter_registry is None:
        adapter_registry = ADAPTER_REGISTRY

    adapters = set()
    for signal_name in signal_names:
        adapter_name = signal_name.split(".")[0]
        adapter = adapter_registry.get(adapter_name)
        if adapter is None:
            raise KeyError(f"Signal Adapter {adapter_name} not found in registry")
        if signal_name.split(".")[1] not in adapter.signals:
            raise KeyError(f"Signal {signal_name} not found in adapter {adapter_name}")
        adapters.add(adapter_registry[adapter_name])

    return list(adapters)


async def fetch_signal(
    signal_names: list[str],
    adapter_inputs: dict[str, Any],
    registry: dict[str, Type[models.SignalAdapterBase]] | None = None,
) -> dict[str, Any]:
    """Fetch signals from the signal adapters"""
    if registry is None:
        registry = ADAPTER_REGISTRY

    adapters = find_required_adapter(signal_names, registry)
    all_signals: dict[str, Any] = {}
    for adapter in adapters:
        inputs = {k: adapter_inputs[k] for k in adapter.required_inputs}
        signals = (await adapter().fetch(**inputs)).dict()
        all_signals |= {
            f"{adapter.name}.{signal}": value for signal, value in signals.items()
        }
    return {k: v for k, v in all_signals.items() if k in signal_names}
