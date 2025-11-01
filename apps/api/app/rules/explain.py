"""Human-readable explanation generator for rule evaluations."""

from apps.api.app.rules.types import Evaluation


def to_human_readable(ev: Evaluation) -> str:
    """
    Create concise English explanation for rule evaluation.

    For failures: list failing rules with thresholds and observed values.
    For success: summarize strongest reasons (e.g., ROI X >= min Y).

    Args:
        ev: Evaluation result

    Returns:
        Human-readable explanation string
    """
    if ev.passed:
        return _explain_success(ev)
    else:
        return _explain_failure(ev)


def _explain_success(ev: Evaluation) -> str:
    """Generate success explanation."""
    passed_rules = [o for o in ev.outcomes if o.passed]

    if not passed_rules:
        return "No rules evaluated."

    reasons = []
    for outcome in passed_rules:
        rule = outcome.rule
        args = rule.args

        if rule.name == "min_roi":
            roi = args.get("threshold", "N/A")
            reasons.append(f"ROI meets minimum ({roi})")
        elif rule.name == "min_profit":
            profit = args.get("threshold", "N/A")
            reasons.append(f"Net profit meets minimum (${profit})")
        elif rule.name == "max_bsr":
            bsr = args.get("threshold", "N/A")
            reasons.append(f"BSR within acceptable range (≤ {bsr})")
        elif rule.name == "min_sellers":
            sellers = args.get("threshold", "N/A")
            reasons.append(f"Sufficient sellers (≥ {sellers})")
        elif rule.name == "brand_allow":
            reasons.append("Brand is allowed")
        elif rule.name == "brand_block":
            reasons.append("Brand is not blocked")
        elif rule.name == "exclude_hazmat":
            reasons.append("Item is not hazmat")

    return f"Passed: {', '.join(reasons)}"


def _explain_failure(ev: Evaluation) -> str:
    """Generate failure explanation."""
    failed_rules = [o for o in ev.outcomes if not o.passed]

    if not failed_rules:
        return "Evaluation failed (no rules passed)."

    reasons = []
    for outcome in failed_rules:
        if outcome.reason:
            reasons.append(outcome.reason)
        else:
            reasons.append(f"Rule '{outcome.rule.name}' failed")

    return f"Failed: {', '.join(reasons)}"
