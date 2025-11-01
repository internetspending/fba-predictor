"""Rules engine for evaluating product items against rule sets."""

from decimal import Decimal
from typing import Any

from apps.api.app.rules import predicates as P
from apps.api.app.rules.types import Evaluation, Rule, RuleOutcome, RuleSet


def apply_rules(item: dict[str, Any], ruleset: RuleSet) -> Evaluation:
    """
    Evaluate rules in order, short-circuit depending on mode.

    Args:
        item: Product item dict (must include computed net_profit and roi from fee calculator)
        ruleset: Rule set to evaluate

    Returns:
        Evaluation with per-rule outcomes (passed + reason code when failed)
    """
    outcomes: list[RuleOutcome] = []
    all_passed = True

    for rule in ruleset.rules:
        outcome = _evaluate_rule(item, rule)

        outcomes.append(outcome)

        if outcome.passed:
            if ruleset.mode == "OR":
                # Short-circuit on first pass in OR mode
                return Evaluation(passed=True, outcomes=outcomes)
        else:
            all_passed = False
            if ruleset.mode == "AND":
                # Short-circuit on first fail in AND mode
                # Continue to collect all outcomes, but mark as failed
                pass

    # In AND mode, all must pass; in OR mode, at least one must pass
    final_passed = all_passed if ruleset.mode == "AND" else any(o.passed for o in outcomes)

    return Evaluation(passed=final_passed, outcomes=outcomes)


def _evaluate_rule(item: dict[str, Any], rule: Rule) -> RuleOutcome:
    """Evaluate a single rule against an item."""
    args = rule.args
    name = rule.name

    try:
        if name == "min_roi":
            threshold = args.get("threshold", 0)
            threshold_decimal = Decimal(str(threshold))
            passed = P.min_roi(item, threshold_decimal)
            reason = None if passed else f"ROI {item.get('roi', 'N/A')} < {threshold_decimal}"

        elif name == "min_profit":
            threshold = args.get("threshold", 0)
            threshold_decimal = Decimal(str(threshold))
            passed = P.min_profit(item, threshold_decimal)
            reason = (
                None
                if passed
                else f"Net profit {item.get('net_profit', 'N/A')} < {threshold_decimal}"
            )

        elif name == "max_bsr":
            threshold = args.get("threshold", 999999)
            threshold_int = int(threshold)
            passed = P.max_bsr(item, threshold_int)
            reason = None if passed else f"BSR {item.get('bsr', 'N/A')} > {threshold_int}"

        elif name == "min_sellers":
            threshold = args.get("threshold", 0)
            threshold_int = int(threshold)
            passed = P.min_sellers(item, threshold_int)
            reason = (
                None
                if passed
                else f"Sellers {item.get('seller_count', item.get('sellers', 'N/A'))} < {threshold_int}"
            )

        elif name == "brand_allow":
            allow_list = args.get("allow", [])
            passed = P.brand_allow(item, allow_list)
            reason = None if passed else f"Brand '{item.get('brand', 'N/A')}' not in allowed list"

        elif name == "brand_block":
            block_list = args.get("block", [])
            passed = P.brand_block(item, block_list)
            reason = None if passed else f"Brand '{item.get('brand', 'N/A')}' is blocked"

        elif name == "exclude_hazmat":
            passed = P.exclude_hazmat(item)
            reason = None if passed else "Item is marked as hazmat"

        else:
            passed = False
            reason = f"Unknown rule: {name}"

    except (KeyError, ValueError, TypeError, AttributeError) as e:
        # Missing field or invalid value
        passed = False
        reason = f"Rule evaluation error: {str(e)}"

    return RuleOutcome(rule=rule, passed=passed, reason=reason)
