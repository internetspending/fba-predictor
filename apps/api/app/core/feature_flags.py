"""Feature flags for optional functionality."""

import os


def is_placement_enabled() -> bool:
    """Check if placement fee is enabled via environment variable."""
    return os.getenv("PLACEMENT_FEE_ENABLED", "false").lower() in ("1", "true", "yes", "y")
