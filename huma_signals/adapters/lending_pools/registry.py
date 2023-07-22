import pathlib

import eth_typing
import web3
from huma_utils import chain_utils

from huma_signals import models


class PoolSetting(models.HumaBaseModel):
    pool_address: eth_typing.ChecksumAddress
    chain: chain_utils.Chain
    pool_abi_path: str


_POOLS = [
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0xA22D20FB0c9980fb96A9B0B5679C061aeAf5dDE4"
        ),
        chain=chain_utils.Chain.GOERLI,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve() / "abi" / "BaseCreditPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0x11672c0bBFF498c72BC2200f42461c0414855042"
        ),
        chain=chain_utils.Chain.GOERLI,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve()
            / "abi"
            / "ReceivableFactoringPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0x91bd14A985AD18f63E3380ac2510EC6e24eAE687"
        ),
        chain=chain_utils.Chain.GOERLI,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve()
            / "abi"
            / "ReceivableFactoringPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0xC08AC7Ba5E8633ac6398C317dF1CEBED3A313c8A"
        ),
        chain=chain_utils.Chain.MUMBAI,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve()
            / "abi"
            / "ReceivableFactoringPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0xAb3dc5221F373Dd879BEc070058c775A0f6Af759"
        ),
        chain=chain_utils.Chain.POLYGON,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve() / "abi" / "BaseCreditPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0x58AAF1f9cB10F335111A2129273056bbED251B61"
        ),
        chain=chain_utils.Chain.POLYGON,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve()
            / "abi"
            / "ReceivableFactoringPool.json"
        ),
    ),
]


POOL_REGISTRY = {pool.pool_address: pool for pool in _POOLS}
