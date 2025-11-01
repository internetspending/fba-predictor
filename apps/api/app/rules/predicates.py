"""Rule predicates for evaluating product items."""

from decimal import Decimal
from typing import Any


def min_roi(item: dict[str, Any], threshold: Decimal) -> bool:
    """
    Check if item ROI meets minimum threshold.

    Args:
        item: Product item dict with 'roi' field (Decimal)
        threshold: Minimum ROI required

    Returns:
        True if roi >= threshold, False otherwise
    """
    roi = item.get("roi")
    if roi is None:
        return False
    if isinstance(roi, int | float):
        roi = Decimal(str(roi))
    elif not isinstance(roi, Decimal):
        return False
    return roi >= threshold


def min_profit(item: dict[str, Any], threshold: Decimal) -> bool:
    """
    Check if item net profit meets minimum threshold.

    Args:
        item: Product item dict with 'net_profit' field (Decimal)
        threshold: Minimum net profit required

    Returns:
        True if net_profit >= threshold, False otherwise
    """
    profit = item.get("net_profit")
    if profit is None:
        return False
    if isinstance(profit, int | float):
        profit = Decimal(str(profit))
    elif not isinstance(profit, Decimal):
        return False
    return profit >= threshold


def max_bsr(item: dict[str, Any], threshold: int) -> bool:
    """
    Check if item BSR (Best Seller Rank) is below maximum threshold.

    Lower BSR is better, so we check bsr <= threshold.

    Args:
        item: Product item dict with 'bsr' field (int)
        threshold: Maximum BSR allowed

    Returns:
        True if bsr <= threshold, False otherwise
    """
    bsr = item.get("bsr")
    if bsr is None:
        return False
    try:
        bsr_int = int(bsr)
        return bsr_int <= threshold
    except (ValueError, TypeError):
        return False


def min_sellers(item: dict[str, Any], threshold: int) -> bool:
    """
    Check if item has minimum number of sellers.

    Args:
        item: Product item dict with 'seller_count' or 'sellers' field (int)
        threshold: Minimum number of sellers required

    Returns:
        True if seller_count >= threshold, False otherwise
    """
    sellers = item.get("seller_count") or item.get("sellers")
    if sellers is None:
        return False
    try:
        sellers_int = int(sellers)
        return sellers_int >= threshold
    except (ValueError, TypeError):
        return False


def brand_allow(item: dict[str, Any], allow: list[str]) -> bool:
    """
    Check if item brand is in allowed list.

    Args:
        item: Product item dict with 'brand' field (str)
        allow: List of allowed brand names (case-insensitive)

    Returns:
        True if brand is in allow list, False otherwise
    """
    brand = item.get("brand")
    if not brand:
        return False

    brand_clean = str(brand).strip().lower()
    allow_clean = [str(a).strip().lower() for a in allow]
    return brand_clean in allow_clean


def brand_block(item: dict[str, Any], block: list[str]) -> bool:
    """
    Check if item brand is NOT in blocked list (returns True if not blocked).

    Args:
        item: Product item dict with 'brand' field (str)
        block: List of blocked brand names (case-insensitive)

    Returns:
        True if brand is NOT in block list, False if blocked
    """
    brand = item.get("brand")
    if not brand:
        # No brand means not blocked
        return True

    brand_clean = str(brand).strip().lower()
    block_clean = [str(b).strip().lower() for b in block]
    return brand_clean not in block_clean


def exclude_hazmat(item: dict[str, Any]) -> bool:
    """
    Check if item is NOT hazardous (returns True if not hazmat).

    Args:
        item: Product item dict with 'hazmat' field (bool) or 'is_hazmat'

    Returns:
        True if item is not hazmat, False if hazmat
    """
    hazmat = item.get("hazmat") or item.get("is_hazmat") or item.get("hazardous")
    if hazmat is None:
        # No hazmat flag means assume not hazmat
        return True
    return not bool(hazmat)
