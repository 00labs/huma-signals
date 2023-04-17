from huma_signals.domain.clients.eth_client import eth_types
from tests.fixtures.clients.eth import eth_type_factories


class FakeEthClient:
    def __init__(
        self, transactions: list[eth_types.EthTransaction] | None = None
    ) -> None:
        self.transactions = transactions

    async def get_transactions(
        self, wallet_address: str
    ) -> list[eth_types.EthTransaction]:
        return (
            self.transactions
            if self.transactions is not None
            else eth_type_factories.EthTransactionFactory.create_batch(
                size=5, to=wallet_address
            )
        )
