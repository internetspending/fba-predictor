"""Fee calculation interfaces and data structures."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Dimensions:
    """Product dimensions."""

    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal
    weight_kg: Decimal | None = None


@dataclass(frozen=True)
class FeeInputs:
    """Inputs for fee calculation."""

    category: str
    sell_price: Decimal  # final sale price on Amazon
    buy_cost: Decimal  # acquisition cost
    dimensions: Dimensions | None = None


@dataclass(frozen=True)
class FeeBreakdown:
    """Complete fee breakdown and profitability metrics."""

    referral_fee: Decimal
    fba_fee: Decimal
    placement_fee: Decimal
    total_fees: Decimal
    net_profit: Decimal  # sell_price - total_fees - buy_cost
    roi: Decimal  # net_profit / buy_cost (0 if buy_cost == 0)
