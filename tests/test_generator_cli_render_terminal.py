"""Tests for :mod:`generator.cli.render_terminal`."""

from __future__ import annotations

from typing import Final

import pytest

from generator.cli.render_terminal import render_task, step_hints
from generator.models import GeneratedTask

_INDEX_ONE: Final[int] = 1
_BEGINNER_HINTS: Final[int] = 3


def _base_payload() -> dict[str, object]:
    """Sample task payload for render and hint tests.

    Returns:
        Mapping passed to :class:`GeneratedTask.from_dict`.
    """
    return {
        "task_id": "r1",
        "title": "Render me",
        "description": "Short",
        "input_data": {"x": [1, 2]},
        "expected_result": {"k": 1},
        "collections": ["list", "dict"],
        "constraints": ["c1"],
    }


def test_step_hints_prefers_difficulty_hints() -> None:
    """``difficulty_hints`` override generated step hints.

    Returns:
        None.
    """
    payload = _base_payload()
    payload["difficulty_hints"] = ["one", "two"]
    task = GeneratedTask.from_dict(payload)
    assert step_hints(task) == ["one", "two"]


def test_step_hints_beginner_fallback() -> None:
    """Without difficulty hints, derive steps from description.

    Returns:
        None.
    """
    task = GeneratedTask.from_dict(
        {**_base_payload(), "description": "Hi"},
    )
    hints = step_hints(task)
    assert len(hints) == _BEGINNER_HINTS


def test_render_task_prints_headers(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Render includes title, id, collections, and constraints.

    Args:
        capsys: Pytest stdout capture fixture.

    Returns:
        None.
    """
    task = GeneratedTask.from_dict(_base_payload())
    render_task(
        task,
        index=_INDEX_ONE,
        show_solution=False,
        show_full_example=False,
        hints_step=False,
    )
    out = capsys.readouterr().out
    assert "Render me" in out
    assert "r1" in out
    assert "list" in out
    assert "dict" in out
    assert "c1" in out
