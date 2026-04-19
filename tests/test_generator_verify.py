"""Tests for :mod:`generator.cli.verify`."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Final

import pytest

from generator.cli.verify import parse_solution_ast, quality_warnings
from messages import (
    ERROR_SOLUTION_FILE_MISSING_DINAMIC_POSTFIX_PHDP,
    ERROR_SYNTAX_IN_SOLUTION_FILE_DINAMIC_POSTFIX_PHDP,
)

_TASKS_COUNT: Final[int] = 2


def test_parse_solution_ast_missing_file(tmp_path: Path) -> None:
    """Missing path raises with the catalog missing-file template.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    missing = tmp_path / "nope.py"
    expected = ERROR_SOLUTION_FILE_MISSING_DINAMIC_POSTFIX_PHDP.format(
        path=str(missing),
    )
    with pytest.raises(ValueError, match=re.escape(expected)):
        parse_solution_ast(str(missing))


def test_parse_solution_ast_syntax_error(tmp_path: Path) -> None:
    """Invalid Python raises with syntax error template text.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    bad = tmp_path / "bad.py"
    bad.write_text("def x(\n", encoding="utf-8")
    prefix = ERROR_SYNTAX_IN_SOLUTION_FILE_DINAMIC_POSTFIX_PHDP.split("{", 1)[
        0
    ]
    with pytest.raises(ValueError, match=re.escape(prefix.rstrip())):
        parse_solution_ast(str(bad))


def test_parse_solution_ast_ok(tmp_path: Path) -> None:
    """Valid file parses to an ``ast.Module``.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "ok.py"
    path.write_text("x = 1\n", encoding="utf-8")
    tree = parse_solution_ast(str(path))
    assert isinstance(tree, ast.Module)


def test_quality_warnings_detects_missing_solve_functions() -> None:
    """Empty module warns about missing ``solve_task_*`` stubs.

    Returns:
        None.
    """
    tree = ast.parse("")
    warnings = quality_warnings(tree, tasks_count=_TASKS_COUNT)
    assert any("solve_task_1" in w for w in warnings)
