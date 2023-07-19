import decimal
import pathlib
from typing import Any, ClassVar

import aiofiles
import orjson
import pydantic
import structlog
import web3
from huma_utils import web3_utils
from web3 import exceptions as web3_exceptions

from huma_signals import exceptions, models
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.lending_pools import registry
from huma_signals.adapters.lending_pools.settings import settings

logger = structlog.get_logger(__name__)


class LendingPoolSignals(models.HumaBaseModel):
    # TODO: add other pool signals: utilization, liquidity, etc.
    # Pool policy signals
    pool_address: str = pydantic.Field(..., description="Address of the lending pool")
    apr: int = pydantic.Field(..., description="Annual percentage rate in BPS")
    max_credit_amount: decimal.Decimal = pydantic.Field(
        ..., description="Maximum credit amount defined by the pool"
    )
    token_address: str = pydantic.Field(
        ..., description="Contract address of the token"
    )
    token_name: str = pydantic.Field(
        ..., description="Name of the token used by the pool"
    )
    token_symbol: str = pydantic.Field(
        ..., description="Symbol of the token used by the pool"
    )
    token_decimal: int = pydantic.Field(
        ..., description="Decimal of the token used by the pool"
    )
    interval_in_days_max: int = pydantic.Field(
        ..., description="Maximum payment interval in days for the pool"
    )
    interval_in_days_min: int = pydantic.Field(
        ..., description="Minimum payment interval in days for the pool"
    )
    invoice_amount_ratio: float = pydantic.Field(
        ...,
        description="For invoice factoring pool, the percentage of the payable amount the pool allow to borrow",
    )
    is_testnet: bool = pydantic.Field(
        default=False, description="Whether the pool is on testnet or not"
    )


class LendingPoolAdapter(adapter_models.SignalAdapterBase):
    # TODO: move the hard coded values to EA settings cause these are not pool setting
    interval_in_days_max: ClassVar[int] = 90
    interval_in_days_min: ClassVar[int] = 0
    invoice_amount_ratio: ClassVar[float] = 0.8

    async def fetch(  # pylint: disable=arguments-differ
        self, pool_address: str, *args: Any, **kwargs: Any
    ) -> LendingPoolSignals:
        try:
            checksum_address = web3.Web3.to_checksum_address(pool_address)
            pool_settings = registry.POOL_REGISTRY[checksum_address]
        except KeyError as e:
            message = f"Invalid pool_address {pool_address}: pool settings not found."
            logger.exception(message)
            raise exceptions.PoolSettingsNotFoundException(
                pool_address=pool_address
            ) from e

        w3 = await web3_utils.get_w3(pool_settings.chain, settings.web3_provider_url)

        async with aiofiles.open(pool_settings.pool_abi_path) as f:
            contents = await f.read()
            huma_pool_contract = w3.eth.contract(
                address=checksum_address,
                abi=orjson.loads(contents),
            )
        try:
            contract_address = await huma_pool_contract.functions.poolConfig().call()
        except web3_exceptions.Web3Exception as e:
            message = "Failed to get contract address"
            logger.exception(message)
            raise exceptions.ContractCallFailedException(message=message) from e

        async with aiofiles.open(
            pathlib.Path(__file__).parent.resolve() / "abi" / "BasePoolConfig.json",
        ) as f:
            contents = await f.read()
            pool_config_contract = w3.eth.contract(
                address=contract_address,
                abi=orjson.loads(contents),
            )

        try:
            pool_summary = await pool_config_contract.functions.getPoolSummary().call()
        except web3_exceptions.Web3Exception as e:
            message = "Failed to get pool summary"
            logger.exception(message)
            raise exceptions.ContractCallFailedException(message=message) from e

        return LendingPoolSignals(
            pool_address=pool_address,
            apr=pool_summary[1],
            max_credit_amount=pool_summary[3],
            token_address=pool_summary[0],
            token_name=pool_summary[5],
            token_symbol=pool_summary[6],
            token_decimal=pool_summary[7],
            interval_in_days_max=self.interval_in_days_max,
            interval_in_days_min=self.interval_in_days_min,
            invoice_amount_ratio=self.invoice_amount_ratio,
            is_testnet=pool_settings.chain.is_testnet(),
        )
