from typing import Any, Dict, List

from .lending_pools.adapter import LendingPoolAdapter
from .models import SignalAdapterBase

ADAPTER_REGISTRY = {LendingPoolAdapter.name: LendingPoolAdapter}
