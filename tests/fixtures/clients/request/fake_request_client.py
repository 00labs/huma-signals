from typing import Any

from huma_signals.clients.request_client import request_client, request_types
from tests.fixtures.clients.request import request_type_factories


class FakeRequestClient(request_client.BaseRequestClient):
    def __init__(self, invoice: request_types.Invoice | None = None) -> None:
        self.invoice = invoice

    async def get_payments(
        self,
        from_address: str | None,
        to_address: str | None,
    ) -> list[dict[str, Any]]:
        return request_type_factories.PaymentFactory.create_batch(
            size=10, from_=from_address, to=to_address
        )

    async def get_invoice(self, request_id: str) -> request_types.Invoice:
        return self.invoice or request_type_factories.InvoiceFactory.create()
