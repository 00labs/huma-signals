from __future__ import annotations

import enum
import os
from typing import Optional

import web3
from web3 import middleware


class Chain(enum.Enum):
    ETHEREUM = "ETHEREUM"
    GOERLI = "GOERLI"
    POLYGON = "POLYGON"

    @staticmethod
    def from_chain_name(chain_name: str) -> Chain:
        if chain_name.lower() in ("ethereum", "mainnet", "eth"):
            return Chain.ETHEREUM
        if chain_name.lower() in ("goerli"):
            return Chain.GOERLI
        if chain_name.lower() in ("polygon", "matic"):
            return Chain.POLYGON
        raise ValueError(f"Unsupported chain: {chain_name}")

    def chain_name(self) -> str:
        return self.name.lower()

    def is_testnet(self) -> bool:
        return self.chain_name() in ("goerli")


def get_w3(chain: Chain, alchemy_key: Optional[str] = None) -> web3.Web3:
    """Get a web3 instance for the given chain

    Parameters
    ----------
    chain : Chain
        the chain to connect to
    alchemy_key : str, optional
        the alchemy_key to connect to the chain with, by default None
        when set to None, function will try to get from env

    Returns
    -------
    Web3
        the web3 instance
    """
    if not alchemy_key:
        # Try to get from env
        alchemy_key = os.getenv(f"ALCHEMY_KEY_{chain.name.upper()}")

    if not alchemy_key:
        raise ValueError(f"Alchemy key not set for chain: {chain}")

    if chain == Chain.ETHEREUM:
        return web3.Web3(
            web3.Web3.HTTPProvider(
                f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}"
            )
        )
    if chain == Chain.POLYGON:
        return web3.Web3(
            web3.Web3.HTTPProvider(
                f"https://polygon-mainnet.g.alchemy.com/v2/{alchemy_key}"
            )
        )
    if chain == Chain.GOERLI:
        w3 = web3.Web3(
            web3.Web3.HTTPProvider(f"https://eth-goerli.g.alchemy.com/v2/{alchemy_key}")
        )
        w3.middleware_onion.inject(middleware.geth_poa_middleware, layer=0)
        return w3

    raise ValueError(f"Unsupported chain: {chain}")
