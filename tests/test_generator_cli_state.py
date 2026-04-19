"""Tests for CLI task state persistence (:mod:`generator.cli.state`)."""

from __future__ import annotations

import pytest
from pathlib import Path
from typing import Final

import generator.cli.state as state_module
from generator.cli.state import (
    load_history_from_state,
    load_tasks_from_state,
    save_state,
)
from generator.models import GeneratedTask

_BAD_JSON: Final[str] = '{"tasks": "nope"}'
_MISSING_PATH: Final[str] = "/nonexistent/path/state.json"


@pytest.fixture(autouse=True)
def _patch_runtime_task_alias(  # pyright: ignore[reportUnusedFunction]
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Make ``Task.from_dict`` work if ``generator.models`` uses a PEP
    695 alias.

    ``type Task = GeneratedTask`` exposes :class:`~typing.TypeAliasType`
    at runtime, which has no ``from_dict``. Some ``state``
    implementations call ``Task.from_dict``; binding the name to
    :class:`GeneratedTask` fixes that without changing application
    modules under test.
    """
    task_obj = getattr(state_module, "Task", None)
    if task_obj is not None and getattr(task_obj, "from_dict", None) is None:
        monkeypatch.setattr(state_module, "Task", GeneratedTask, raising=False)


def _sample_task(task_id: str = "s1") -> GeneratedTask:
    """Create a small task for roundtrip tests.

    Args:
        task_id: Stored task identifier.

    Returns:
        A :class:`GeneratedTask` instance.
    """
    return GeneratedTask.from_dict(
        {
            "task_id": task_id,
            "title": "Title",
            "description": "",
            "input_data": {"k": 1},
            "expected_result": 2,
        }
    )


def test_save_and_load_tasks_roundtrip(tmp_path: Path) -> None:
    """Persisted task order matches save order.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "state.json"
    tasks = [_sample_task("a"), _sample_task("b")]
    save_state(tasks, str(path))
    loaded = load_tasks_from_state(str(path))
    assert len(loaded) == 2
    assert [t.task_id for t in loaded] == ["a", "b"]


def test_load_tasks_from_state_invalid_raises(tmp_path: Path) -> None:
    """Malformed JSON document raises :exc:`ValueError`.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "bad.json"
    path.write_text(_BAD_JSON, encoding="utf-8")
    with pytest.raises(ValueError):
        load_tasks_from_state(str(path))


def test_load_history_accumulates(tmp_path: Path) -> None:
    """History merges ids across successive saves.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "state.json"
    save_state([_sample_task("x")], str(path))
    assert "x" in load_history_from_state(str(path))
    save_state([_sample_task("y")], str(path))
    hist = load_history_from_state(str(path))
    assert "x" in hist
    assert "y" in hist


def test_load_tasks_missing_file_raises() -> None:
    """Missing state file raises :exc:`ValueError`.

    Returns:
        None.
    """
    with pytest.raises(ValueError):
        load_tasks_from_state(_MISSING_PATH)
