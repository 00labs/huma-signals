import decimal

from huma_signals.commons import number_utils


def validate_amount(v: decimal.Decimal | int | float) -> decimal.Decimal:
    return number_utils.round_to_cents(v)
