"""Parse SellerAmp CSV and JSON storefront exports."""

import csv
import io
import json
from typing import Any


def parse_csv(content: str | bytes | io.StringIO) -> list[dict[str, Any]]:
    """
    Parse SellerAmp CSV storefront export into common ingest schema.

    Schema fields:
        - asin: Product ASIN (required)
        - title: Product title (optional)
        - brand: Product brand (optional)
        - buy_cost: Purchase cost (optional)
        - notes: Additional notes (optional)

    Args:
        content: CSV content as string, bytes, or StringIO

    Returns:
        List of product dicts in ingest schema
    """
    # Handle different input types
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")  # Handle BOM
    elif isinstance(content, str):
        # Remove BOM if present
        if content.startswith("\ufeff"):
            content = content[1:]

    # Create StringIO if needed
    if isinstance(content, str):
        content = io.StringIO(content)

    results: list[dict[str, Any]] = []

    try:
        # Use DictReader to handle variable columns
        reader = csv.DictReader(content)
        for row in reader:
            # Normalize keys (strip whitespace, lowercase)
            normalized: dict[str, Any] = {}
            for key, value in row.items():
                if value is None:
                    continue
                # Strip whitespace from values
                clean_value = value.strip() if isinstance(value, str) else value
                if not clean_value:  # Skip empty values
                    continue

                key_lower = key.strip().lower()

                # Map common CSV column names to schema
                if key_lower in ("asin", "product asin", "amazon asin"):
                    normalized["asin"] = clean_value
                elif key_lower in ("title", "product title", "name", "product name"):
                    normalized["title"] = clean_value
                elif key_lower in ("brand", "manufacturer", "seller"):
                    normalized["brand"] = clean_value
                elif key_lower in ("buy cost", "cost", "price", "purchase price"):
                    # Try to parse as float
                    try:
                        normalized["buy_cost"] = float(
                            clean_value.replace("$", "").replace(",", "")
                        )
                    except (ValueError, AttributeError):
                        normalized["buy_cost"] = None
                elif key_lower in ("notes", "note", "comments", "comment"):
                    normalized["notes"] = clean_value
                else:
                    # Store other columns as-is (lowercase key)
                    normalized[key_lower] = clean_value

            # Require ASIN
            if "asin" in normalized and normalized["asin"]:
                results.append(normalized)

    except (csv.Error, UnicodeDecodeError):
        # On parse error, return empty list (or could raise, but being robust)
        return []

    return results


def parse_json(content: str | bytes) -> list[dict[str, Any]]:
    """
    Parse SellerAmp JSON storefront export into common ingest schema.

    Schema matches parse_csv() output.

    Args:
        content: JSON content as string or bytes

    Returns:
        List of product dicts in ingest schema
    """
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    try:
        data = json.loads(content)

        # Handle different JSON structures
        products: list[dict[str, Any]] = []

        # If it's a list, use directly
        if isinstance(data, list):
            products = data
        # If it's a dict with a products/items key
        elif isinstance(data, dict):
            if "products" in data:
                products = data["products"]
            elif "items" in data:
                products = data["items"]
            elif "data" in data:
                products = data["data"]
            else:
                # Assume the dict itself is a single product
                products = [data]

        # Normalize each product
        results: list[dict[str, Any]] = []
        for item in products:
            if not isinstance(item, dict):
                continue

            normalized: dict[str, Any] = {}

            # Map JSON fields to schema (case-insensitive)
            for key, value in item.items():
                if value is None:
                    continue

                key_lower = key.lower().strip()

                # Map common JSON field names
                if key_lower in ("asin", "product_asin", "amazon_asin"):
                    normalized["asin"] = str(value).strip()
                elif key_lower in ("title", "name", "product_title", "product_name"):
                    normalized["title"] = str(value).strip() if value else None
                elif key_lower in ("brand", "manufacturer", "seller"):
                    normalized["brand"] = str(value).strip() if value else None
                elif key_lower in ("buy_cost", "cost", "price", "purchase_price", "buy_price"):
                    try:
                        normalized["buy_cost"] = float(value) if value else None
                    except (ValueError, TypeError):
                        normalized["buy_cost"] = None
                elif key_lower in ("notes", "note", "comments", "comment"):
                    normalized["notes"] = str(value).strip() if value else None
                else:
                    # Preserve other fields
                    normalized[key_lower] = value

            # Require ASIN
            if "asin" in normalized and normalized["asin"]:
                results.append(normalized)

        return results

    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        # On parse error, return empty list
        return []
