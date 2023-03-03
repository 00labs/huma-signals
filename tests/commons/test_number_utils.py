import decimal
from typing import Optional

import pytest

from huma_signals.commons import number_utils


def describe_round_to_cents() -> None:
    @pytest.mark.parametrize(
        "input_, expected",
        [
            (None, None),
            (decimal.Decimal("10.00"), decimal.Decimal("10.00")),
            (decimal.Decimal("10.005"), decimal.Decimal("10.01")),
            (decimal.Decimal("10.004"), decimal.Decimal("10.00")),
        ],
    )
    def it_rounds(
        input_: Optional[decimal.Decimal], expected: Optional[decimal.Decimal]
    ) -> None:
        assert number_utils.round_to_cents(input_) == expected
