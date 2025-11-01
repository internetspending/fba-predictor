"""Size tier estimation for FBA fee calculation."""

from decimal import Decimal
from typing import Literal

from apps.api.app.fees.interfaces import Dimensions

SizeTier = Literal["standard", "oversize"]

# Thresholds for size tier determination
MAX_LENGTH_CM = Decimal("45")
MAX_WIDTH_CM = Decimal("45")
MAX_HEIGHT_CM = Decimal("35")
MAX_WEIGHT_KG = Decimal("1.8")


def estimate_size_tier(dim: Dimensions | None) -> SizeTier:
    """
    Estimate size tier based on dimensions and weight.

    If any dimension > threshold or weight_kg > threshold => 'oversize', else 'standard'.

    Args:
        dim: Product dimensions (optional)

    Returns:
        'standard' or 'oversize'
    """
    if dim is None:
        return "standard"

    # Check dimension thresholds
    if (
        dim.length_cm > MAX_LENGTH_CM
        or dim.width_cm > MAX_WIDTH_CM
        or dim.height_cm > MAX_HEIGHT_CM
    ):
        return "oversize"

    # Check weight threshold
    if dim.weight_kg is not None and dim.weight_kg > MAX_WEIGHT_KG:
        return "oversize"

    return "standard"
