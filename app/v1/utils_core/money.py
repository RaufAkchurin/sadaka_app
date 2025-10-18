from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

MINOR_UNITS_IN_RUBLE = Decimal("100")


def _to_decimal(value: int | float | str | Decimal) -> Decimal:
    """
    Convert arbitrary numeric input to Decimal without losing precision.
    Strings are preferred for floats to avoid binary drift.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, str)):
        return Decimal(value)
    # for floats fall back to str representation to keep original value
    return Decimal(str(value))


def rub_to_kopecks(value: int | float | str | Decimal) -> int:
    """
    Convert ruble amount to kopecks with bankers rounding.
    """
    dec_value = _to_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int((dec_value * MINOR_UNITS_IN_RUBLE).to_integral_value(rounding=ROUND_HALF_UP))


def kopecks_to_rub(value: int | float | str | Decimal) -> Decimal:
    """
    Convert kopeck amount to rubles and keep two fractional digits precision.
    """
    dec_value = _to_decimal(value)
    return (dec_value / MINOR_UNITS_IN_RUBLE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

