"""Fee tables configuration loader."""

import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Any


def load_referral_table() -> dict[str, Any]:
    """
    Load referral fee table from config or default fixture.

    Returns a dict mapping category -> { 'rate': Decimal('0.15') }.
    """
    table_path = os.getenv("REFERRAL_FEE_TABLE", None)
    if table_path and os.path.exists(table_path):
        with open(table_path) as f:
            data = json.load(f)
    else:
        # Default to fixture for testing
        fixture_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "tests"
            / "fixtures"
            / "fee"
            / "referral_table.json"
        )
        if fixture_path.exists():
            with open(fixture_path) as f:
                data = json.load(f)
        else:
            # Fallback defaults
            data = {
                "Electronics": {"rate": 0.15},
                "Home & Kitchen": {"rate": 0.15},
                "default": {"rate": 0.15},
            }

    # Convert rates to Decimal
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict) and "rate" in value:
            result[key] = {"rate": Decimal(str(value["rate"]))}
        else:
            result[key] = value

    return result


def load_fba_table() -> dict[str, Any]:
    """
    Load FBA fee table from config or default fixture.

    Returns a dict with size tier fees.
    """
    table_path = os.getenv("FBA_FEE_TABLE", None)
    if table_path and os.path.exists(table_path):
        with open(table_path) as f:
            data = json.load(f)
    else:
        # Default to fixture for testing
        fixture_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "tests"
            / "fixtures"
            / "fee"
            / "fba_table.json"
        )
        if fixture_path.exists():
            with open(fixture_path) as f:
                data = json.load(f)
        else:
            # Fallback defaults
            data = {
                "standard": {"base": 3.22},
                "oversize": {"base": 6.10},
            }

    # Convert fees to Decimal
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict) and "base" in value:
            result[key] = {"base": Decimal(str(value["base"]))}
        else:
            result[key] = value

    return result
