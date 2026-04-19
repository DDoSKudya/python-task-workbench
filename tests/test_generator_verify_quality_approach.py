"""
Tests for quality warnings and approach feedback
(:mod:`generator.cli.verify`).
"""

from __future__ import annotations

import ast
from typing import Final

from generator.cli.verify import approach_feedback, quality_warnings
from generator.models import GeneratedTask

_TASKS_ONE: Final[int] = 1
_OPTIMAL_TOOL: Final[str] = "stdlib.collections.Counter"


def _task(**extra: object) -> GeneratedTask:
    """Build a task dict with optional overrides.

    Args:
        **extra: Extra keys merged into the base payload.

    Returns:
        Parsed :class:`GeneratedTask`.
    """
    base: dict[str, object] = {
        "task_id": "q1",
        "title": "t",
        "description": "d",
        "input_data": {"x": 1},
        "expected_result": 1,
    }
    base.update(extra)
    return GeneratedTask.from_dict(base)


def test_quality_warnings_empty_when_functions_ok() -> None:
    """Valid solve function avoids missing-function warnings.

    Returns:
        None.
    """
    src = """
def solve_task_1(input_data):
    x = input_data["x"] + 1
    return x
"""
    tree = ast.parse(src)
    warns = quality_warnings(tree, tasks_count=_TASKS_ONE)
    assert all("missing" not in w.lower() for w in warns)


def test_quality_warnings_missing_function() -> None:
    """Empty module warns about missing ``solve_task_1``.

    Returns:
        None.
    """
    tree = ast.parse("")
    warns = quality_warnings(tree, tasks_count=_TASKS_ONE)
    assert any("solve_task_1" in w for w in warns)


def test_approach_feedback_when_tool_not_used() -> None:
    """Unused ``optimal_tool`` produces at least one note.

    Returns:
        None.
    """
    task = _task(optimal_tool=_OPTIMAL_TOOL)
    tree = ast.parse("x = 1\n")
    notes = approach_feedback([task], tree)
    assert len(notes) >= 1


def test_approach_feedback_empty_without_optimal_tool() -> None:
    """No optimal tool hint yields empty feedback.

    Returns:
        None.
    """
    task = _task()
    tree = ast.parse("import itertools\n")
    assert approach_feedback([task], tree) == []
