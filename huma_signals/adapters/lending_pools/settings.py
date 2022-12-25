import pathlib

from eth_typing import ChecksumAddress
from web3 import Web3

from huma_signals.commons.chains import Chain
from huma_signals.models import HumaBaseModel


class PoolSetting(HumaBaseModel):
    pool_address: ChecksumAddress
    chain: Chain
    pool_abi_path: str


_POOLS = [
    PoolSetting(
        pool_address=Web3.toChecksumAddress("0xA22D20FB0c9980fb96A9B0B5679C061aeAf5dDE4"),
        chain=Chain.GOERLI,
        pool_abi_path=str(pathlib.Path(__file__).parent.resolve() / "abi" / "BaseCreditPool.json"),
    ),
    PoolSetting(
        pool_address=Web3.toChecksumAddress("0x11672c0bBFF498c72BC2200f42461c0414855042"),
        chain=Chain.GOERLI,
        pool_abi_path=str(pathlib.Path(__file__).parent.resolve() / "abi" / "ReceivableFactoringPool.json"),
    ),
    PoolSetting(
        pool_address=Web3.toChecksumAddress("0xAb3dc5221F373Dd879BEc070058c775A0f6Af759"),
        chain=Chain.POLYGON,
        pool_abi_path=str(pathlib.Path(__file__).parent.resolve() / "abi" / "BaseCreditPool.json"),
    ),
    PoolSetting(
        pool_address=Web3.toChecksumAddress("0x58AAF1f9cB10F335111A2129273056bbED251B61"),
        chain=Chain.POLYGON,
        pool_abi_path=str(pathlib.Path(__file__).parent.resolve() / "abi" / "ReceivableFactoringPool.json"),
    ),
]


POOL_REGISTRY = {pool.pool_address: pool for pool in _POOLS}
