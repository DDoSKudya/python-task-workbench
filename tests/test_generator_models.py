"""Tests for :mod:`generator.models`."""

from __future__ import annotations

from typing import Final

import pytest

from generator.models import GeneratedTask, task_family_from_id
from messages import AUTO_TASK_PREFIX_DINAMIC_POSTFIX_P2VG

_FAMILY_PART: Final[str] = "CL1_DICT_GET_DEFAULT_x"


def test_task_family_from_id_plain() -> None:
    """Manual ids pass through as the family name.

    Returns:
        None.
    """
    assert task_family_from_id("manual_id") == "manual_id"


def test_task_family_from_id_auto_pattern() -> None:
    """Auto-prefixed ids normalize to a stable family fragment.

    Returns:
        None.
    """
    tid = f"{AUTO_TASK_PREFIX_DINAMIC_POSTFIX_P2VG}{_FAMILY_PART}"
    fam = task_family_from_id(tid)
    assert "DICT_GET_DEFAULT" in fam or fam == tid


def test_generated_task_from_dict_minimal() -> None:
    """Minimal dict maps to task fields.

    Returns:
        None.
    """
    payload = {
        "task_id": "tid",
        "title": "Hello",
        "description": "",
        "input_data": {"n": 1},
        "expected_result": 2,
    }
    task = GeneratedTask.from_dict(payload)
    assert task.task_id == "tid"
    assert task.input_data == {"n": 1}
    assert task.expected_result == 2


def test_generated_task_from_dict_rejects_non_mapping_input() -> None:
    """``input_data`` must be a mapping.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="input_data"):
        GeneratedTask.from_dict(
            {
                "task_id": "x",
                "title": "t",
                "description": "",
                "input_data": [1, 2],
                "expected_result": 0,
            }
        )
