from __future__ import annotations

import enum


class Chain(enum.Enum):
    ETHEREUM = "ETHEREUM"
    GOERLI = "GOERLI"
    POLYGON = "POLYGON"
    LOCAL = "LOCAL"

    @staticmethod
    def from_chain_name(chain_name: str) -> Chain:
        if chain_name.lower() in ("ethereum", "mainnet", "eth", "homestead"):
            return Chain.ETHEREUM
        if chain_name.lower() in ("goerli"):
            return Chain.GOERLI
        if chain_name.lower() in ("polygon", "matic"):
            return Chain.POLYGON
        if chain_name.lower() in ("local"):
            return Chain.LOCAL
        raise ValueError(f"Unsupported chain: {chain_name}")

    def chain_name(self) -> str:
        return self.name.lower()

    def is_testnet(self) -> bool:
        return self.chain_name() in ("goerli")
