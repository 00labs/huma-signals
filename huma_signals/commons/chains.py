import enum


class Chain(enum.Enum):
    ETHEREUM = "ETHEREUM"
    GOERLI = "GOERLI"
    POLYGON = "POLYGON"
    MUMBAI = "MUMBAI"

    def chain_name(self) -> str:
        return self.name.lower()

    def is_testnet(self) -> bool:
        return self.chain_name() in ("goerli", "mumbai")
