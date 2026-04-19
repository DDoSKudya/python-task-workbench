"""Tests for :func:`generator.cli.modes.run_check_mode` with stubs."""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import Final
from unittest.mock import patch

from generator.cli.modes import run_check_mode
from generator.cli.resolve import resolve_config
from generator.models import GeneratedTask

_EXPECTED_ANSWER: Final[int] = 4
_STUB_LINE: Final[str] = "# stub\n"


def _task() -> GeneratedTask:
    """Minimal task aligned with the stub solution module.

    Returns:
        A :class:`GeneratedTask` for check mode.
    """
    return GeneratedTask.from_dict(
        {
            "task_id": "chk1",
            "title": "t",
            "description": "d",
            "input_data": {"k": 2},
            "expected_result": _EXPECTED_ANSWER,
        }
    )


def test_run_check_mode_end_to_end_with_stub_module(
    tmp_path: Path,
) -> None:
    """Run check mode with mocked AST, tasks, and solution module.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    sol = tmp_path / "sol.py"
    sol.write_text(_STUB_LINE, encoding="utf-8")
    cfg = replace(
        resolve_config(),
        state_file=str(tmp_path / "state.pkl"),
        solution_file=str(sol),
        strict_types=False,
    )
    fake_mod = ModuleType("fake_solution")
    fake_mod.TASK_IDS = ["chk1"]  # pyright: ignore[reportAttributeAccessIssue]
    fake_mod.TASKS = [  # pyright: ignore[reportAttributeAccessIssue]
        {"input_data": {"k": 2}}
    ]
    fake_mod.ANSWERS = [  # pyright: ignore[reportAttributeAccessIssue]
        _EXPECTED_ANSWER
    ]

    tree = ast.parse(
        "def solve_task_1(input_data):\n    x = 1\n    return x\n",
    )

    with patch(
        "generator.cli.modes.load_tasks_from_state",
        return_value=[_task()],
    ):
        with patch(
            "generator.cli.modes.parse_solution_ast",
            return_value=tree,
        ):
            with patch(
                "generator.cli.modes._load_solution_module",
                return_value=fake_mod,
            ):
                run_check_mode(cfg, coach_mode=False)
