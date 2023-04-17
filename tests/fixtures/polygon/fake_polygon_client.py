from huma_signals.domain.clients.polygon_client import polygon_types
from tests.fixtures.polygon import polygon_type_factories


class FakePolygonClient:
    def __init__(
        self, transactions: list[polygon_types.PolygonTransaction] | None = None
    ) -> None:
        self.transactions = transactions

    async def get_transactions(
        self, wallet_address: str
    ) -> list[polygon_types.PolygonTransaction]:
        return (
            self.transactions
            if self.transactions is not None
            else polygon_type_factories.PolygonTransactionFactory.create_batch(
                size=5, to=wallet_address
            )
        )
