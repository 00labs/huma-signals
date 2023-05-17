import pathlib

import eth_typing
import web3

from huma_signals import models
from huma_signals.commons import chains


class PoolSetting(models.HumaBaseModel):
    pool_address: eth_typing.ChecksumAddress
    chain: chains.Chain
    pool_abi_path: str


_POOLS = [
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0xA22D20FB0c9980fb96A9B0B5679C061aeAf5dDE4"
        ),
        chain=chains.Chain.GOERLI,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve() / "abi" / "BaseCreditPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0x11672c0bBFF498c72BC2200f42461c0414855042"
        ),
        chain=chains.Chain.GOERLI,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve()
            / "abi"
            / "ReceivableFactoringPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0x423Dbc7B52DB033bE5630c0521A43F4aFeDe275A"
        ),
        chain=chains.Chain.MUMBAI,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve()
            / "abi"
            / "SuperfluidFactoringPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0xAb3dc5221F373Dd879BEc070058c775A0f6Af759"
        ),
        chain=chains.Chain.POLYGON,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve() / "abi" / "BaseCreditPool.json"
        ),
    ),
    PoolSetting(
        pool_address=web3.Web3.to_checksum_address(
            "0x58AAF1f9cB10F335111A2129273056bbED251B61"
        ),
        chain=chains.Chain.POLYGON,
        pool_abi_path=str(
            pathlib.Path(__file__).parent.resolve()
            / "abi"
            / "ReceivableFactoringPool.json"
        ),
    ),
]


POOL_REGISTRY = {pool.pool_address: pool for pool in _POOLS}
