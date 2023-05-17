# mypy: disable-error-code=var-annotated
import datetime
from typing import Any

import factory

from huma_signals.clients.request_client import request_types
from huma_signals.commons import string_utils
from tests.helpers import address_helpers


class PaymentFactory(factory.DictFactory):
    id = address_helpers.fake_hex_address_factory()
    contract_address = address_helpers.fake_hex_address_factory()
    token_address = address_helpers.fake_hex_address_factory()
    to = address_helpers.fake_hex_address_factory()
    from_ = address_helpers.fake_hex_address_factory()
    timestamp = factory.LazyFunction(lambda: int(datetime.datetime.now().timestamp()))
    tx_hash = address_helpers.fake_hex_address_factory()
    # mypy couldn't figure out that the faker is producing an int value and complains.
    amount: int = factory.Faker("pyint", min_value=1, max_value=1e18)  # type: ignore[assignment]
    currency: str | None = None
    amount_in_crypto: str | None = None

    @classmethod
    def create(cls, **kwargs: Any) -> dict[str, Any]:
        """
        Overrides the original `create` method to convert snake_case keys to camelCase.
        """
        obj = super().create(**kwargs)
        return {string_utils.snake_to_camel(key): value for key, value in obj.items()}


class InvoiceFactory(factory.Factory):
    class Meta:
        model = request_types.Invoice

    token_owner = address_helpers.fake_hex_address_factory()
    currency = "USDC"
    amount = factory.Faker("pydecimal")
    status = "PAID"
    payer = address_helpers.fake_hex_address_factory()
    payee = address_helpers.fake_hex_address_factory()
    creation_date: datetime.datetime = factory.Faker("date_time")  # type: ignore[assignment]
    due_date: datetime.datetime = factory.Faker("date_time")  # type: ignore[assignment]
