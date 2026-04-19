"""Tests for :mod:`generator.cli.export_tasks`."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Final

from generator.cli.export_tasks import export_tasks, task_to_payload
from generator.cli.resolve import resolve_config
from generator.models import GeneratedTask
from messages import (
    EXPORT_FORMAT_MARKDOWN_DINAMIC_POSTFIX_Y8BW,
    EXPORT_FORMAT_NONE_DINAMIC_POSTFIX_Y8BW,
    EXPORT_FORMAT_PYTEST_DINAMIC_POSTFIX_Y8BW,
)

_TASK_INDEX: Final[int] = 1
_MARKDOWN_HEAD: Final[str] = "#"


def _task() -> GeneratedTask:
    """Build a sample task for export tests.

    Returns:
        A :class:`GeneratedTask` with stable fields.
    """
    return GeneratedTask.from_dict(
        {
            "task_id": "exp1",
            "title": "Export task",
            "description": "Do something",
            "input_data": {"a": 1},
            "expected_result": [1],
        }
    )


def test_task_to_payload_includes_index_and_metadata() -> None:
    """Payload carries index, id, and input mapping.

    Returns:
        None.
    """
    payload = task_to_payload(_task(), index=_TASK_INDEX)
    assert payload["index"] == _TASK_INDEX
    assert payload["task_id"] == "exp1"
    assert payload["input_data"] == {"a": 1}


def test_export_tasks_none_returns_none() -> None:
    """``none`` export format skips file output.

    Returns:
        None.
    """
    cfg = replace(
        resolve_config(),
        export_format=EXPORT_FORMAT_NONE_DINAMIC_POSTFIX_Y8BW,
    )
    assert export_tasks([_task()], cfg) is None


def test_export_tasks_markdown_writes_file(tmp_path: Path) -> None:
    """Markdown export writes the configured path with headings.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    out = tmp_path / "tasks.md"
    cfg = replace(
        resolve_config(),
        export_format=EXPORT_FORMAT_MARKDOWN_DINAMIC_POSTFIX_Y8BW,
        export_file=str(out),
        state_file=str(tmp_path / "state.pkl"),
    )
    path = export_tasks([_task()], cfg)
    assert path == str(out)
    body = out.read_text(encoding="utf-8")
    assert _MARKDOWN_HEAD in body
    assert "exp1" in body


def test_export_tasks_pytest_writes_tasks_var(tmp_path: Path) -> None:
    """Pytest export embeds ``TASKS`` and ``test_`` stubs.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    out = tmp_path / "tasks_export.py"
    cfg = replace(
        resolve_config(),
        export_format=EXPORT_FORMAT_PYTEST_DINAMIC_POSTFIX_Y8BW,
        export_file=str(out),
        state_file=str(tmp_path / "state.pkl"),
    )
    export_tasks([_task()], cfg)
    body = out.read_text(encoding="utf-8")
    assert "TASKS" in body
    assert "def test_" in body
