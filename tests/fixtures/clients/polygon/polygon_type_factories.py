# mypy: disable-error-code=var-annotated
from typing import Any

import factory

from huma_signals.domain.clients.polygon_client import polygon_types
from tests.helpers import address_helpers


class PolygonTransactionFactory(factory.Factory):
    class Meta:
        model = polygon_types.PolygonTransaction

    block_number = factory.Faker("pyint")
    time_stamp = factory.Faker("unix_time")
    hash = address_helpers.fake_hex_address_factory()
    nonce = factory.Faker("pyint")
    block_hash = address_helpers.fake_hex_address_factory()
    transaction_index = factory.Faker("pyint")
    from_ = address_helpers.fake_hex_address_factory()
    to = address_helpers.fake_hex_address_factory()
    value = factory.Faker("pyint", max_value=1e27)
    gas = factory.Faker("pyint")
    gas_price = factory.Faker("pyint", max_value=1e27)
    is_error = factory.Faker("pybool")
    txreceipt_status = ""
    input = address_helpers.fake_hex_address_factory()
    contract_address = ""
    cumulative_gas_used = factory.Faker("pyint", max_value=500000)
    gas_used = factory.Faker("pyint", max_value=500000)
    confirmations = factory.Faker("pyint", max_value=500000)
    method_id = address_helpers.fake_hex_address_factory(length=8)
    function_name = ""

    @classmethod
    def create(cls, **kwargs: Any) -> polygon_types.PolygonTransaction:
        """
        Overrides the original `create` method to convert snake_case keys to camelCase.
        """
        obj = super().create(**kwargs)
        return polygon_types.PolygonTransaction(
            **{k: str(v) for k, v in obj.dict(by_alias=True).items()}
        )


class PolygonTransactionResponseFactory(factory.Factory):
    class Meta:
        model = polygon_types.PolygonTransactionResponse

    status = "0"
    message = "OK"
    result = factory.List(
        [factory.SubFactory(PolygonTransactionFactory) for _ in range(5)]
    )

    class Params:
        failed = factory.Trait(status="1", message="error", result=[])
