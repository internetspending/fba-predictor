"""Referral fee calculation."""

from decimal import ROUND_HALF_UP, Decimal

from apps.api.app.fees.interfaces import FeeInputs
from apps.api.app.fees.tables import load_referral_table

# Default referral rate (15%)
DEFAULT_REFERRAL_RATE = Decimal("0.15")


def compute_referral_fee(inp: FeeInputs) -> Decimal:
    """
    Compute referral fee based on category and sell price.

    Look up category. If missing, default rate (e.g., 15%).
    fee = rate * sell_price

    Args:
        inp: Fee calculation inputs

    Returns:
        Referral fee as Decimal, rounded to cents
    """
    table = load_referral_table()
    category_data = table.get(inp.category, table.get("default", {}))
    rate = (
        category_data.get("rate", DEFAULT_REFERRAL_RATE)
        if isinstance(category_data, dict)
        else DEFAULT_REFERRAL_RATE
    )

    fee = rate * inp.sell_price
    return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
