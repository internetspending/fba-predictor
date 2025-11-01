"""Placement fee calculation."""

from decimal import ROUND_HALF_UP, Decimal

from apps.api.app.core.feature_flags import is_placement_enabled
from apps.api.app.fees.interfaces import FeeInputs

# Default placement fee (if enabled)
DEFAULT_PLACEMENT_FEE = Decimal("0.50")


def compute_placement_fee(inp: FeeInputs) -> Decimal:
    """
    Compute placement fee if feature is enabled.

    If feature disabled -> Decimal('0.00').
    Else compute a flat placement fee.

    Args:
        inp: Fee calculation inputs

    Returns:
        Placement fee as Decimal, rounded to cents
    """
    if not is_placement_enabled():
        return Decimal("0.00")

    return DEFAULT_PLACEMENT_FEE.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
