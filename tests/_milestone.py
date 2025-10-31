"""Milestone helper for test marking and unlocking."""

import os

import pytest

ACTIVE = int(os.getenv("CURRENT_MILESTONE", "2") or "2")


def unlocked(n: int) -> bool:
    """Check if milestone n is unlocked."""
    return ACTIVE >= n


xfuture = pytest.mark.xfail(reason="Future milestone locked", strict=False)
