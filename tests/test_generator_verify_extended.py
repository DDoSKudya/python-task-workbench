"""Additional tests for :mod:`generator.cli.verify`."""

from __future__ import annotations

import ast
from typing import Final

import pytest

from generator.cli.verify import (
    collect_used_tool_tokens,
    load_answers_from_module,
    validate_solution_file_context,
)
from generator.models import GeneratedTask

_ANSWERS: Final[list[int]] = [1, 2, 3]


def test_load_answers_from_module_ok() -> None:
    """Read ``ANSWERS`` from a module mapping.

    Returns:
        None.
    """
    answers = load_answers_from_module({"ANSWERS": _ANSWERS})
    assert answers == _ANSWERS


def test_load_answers_from_module_missing() -> None:
    """Missing ``ANSWERS`` raises :exc:`ValueError`.

    Returns:
        None.
    """
    with pytest.raises(ValueError):
        load_answers_from_module({})


def test_validate_solution_file_context_ok() -> None:
    """Matching ``TASK_IDS`` passes validation.

    Returns:
        None.
    """
    tasks = [
        GeneratedTask.from_dict(
            {
                "task_id": "a",
                "title": "t",
                "description": "",
                "input_data": {"x": 1},
                "expected_result": 1,
            }
        )
    ]
    validate_solution_file_context(tasks, {"TASK_IDS": ["a"]})


def test_validate_solution_file_context_mismatch() -> None:
    """Mismatched ids raise :exc:`ValueError`.

    Returns:
        None.
    """
    tasks = [
        GeneratedTask.from_dict(
            {
                "task_id": "a",
                "title": "t",
                "description": "",
                "input_data": {"x": 1},
                "expected_result": 1,
            }
        )
    ]
    with pytest.raises(ValueError):
        validate_solution_file_context(tasks, {"TASK_IDS": ["b"]})


def test_collect_used_tool_tokens() -> None:
    """AST visitor records imported modules and attribute names.

    Returns:
        None.
    """
    tree = ast.parse("import itertools\nitertools.count()\n")
    tokens = collect_used_tool_tokens(tree)
    assert "itertools" in tokens
    assert "count" in tokens
