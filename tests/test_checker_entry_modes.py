"""Tests for :mod:`core.checker` entry resolution modes."""

from __future__ import annotations

from typing import Final

from core.checker import check_solution
from core.models import Task
from messages import CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG

_EMPTY_CHECK_ENTRY: Final[str] = ""
_LIST_COLLECTION: Final[tuple[str, ...]] = ("list",)
_PACK_NAME: Final[str] = "pack"
_TASK_ID: Final[str] = "t"
_TASK_TITLE: Final[str] = "t"
_TASK_DESC: Final[str] = "t"
_TIMEOUT_SEC: Final[int] = 2
_TASK_INDEX: Final[int] = 0
_INPUT_X: Final[int] = 3
_NUMS: Final[list[int]] = [3, 1, 2]


def _task(
    *,
    expected: object,
    check_entry: str = _EMPTY_CHECK_ENTRY,
) -> Task:
    """Build a minimal :class:`Task` for checker mode tests.

    Args:
        expected: Expected learner result for the task.
        check_entry: Optional dotted entry path for strict mode.

    Returns:
        A configured :class:`Task` instance.
    """
    return Task(
        task_id=_TASK_ID,
        title=_TASK_TITLE,
        description=_TASK_DESC,
        input_data={"x": _INPUT_X, "nums": _NUMS},
        expected_result=expected,
        collections=_LIST_COLLECTION,
        pack_name=_PACK_NAME,
        check_entry=check_entry,
        check_input=CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG,  # pyright: ignore[reportArgumentType]
        check_input_kw=None,
        starter_code=None,
    )


def test_strict_mode_requires_check_entry() -> None:
    """Strict mode fails when ``check_entry`` is empty.

    Returns:
        None.
    """
    result = check_solution(
        task_index=_TASK_INDEX,
        task=_task(expected=4, check_entry=_EMPTY_CHECK_ENTRY),
        code="result = input_data['x'] + 1",
        strict_types=True,
        checker_entry_mode="strict",
        timeout_sec=_TIMEOUT_SEC,
    )
    assert not result.passed
    assert result.error_text is not None
    assert "check_entry" in result.error_text.lower()


def test_hybrid_mode_uses_single_callable_without_check_entry() -> None:
    """Hybrid mode accepts one callable without ``check_entry``.

    Returns:
        None.
    """
    result = check_solution(
        task_index=_TASK_INDEX,
        task=_task(expected=4, check_entry=_EMPTY_CHECK_ENTRY),
        code="def compute(data):\n    return data['x'] + 1",
        strict_types=True,
        checker_entry_mode="hybrid",
        timeout_sec=_TIMEOUT_SEC,
    )
    assert result.passed


def test_hybrid_mode_reports_ambiguous_callables() -> None:
    """Hybrid mode fails when multiple callables are ambiguous.

    Returns:
        None.
    """
    result = check_solution(
        task_index=_TASK_INDEX,
        task=_task(expected=4, check_entry=_EMPTY_CHECK_ENTRY),
        code=(
            "def a(input_data):\n    return input_data['x'] + 1\n\n"
            "def b(data):\n    return data['x'] + 1\n"
        ),
        strict_types=True,
        checker_entry_mode="hybrid",
        timeout_sec=_TIMEOUT_SEC,
    )
    assert not result.passed
    assert result.error_text is not None
    assert "check_entry" in result.error_text.lower()


def test_hybrid_mode_uses_result_variable() -> None:
    """Hybrid mode accepts a top-level ``result`` assignment.

    Returns:
        None.
    """
    result = check_solution(
        task_index=_TASK_INDEX,
        task=_task(expected=4, check_entry=_EMPTY_CHECK_ENTRY),
        code="result = input_data['x'] + 1",
        strict_types=True,
        checker_entry_mode="hybrid",
        timeout_sec=_TIMEOUT_SEC,
    )
    assert result.passed


def test_hybrid_mode_passes_with_expected_and_strict_types() -> None:
    """Hybrid mode passes when ``result`` matches expected value.

    Returns:
        None.
    """
    result = check_solution(
        task_index=_TASK_INDEX,
        task=_task(expected=4, check_entry=_EMPTY_CHECK_ENTRY),
        code="result = 4",
        strict_types=True,
        checker_entry_mode="hybrid",
        timeout_sec=_TIMEOUT_SEC,
    )
    assert result.passed
    assert result.actual_result == 4
