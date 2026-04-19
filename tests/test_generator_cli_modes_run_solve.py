"""
Integration-style tests for :func:`generator.cli.modes.run_solve_mode`.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Final
from unittest.mock import patch

from generator.cli.modes import run_solve_mode
from generator.cli.resolve import resolve_config
from generator.models import GeneratedTask
from messages import EXPORT_FORMAT_NONE_DINAMIC_POSTFIX_Y8BW

_COUNT_ONE: Final[int] = 1
_INVERSE_ZERO: Final[float] = 0.0


def _one_task() -> GeneratedTask:
    """Single trivial task for solve-mode wiring tests.

    Returns:
        A :class:`GeneratedTask` instance.
    """
    return GeneratedTask.from_dict(
        {
            "task_id": "solve_t1",
            "title": "T",
            "description": "d",
            "input_data": {"n": 0},
            "expected_result": 0,
        }
    )


def test_run_solve_mode_invokes_save_and_template(
    tmp_path: Path,
) -> None:
    """Solve mode generates tasks, saves state, and writes templates.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    cfg = replace(
        resolve_config(),
        count=_COUNT_ONE,
        session_size=_COUNT_ONE,
        state_file=str(tmp_path / "state.pkl"),
        solution_file=str(tmp_path / "sol.py"),
        export_format=EXPORT_FORMAT_NONE_DINAMIC_POSTFIX_Y8BW,
        export_file=None,
        content_pack="mock-pack",
        story_mode=False,
        inverse_rate=_INVERSE_ZERO,
    )
    task = _one_task()
    with (
        patch(
            "generator.cli.modes.generate_tasks_batch",
            return_value=[task],
        ) as gen,
        patch("generator.cli.modes.save_state") as save,
        patch(
            "generator.cli.modes.write_solution_template",
        ) as wst,
        patch(
            "generator.cli.modes.export_tasks",
            return_value=None,
        ) as exp,
        patch("generator.cli.modes._render_generated_tasks"),
    ):
        run_solve_mode(cfg)
    gen.assert_called_once_with(cfg)
    save.assert_called_once()
    wst.assert_called_once()
    exp.assert_called_once()
