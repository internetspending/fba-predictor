"""Rules engine types and data structures."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class Rule(BaseModel):
    """Individual rule definition."""

    name: Literal[
        "min_roi",
        "min_profit",
        "max_bsr",
        "min_sellers",
        "brand_allow",
        "brand_block",
        "exclude_hazmat",
    ]
    args: dict[str, Any] = Field(default_factory=dict)


class RuleSet(BaseModel):
    """Collection of rules with evaluation mode."""

    rules: list[Rule] = Field(default_factory=list)
    mode: Literal["AND", "OR"] = "AND"


class RuleOutcome(BaseModel):
    """Outcome of a single rule evaluation."""

    rule: Rule
    passed: bool
    reason: str | None = None  # machine-readable reason code


class Evaluation(BaseModel):
    """Complete rule evaluation result."""

    passed: bool
    outcomes: list[RuleOutcome]
