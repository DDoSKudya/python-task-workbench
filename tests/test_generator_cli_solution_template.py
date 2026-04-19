"""Tests for :mod:`generator.cli.solution_template`."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from generator.cli.solution_template import write_solution_template
from generator.models import GeneratedTask

_MAIN_GUARD: Final[str] = '__name__ == "__main__"'


def _task(task_id: str = "tid_1") -> GeneratedTask:
    """Build a trivial task for template emission.

    Args:
        task_id: Identifier embedded in the template.

    Returns:
        A :class:`GeneratedTask` instance.
    """
    return GeneratedTask.from_dict(
        {
            "task_id": task_id,
            "title": "T",
            "description": "d",
            "input_data": {"n": 1},
            "expected_result": 2,
        }
    )


def test_write_solution_template_creates_expected_sections(
    tmp_path: Path,
) -> None:
    """Template file lists IDs, tasks, stubs, answers, and main guard.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "sol.py"
    write_solution_template([_task()], str(path))
    text = path.read_text(encoding="utf-8")
    assert "TASK_IDS" in text
    assert "TASKS" in text
    assert "solve_task_1" in text
    assert "ANSWERS" in text
    assert _MAIN_GUARD in text
