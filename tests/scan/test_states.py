"""Tests for job states."""

import pytest

from apps.api.app.scan.states import JobState

pytestmark = pytest.mark.m5


def test_job_state_enum_values():
    """Test that all expected job states exist."""
    assert JobState.QUEUED == "QUEUED"
    assert JobState.RUNNING == "RUNNING"
    assert JobState.SUCCEEDED == "SUCCEEDED"
    assert JobState.FAILED == "FAILED"
    assert JobState.RETRYING == "RETRYING"
    assert JobState.DLQ == "DLQ"


def test_job_state_string_enum():
    """Test that JobState values are strings."""
    assert isinstance(JobState.QUEUED.value, str)
