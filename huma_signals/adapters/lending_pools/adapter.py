import json
import pathlib
from decimal import Decimal
from typing import ClassVar, List

from web3 import Web3

from huma_signals.adapters.models import SignalAdapterBase
from huma_signals.commons.chains import get_w3
from huma_signals.models import HumaBaseModel

from .settings import POOL_REGISTRY


class LendingPoolSignals(HumaBaseModel):
    # TODO: add other pool signals: utilization, liquidity, etc.
    # Pool policy signals
    pool_address: str
    apr: Decimal
    max_credit_amount: Decimal
    token_name: str
    token_symbol: str
    token_decimal: int
    interval_in_days_max: int
    interval_in_days_min: int
    invoice_amount_ratio: float
    is_testnet: bool = False


class LendingPoolAdapter(SignalAdapterBase):
    interval_in_days_max: ClassVar[int] = 90
    interval_in_days_min: ClassVar[int] = 0
    invoice_amount_ratio: ClassVar[float] = 0.8

    name: ClassVar[str] = "lending_pool"
    required_inputs: ClassVar[List[str]] = ["pool_address"]
    signals: ClassVar[List[str]] = LendingPoolSignals.__fields__.keys()

    @classmethod
    def fetch(cls, pool_address: str) -> LendingPoolSignals:
        pool_settings = POOL_REGISTRY.get(Web3.toChecksumAddress(pool_address))
        w3 = get_w3(pool_settings.chain)

        huma_pool_contract = w3.eth.contract(
            address=Web3.toChecksumAddress(pool_address),
            abi=json.load(open(pool_settings.pool_abi_path)),
        )

        pool_config_contract = w3.eth.contract(
            address=huma_pool_contract.functions.poolConfig().call(),
            abi=json.load(open(pathlib.Path(__file__).parent.resolve() / "abi" / "BasePoolConfig.json")),
        )

        pool_summary = pool_config_contract.functions.getPoolSummary().call()
        return LendingPoolSignals(
            pool_address=pool_address,
            apr=pool_summary[1],
            max_credit_amount=pool_summary[3],
            token_name=pool_summary[5],
            token_symbol=pool_summary[6],
            token_decimal=pool_summary[7],
            interval_in_days_max=cls.interval_in_days_max,
            interval_in_days_min=cls.interval_in_days_min,
            invoice_amount_ratio=cls.invoice_amount_ratio,
            is_testnet=pool_settings.chain.is_testnet(),
        )
