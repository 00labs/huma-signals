import decimal
from typing import Optional, overload


@overload
def round_to_cents(value: None) -> None:
    pass


@overload
def round_to_cents(value: decimal.Decimal | float | int) -> decimal.Decimal:
    pass


def round_to_cents(
    value: Optional[decimal.Decimal | float | int],
) -> Optional[decimal.Decimal]:
    if value is None:
        return None

    return decimal.Decimal(value).quantize(
        decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP
    )
