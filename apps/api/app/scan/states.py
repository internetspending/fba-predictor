"""Job state enumeration."""

from enum import Enum


class JobState(str, Enum):
    """Scan job state values."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    DLQ = "DLQ"  # dead-letter queued
