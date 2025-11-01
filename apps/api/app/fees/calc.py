"""Fee breakdown calculation."""

from decimal import ROUND_HALF_UP, Decimal

from apps.api.app.fees.fba import compute_fba_fee
from apps.api.app.fees.interfaces import FeeBreakdown, FeeInputs
from apps.api.app.fees.placement import compute_placement_fee
from apps.api.app.fees.referral import compute_referral_fee


def _q2(x: Decimal) -> Decimal:
    """Quantize to 2 decimal places (cents)."""
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_breakdown(inp: FeeInputs) -> FeeBreakdown:
    """
    Compute complete fee breakdown and profitability metrics.

    Args:
        inp: Fee calculation inputs

    Returns:
        Complete fee breakdown with ROI and net profit
    """
    rf = compute_referral_fee(inp)
    fba = compute_fba_fee(inp)
    pf = compute_placement_fee(inp)
    total = rf + fba + pf
    net = inp.sell_price - total - inp.buy_cost
    roi = (net / inp.buy_cost) if inp.buy_cost != 0 else Decimal("0")

    return FeeBreakdown(
        referral_fee=_q2(rf),
        fba_fee=_q2(fba),
        placement_fee=_q2(pf),
        total_fees=_q2(total),
        net_profit=_q2(net),
        roi=roi.quantize(Decimal("0.0001")),
    )
