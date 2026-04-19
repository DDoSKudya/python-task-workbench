"""Tests for inverse task generation (:mod:`generator.cli.inverse`)."""

from __future__ import annotations

from typing import Final

from generator.cli.inverse import inverse_task
from generator.models import GeneratedTask

_INVERSE_ROWS: Final[int] = 3


def test_inverse_task_returns_none_when_multiple_input_keys() -> None:
    """Inverse transform is undefined for multi-key input dicts.

    Returns:
        None.
    """
    task = GeneratedTask.from_dict(
        {
            "task_id": "t",
            "title": "T",
            "description": "",
            "input_data": {"a": 1, "b": 2},
            "expected_result": {"g": [1]},
        }
    )
    assert inverse_task(task) is None


def test_inverse_task_builds_flat_rows() -> None:
    """Inverse flattens nested expected lists into row records.

    Returns:
        None.
    """
    task = GeneratedTask.from_dict(
        {
            "task_id": "t",
            "title": "T",
            "description": "",
            "input_data": {"raw": [1]},
            "expected_result": {"north": [10, 20], "south": [5]},
        }
    )
    inv = inverse_task(task)
    assert inv is not None
    assert inv.task_id != task.task_id
    assert isinstance(inv.expected_result, list)
    assert len(inv.expected_result) == _INVERSE_ROWS
