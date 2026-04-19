"""
Tests for answer checks and mutation warnings
(:mod:`generator.cli.verify`).
"""

from __future__ import annotations

import re
from typing import Final

import pytest

from generator.cli.verify import check_answers, input_mutation_warnings
from generator.models import GeneratedTask
from messages import (
    ERROR_ANSWERS_COUNT_MISMATCH_DINAMIC_POSTFIX_PHDP,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_PHDP,
    TASKS_VAR_NAME_DINAMIC_POSTFIX_PHDP,
)

_EXPECTED: Final[int] = 42
_SINGLE_WARN: Final[int] = 1


def _one_task() -> GeneratedTask:
    """Single task with stable id and expected answer.

    Returns:
        A :class:`GeneratedTask` instance.
    """
    return GeneratedTask.from_dict(
        {
            "task_id": "v1",
            "title": "t",
            "description": "d",
            "input_data": {"a": 1},
            "expected_result": _EXPECTED,
        }
    )


def test_check_answers_passes_and_prints_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Matching answers print task id and counts.

    Args:
        capsys: Pytest stdout capture fixture.

    Returns:
        None.
    """
    task = _one_task()
    check_answers([task], [_EXPECTED], strict_types=False)
    out = capsys.readouterr().out
    assert "v1" in out
    assert "1" in out


def test_check_answers_count_mismatch_raises() -> None:
    """Fewer answers than tasks raises with the catalog template.

    Returns:
        None.
    """
    expected_msg = ERROR_ANSWERS_COUNT_MISMATCH_DINAMIC_POSTFIX_PHDP.format(
        answers_count=0,
        tasks_count=1,
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        check_answers([_one_task()], [], strict_types=False)


def test_input_mutation_warnings_empty_when_tasks_match() -> None:
    """No warnings when ``TASKS`` inputs match generated tasks.

    Returns:
        None.
    """
    task = _one_task()
    module_dict = {
        TASKS_VAR_NAME_DINAMIC_POSTFIX_PHDP: [
            {KEY_INPUT_DATA_DINAMIC_POSTFIX_PHDP: {"a": 1}},
        ],
    }
    assert input_mutation_warnings([task], module_dict) == []


def test_input_mutation_warnings_when_input_changed() -> None:
    """Differing input data yields one warning string.

    Returns:
        None.
    """
    task = _one_task()
    module_dict = {
        TASKS_VAR_NAME_DINAMIC_POSTFIX_PHDP: [
            {KEY_INPUT_DATA_DINAMIC_POSTFIX_PHDP: {"a": 999}},
        ],
    }
    warns = input_mutation_warnings([task], module_dict)
    assert len(warns) == _SINGLE_WARN


def test_input_mutation_warnings_missing_tasks_var() -> None:
    """Missing ``TASKS`` list yields one warning.

    Returns:
        None.
    """
    warns = input_mutation_warnings([_one_task()], {})
    assert len(warns) == _SINGLE_WARN
