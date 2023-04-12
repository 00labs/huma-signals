from typing import Any

from huma_signals.domain.clients.request_client import request_client
from tests.fixtures.request import request_type_factories


class FakeRequestClient(request_client.BaseRequestClient):
    async def get_payments(
        self,
        from_address: str | None,
        to_address: str | None,
    ) -> list[dict[str, Any]]:
        return request_type_factories.PaymentFactory.create_batch(
            size=10, from_=from_address, to=to_address
        )
