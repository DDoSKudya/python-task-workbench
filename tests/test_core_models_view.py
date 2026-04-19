"""Tests for task view models and status lines."""

from __future__ import annotations

from typing import Final

from core.models import (
    CheckResult,
    SessionConfig,
    Task,
    TaskSession,
    TaskState,
    TaskViewModel,
    all_task_view_models,
    task_view_model,
)
from messages import (
    KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_TGHG,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_TGHG,
    KEY_TASK_ID_DINAMIC_POSTFIX_TGHG,
    KEY_TITLE_DINAMIC_POSTFIX_TGHG,
    STATUS_FAILED_DINAMIC_POSTFIX_TGHG,
)

_PACK: Final[str] = "p"
_ERR_LINE_LEN: Final[int] = 200
_STATUS_LINE_MAX: Final[int] = 130
_SESSION_COUNT_TWO: Final[int] = 2
_TASK_INDEX: Final[int] = 0


def _minimal_task(**kwargs: object) -> Task:
    """Build a task from a base payload with optional overrides.

    Args:
        **kwargs: Fields merged into the base payload mapping.

    Returns:
        Parsed :class:`Task` instance.
    """
    base: dict[str, object] = {
        KEY_TASK_ID_DINAMIC_POSTFIX_TGHG: "id1",
        KEY_TITLE_DINAMIC_POSTFIX_TGHG: "T",
        KEY_INPUT_DATA_DINAMIC_POSTFIX_TGHG: {"x": 1},
        KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_TGHG: 2,
    }
    base.update(kwargs)
    return Task.from_payload(base, pack_name=_PACK)


def test_task_view_model_pending() -> None:
    """Pending task exposes id and zero-based index.

    Returns:
        None.
    """
    cfg = SessionConfig(
        selected_packs=(_PACK,),
        count=1,
        seed=None,
        strict_types=True,
    )
    task = _minimal_task()
    session = TaskSession(config=cfg, tasks=[task])
    vm = task_view_model(session, _TASK_INDEX)
    assert isinstance(vm, TaskViewModel)
    assert vm.task_id == "id1"
    assert vm.index == _TASK_INDEX


def test_task_view_model_failed_with_error_truncation() -> None:
    """Failed status line is bounded in length.

    Returns:
        None.
    """
    cfg = SessionConfig(
        selected_packs=(_PACK,),
        count=1,
        seed=None,
        strict_types=True,
    )
    task = _minimal_task()
    long_err = "e" * _ERR_LINE_LEN
    state = TaskState(
        status=STATUS_FAILED_DINAMIC_POSTFIX_TGHG,  # pyright: ignore[reportArgumentType]
        result=CheckResult(
            task_index=_TASK_INDEX,
            passed=False,
            error_text=f"{long_err}\nsecond line",
        ),
    )
    session = TaskSession(config=cfg, tasks=[task], states=[state])
    vm = task_view_model(session, _TASK_INDEX)
    assert vm.status == STATUS_FAILED_DINAMIC_POSTFIX_TGHG
    assert len(vm.status_line) <= _STATUS_LINE_MAX


def test_all_task_view_models_matches_task_count() -> None:
    """View model rows align with tasks in session order.

    Returns:
        None.
    """
    cfg = SessionConfig(
        selected_packs=(_PACK,),
        count=_SESSION_COUNT_TWO,
        seed=None,
        strict_types=True,
    )
    first = _minimal_task(
        **{KEY_TASK_ID_DINAMIC_POSTFIX_TGHG: "a"},
    )
    second = _minimal_task(
        **{KEY_TASK_ID_DINAMIC_POSTFIX_TGHG: "b"},
    )
    session = TaskSession(config=cfg, tasks=[first, second])
    rows = all_task_view_models(session)
    assert len(rows) == 2
    assert rows[0].task_id == "a"
    assert rows[1].task_id == "b"
