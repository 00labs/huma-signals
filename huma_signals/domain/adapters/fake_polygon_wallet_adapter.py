# mypy: disable-error-code=var-annotated
from typing import Any

import factory

from huma_signals.domain.adapters.polygon_wallet import adapter


class PolygonWalletSignalsFactory(factory.Factory):
    class Meta:
        model = adapter.PolygonWalletSignals

    total_transactions = factory.LazyAttribute(  # type: ignore[misc]
        lambda s: s.total_sent + s.total_received
    )
    total_sent = factory.Faker("pyint", min_value=0)
    total_received = factory.Faker("pyint", min_value=0)
    wallet_tenure_in_days = factory.Faker("pyint", min_value=0)
    total_income_90days = factory.Faker("pyint", min_value=0)
    total_transactions_90days = factory.LazyAttribute(  # type: ignore[misc]
        lambda s: int(s.total_transactions / 2)
    )


class FakePolygonWalletAdapter(adapter.BasePolygonWalletAdapter):
    def __init__(
        self, output_signals: dict[str, adapter.PolygonWalletSignals] | None = None
    ) -> None:
        self.output_signals = output_signals or {}

    async def fetch(
        self, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> adapter.PolygonWalletSignals:
        try:
            return self.output_signals[borrower_wallet_address]
        except KeyError:
            return PolygonWalletSignalsFactory.create()
