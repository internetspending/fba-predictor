"""Scan pipeline data models."""

from dataclasses import dataclass, field
from typing import Any

from apps.api.app.scan.states import JobState


@dataclass
class ScanJob:
    """Scan job representation."""

    job_id: str
    seller_id: str | None
    items: list[dict[str, Any]]  # normalized storefront items (from M3 selleramp.parse)
    attempt: int = 0
    state: JobState = JobState.QUEUED
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanResultRow:
    """Single scan result row."""

    asin: str
    kept: bool
    reason: str | None = None
    details: dict[str, Any] = field(default_factory=dict)  # e.g., fee/roi, rule outcomes
