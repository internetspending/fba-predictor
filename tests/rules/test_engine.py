"""Tests for rules engine."""

from decimal import Decimal

import pytest

from apps.api.app.rules.engine import apply_rules
from apps.api.app.rules.types import Rule, RuleSet

pytestmark = pytest.mark.m4


def test_engine_and_mode_all_pass():
    """Test AND mode when all rules pass."""
    item = {
        "roi": Decimal("0.50"),
        "net_profit": Decimal("10.00"),
        "bsr": 5000,
    }

    ruleset = RuleSet(
        mode="AND",
        rules=[
            Rule(name="min_roi", args={"threshold": 0.30}),
            Rule(name="min_profit", args={"threshold": 5.00}),
            Rule(name="max_bsr", args={"threshold": 10000}),
        ],
    )

    result = apply_rules(item, ruleset)
    assert result.passed is True
    assert len(result.outcomes) == 3
    assert all(o.passed for o in result.outcomes)


def test_engine_and_mode_one_fails():
    """Test AND mode when one rule fails."""
    item = {
        "roi": Decimal("0.20"),  # Below threshold
        "net_profit": Decimal("10.00"),
        "bsr": 5000,
    }

    ruleset = RuleSet(
        mode="AND",
        rules=[
            Rule(name="min_roi", args={"threshold": 0.30}),
            Rule(name="min_profit", args={"threshold": 5.00}),
        ],
    )

    result = apply_rules(item, ruleset)
    assert result.passed is False
    assert len(result.outcomes) == 2
    assert not result.outcomes[0].passed  # ROI failed
    assert result.outcomes[1].passed  # Profit passed


def test_engine_or_mode_one_passes():
    """Test OR mode when one rule passes (short-circuits)."""
    item = {
        "roi": Decimal("0.50"),  # Passes
        "net_profit": Decimal("3.00"),  # Fails
        "bsr": 15000,  # Fails
    }

    ruleset = RuleSet(
        mode="OR",
        rules=[
            Rule(name="min_roi", args={"threshold": 0.30}),
            Rule(name="min_profit", args={"threshold": 5.00}),
            Rule(name="max_bsr", args={"threshold": 10000}),
        ],
    )

    result = apply_rules(item, ruleset)
    assert result.passed is True
    # Should short-circuit after first pass
    assert len(result.outcomes) >= 1
    assert result.outcomes[0].passed


def test_engine_or_mode_all_fail():
    """Test OR mode when all rules fail."""
    item = {
        "roi": Decimal("0.20"),  # Fails
        "net_profit": Decimal("3.00"),  # Fails
    }

    ruleset = RuleSet(
        mode="OR",
        rules=[
            Rule(name="min_roi", args={"threshold": 0.30}),
            Rule(name="min_profit", args={"threshold": 5.00}),
        ],
    )

    result = apply_rules(item, ruleset)
    assert result.passed is False
    assert len(result.outcomes) == 2
    assert all(not o.passed for o in result.outcomes)


def test_engine_outcomes_have_reasons():
    """Test that failed outcomes include reason codes."""
    item = {
        "roi": Decimal("0.20"),
        "net_profit": Decimal("3.00"),
    }

    ruleset = RuleSet(
        mode="AND",
        rules=[
            Rule(name="min_roi", args={"threshold": 0.30}),
            Rule(name="min_profit", args={"threshold": 5.00}),
        ],
    )

    result = apply_rules(item, ruleset)
    assert result.passed is False

    # Failed outcomes should have reasons
    for outcome in result.outcomes:
        if not outcome.passed:
            assert outcome.reason is not None
            assert len(outcome.reason) > 0


def test_engine_missing_field():
    """Test engine handles missing fields gracefully."""
    item = {}  # Missing all required fields

    ruleset = RuleSet(
        mode="AND",
        rules=[
            Rule(name="min_roi", args={"threshold": 0.30}),
        ],
    )

    result = apply_rules(item, ruleset)
    assert result.passed is False
    assert len(result.outcomes) == 1
    assert not result.outcomes[0].passed
    assert result.outcomes[0].reason is not None


def test_engine_brand_allow_block():
    """Test brand allow and block rules."""
    item = {"brand": "TestBrand"}

    ruleset = RuleSet(
        mode="AND",
        rules=[
            Rule(name="brand_allow", args={"allow": ["TestBrand", "OtherBrand"]}),
            Rule(name="brand_block", args={"block": ["BlockedBrand"]}),
        ],
    )

    result = apply_rules(item, ruleset)
    assert result.passed is True
    assert all(o.passed for o in result.outcomes)


def test_engine_exclude_hazmat():
    """Test exclude_hazmat rule."""
    item = {"hazmat": False}

    ruleset = RuleSet(
        mode="AND",
        rules=[
            Rule(name="exclude_hazmat", args={}),
        ],
    )

    result = apply_rules(item, ruleset)
    assert result.passed is True

    # Test with hazmat item
    item_hazmat = {"hazmat": True}
    result_hazmat = apply_rules(item_hazmat, ruleset)
    assert result_hazmat.passed is False
