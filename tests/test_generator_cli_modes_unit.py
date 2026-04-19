"""Unit tests for helpers in :mod:`generator.cli.modes`."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Final

import pytest

from generator.cli import modes
from generator.models import GeneratedTask

_COACH_VARIANTS: Final[int] = 10
_ANSWER_ATTR: Final[int] = 42
_LOADED_ANSWER: Final[int] = 99
_STATE_NAME: Final[str] = "state.pkl"
_SOL_NAME: Final[str] = "sol.py"
_EXPORTED: Final[str] = "out.md"


def _task(tid: str = "m1") -> GeneratedTask:
    """Build a minimal generated task for preview tests.

    Args:
        tid: Task identifier string.

    Returns:
        A :class:`GeneratedTask` instance.
    """
    return GeneratedTask.from_dict(
        {
            "task_id": tid,
            "title": "t",
            "description": "d",
            "input_data": {"x": 1},
            "expected_result": 1,
        }
    )


def test_preview_tasks_respects_coach_limit() -> None:
    """Preview length is capped by ``COACH_PREVIEW_LIMIT``.

    Returns:
        None.
    """
    many = [_task(f"id{i}") for i in range(_COACH_VARIANTS)]
    prev = modes._preview_tasks(many)  # pyright: ignore[reportPrivateUsage]
    assert len(prev) == min(modes.COACH_PREVIEW_LIMIT, len(many))


def test_module_context_returns_vars_dict() -> None:
    """Expose user-defined names from a loaded module object.

    Returns:
        None.
    """
    mod = ModuleType("tmp")
    mod.answer = _ANSWER_ATTR  # pyright: ignore[reportAttributeAccessIssue]
    ctx = modes._module_context(mod)  # pyright: ignore[reportPrivateUsage]
    assert ctx["answer"] == _ANSWER_ATTR


def test_load_solution_module_roundtrip(tmp_path: Path) -> None:
    """Load a Python file path as a module namespace.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "user.py"
    path.write_text("ANSWER = 99\n", encoding="utf-8")
    loaded = (
        modes._load_solution_module(  # pyright: ignore[reportPrivateUsage]
            str(path)
        )
    )
    assert loaded.ANSWER == _LOADED_ANSWER


def test_load_solution_module_missing_raises() -> None:
    """Missing paths surface as import or OS errors.

    Returns:
        None.
    """
    with pytest.raises((ImportError, FileNotFoundError, OSError)):
        modes._load_solution_module(  # pyright: ignore[reportPrivateUsage]
            "/nonexistent/no_file.py"
        )


def test_print_solve_summary_with_and_without_export(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Summary prints state, solution, and optional export paths.

    Args:
        capsys: Pytest stdout capture fixture.

    Returns:
        None.
    """
    modes._print_solve_summary(  # pyright: ignore[reportPrivateUsage]
        state_file=_STATE_NAME,
        solution_file=_SOL_NAME,
        exported_path=None,
    )
    out = capsys.readouterr().out
    assert _STATE_NAME in out
    assert _SOL_NAME in out
    modes._print_solve_summary(  # pyright: ignore[reportPrivateUsage]
        state_file="a.pkl",
        solution_file="b.py",
        exported_path=_EXPORTED,
    )
    out2 = capsys.readouterr().out
    assert _EXPORTED in out2


def test_print_coach_preview_outputs_header(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Coach preview emits non-empty stdout for one task.

    Args:
        capsys: Pytest stdout capture fixture.

    Returns:
        None.
    """
    modes._print_coach_preview(  # pyright: ignore[reportPrivateUsage]
        [_task()]
    )
    out = capsys.readouterr().out
    assert len(out) > 0
