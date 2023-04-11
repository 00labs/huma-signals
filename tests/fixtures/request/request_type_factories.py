import datetime
from typing import Any

import factory

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
    amount: int = factory.Faker("pyint", min_value=1, max_value=1e18)
    currency: str | None = None
    amount_in_crypto: str | None = None

    @classmethod
    def create(cls, **kwargs: Any) -> dict[str, Any]:
        """
        Overrides the original `create` method to convert snake_case keys to camelCase.
        """
        obj = super().create(**kwargs)
        return {string_utils.snake_to_camel(key): value for key, value in obj.items()}
