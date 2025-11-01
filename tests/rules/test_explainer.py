"""Tests for human-readable explainer."""

import pytest

from apps.api.app.rules.explain import to_human_readable
from apps.api.app.rules.types import Evaluation, Rule, RuleOutcome

pytestmark = pytest.mark.m4


def test_explainer_success_single():
    """Test explainer for successful evaluation with single rule."""
    outcome = RuleOutcome(
        rule=Rule(name="min_roi", args={"threshold": 0.30}), passed=True, reason=None
    )
    ev = Evaluation(passed=True, outcomes=[outcome])

    explanation = to_human_readable(ev)
    assert "Passed" in explanation
    assert "ROI" in explanation


def test_explainer_success_multiple():
    """Test explainer for successful evaluation with multiple rules."""
    outcomes = [
        RuleOutcome(rule=Rule(name="min_roi", args={"threshold": 0.30}), passed=True),
        RuleOutcome(rule=Rule(name="min_profit", args={"threshold": 5.00}), passed=True),
        RuleOutcome(rule=Rule(name="max_bsr", args={"threshold": 10000}), passed=True),
    ]
    ev = Evaluation(passed=True, outcomes=outcomes)

    explanation = to_human_readable(ev)
    assert "Passed" in explanation
    assert "ROI" in explanation
    assert "Net profit" in explanation or "profit" in explanation.lower()
    assert "BSR" in explanation


def test_explainer_failure_single():
    """Test explainer for failed evaluation with single rule."""
    outcome = RuleOutcome(
        rule=Rule(name="min_roi", args={"threshold": 0.30}),
        passed=False,
        reason="ROI 0.20 < 0.30",
    )
    ev = Evaluation(passed=False, outcomes=[outcome])

    explanation = to_human_readable(ev)
    assert "Failed" in explanation
    assert "ROI" in explanation
    assert "0.20" in explanation or "0.30" in explanation


def test_explainer_failure_multiple():
    """Test explainer for failed evaluation with multiple rules."""
    outcomes = [
        RuleOutcome(
            rule=Rule(name="min_roi", args={"threshold": 0.30}),
            passed=False,
            reason="ROI 0.20 < 0.30",
        ),
        RuleOutcome(
            rule=Rule(name="min_profit", args={"threshold": 5.00}),
            passed=False,
            reason="Net profit 3.00 < 5.00",
        ),
    ]
    ev = Evaluation(passed=False, outcomes=outcomes)

    explanation = to_human_readable(ev)
    assert "Failed" in explanation
    assert "ROI" in explanation or "profit" in explanation.lower()


def test_explainer_no_rules():
    """Test explainer when no rules evaluated."""
    ev = Evaluation(passed=False, outcomes=[])

    explanation = to_human_readable(ev)
    assert (
        "No rules" in explanation
        or "no rules" in explanation.lower()
        or "failed" in explanation.lower()
    )


def test_explainer_brand_rules():
    """Test explainer for brand-related rules."""
    outcomes = [
        RuleOutcome(rule=Rule(name="brand_allow", args={"allow": ["TestBrand"]}), passed=True),
        RuleOutcome(rule=Rule(name="brand_block", args={"block": ["BlockedBrand"]}), passed=True),
    ]
    ev = Evaluation(passed=True, outcomes=outcomes)

    explanation = to_human_readable(ev)
    assert "Passed" in explanation
    assert "brand" in explanation.lower()


def test_explainer_hazmat_rule():
    """Test explainer for hazmat exclusion rule."""
    outcomes = [
        RuleOutcome(rule=Rule(name="exclude_hazmat", args={}), passed=True),
    ]
    ev = Evaluation(passed=True, outcomes=outcomes)

    explanation = to_human_readable(ev)
    assert "Passed" in explanation
    assert "hazmat" in explanation.lower() or "not hazmat" in explanation.lower()
