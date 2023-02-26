import decimal

import pytest

from huma_signals.commons import pydantic_utils


def describe_validate_amount() -> None:
    @pytest.mark.parametrize(
        "input_, expected",
        [
            (decimal.Decimal("10.00"), decimal.Decimal("10.00")),
            (decimal.Decimal("10.005"), decimal.Decimal("10.01")),
            (decimal.Decimal("10.004"), decimal.Decimal("10.00")),
            (10, decimal.Decimal("10.00")),
            (10.00, decimal.Decimal("10.00")),
            (10.005, decimal.Decimal("10.01")),
            (10.004, decimal.Decimal("10.00")),
        ],
    )
    def it_transforms_the_amount(
        input_: decimal.Decimal | int | float,
        expected: decimal.Decimal,
    ) -> None:
        assert pydantic_utils.validate_amount(input_) == expected
