"""Normalize Keepa API responses to internal product format."""

from typing import Any


def normalize_product(keepa_json: dict[str, Any]) -> dict[str, Any]:
    """
    Map Keepa response to internal product-like dict.

    Extracts:
        - asin: Product ASIN
        - title: Product title
        - brand: Product brand (if available)
        - category: Product category (if available)
        - price_current: Current price (if available)
        - bsr: Best Seller Rank (if available)
        - dimensions: Product dimensions (if available)
        - weight: Product weight (if available)

    Args:
        keepa_json: Raw Keepa API response dict

    Returns:
        Normalized product dict with internal fields
    """
    result: dict[str, Any] = {}

    # Extract ASIN (required)
    products = keepa_json.get("products", [])
    if not products:
        return result

    product = products[0] if products else {}

    # Basic fields
    result["asin"] = product.get("asin", "")
    result["title"] = product.get("title", "")
    result["brand"] = product.get("brand", None)
    result["category"] = product.get("categoryName", None)

    # Price data (use current/last price if available)
    if "csv" in product and product["csv"]:
        # Keepa CSV format: [0] = Amazon, [1] = New, [2] = Used, etc.
        # Prices are typically in cents
        prices = product.get("csv", [])
        if len(prices) > 1 and prices[1]:
            # New price from CSV (in cents)
            price_list = prices[1]
            if price_list and len(price_list) > 0:
                last_price = price_list[-1]
                if last_price > 0:
                    result["price_current"] = last_price / 100.0  # Convert cents to dollars

    # BSR (Best Seller Rank)
    if "salesRanks" in product:
        sales_ranks = product["salesRanks"]
        if sales_ranks:
            # Get first available rank
            first_category = list(sales_ranks.keys())[0] if sales_ranks else None
            if first_category:
                rank_data = sales_ranks[first_category]
                if rank_data:
                    result["bsr"] = rank_data[-1] if rank_data else None

    # Dimensions (from product data if available)
    if "packageDimensions" in product:
        dims = product["packageDimensions"]
        if dims:
            result["dimensions"] = {
                "length": dims.get("length", None),
                "width": dims.get("width", None),
                "height": dims.get("height", None),
                "weight": dims.get("weight", None),
            }

    # Weight (if available separately)
    if "packageWeight" in product:
        result["weight"] = product["packageWeight"]
    elif "dimensions" in result and result["dimensions"]:
        result["weight"] = result["dimensions"].get("weight", None)

    # Clean up None values for optional fields (keep empty string for required)
    result = {k: v for k, v in result.items() if v is not None or k == "asin"}

    return result
