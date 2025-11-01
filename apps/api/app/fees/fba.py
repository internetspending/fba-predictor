"""FBA fee calculation."""

from decimal import ROUND_HALF_UP, Decimal

from apps.api.app.fees.interfaces import FeeInputs
from apps.api.app.fees.size_tiers import estimate_size_tier
from apps.api.app.fees.tables import load_fba_table


def compute_fba_fee(inp: FeeInputs) -> Decimal:
    """
    Compute FBA fee based on size tier.

    Use size tier to select a base per-unit FBA fee (simple table).

    Args:
        inp: Fee calculation inputs

    Returns:
        FBA fee as Decimal, rounded to cents
    """
    tier = estimate_size_tier(inp.dimensions)
    table = load_fba_table()
    tier_data = table.get(tier, table.get("standard", {}))
    base_fee = (
        tier_data.get("base", Decimal("3.22")) if isinstance(tier_data, dict) else Decimal("3.22")
    )

    return base_fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
