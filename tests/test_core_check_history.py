"""Tests for SQLite check history (:mod:`core.check_history`)."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pytest

import core.check_history as ch
from core.check_history import (
    HistoryRowView,
    append_check_record,
    clear_history_file,
    default_history_export_filename,
    export_history_entry_to_python,
    load_entries_newest_first,
)
from core.models import CheckResult, SessionConfig, Task
from messages import (
    KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_TGHG,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_TGHG,
    KEY_TASK_ID_DINAMIC_POSTFIX_TGHG,
    KEY_TITLE_DINAMIC_POSTFIX_TGHG,
)

_PACK: Final[str] = "pack"
_SEED: Final[int] = 7
_DURATION_APPEND: Final[float] = 0.01
_CODE_PRINT: Final[str] = "print(1)"
_TASK_INDEX: Final[int] = 0
_DURATION_EXPORT: Final[float] = 0.1
_CODE_EXPORT: Final[str] = "x=1"
_ERROR_TEXT: Final[str] = "oops"


def _ui_task() -> Task:
    """Build a minimal task for history roundtrip tests.

    Returns:
        A :class:`Task` with stable identifiers.
    """
    return Task.from_payload(
        {
            KEY_TASK_ID_DINAMIC_POSTFIX_TGHG: "h1",
            KEY_TITLE_DINAMIC_POSTFIX_TGHG: "Hist",
            KEY_INPUT_DATA_DINAMIC_POSTFIX_TGHG: {"a": 1},
            KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_TGHG: 2,
        },
        pack_name=_PACK,
    )


def _fresh_store(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Point the module at a temporary SQLite store.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest temporary directory.
    """
    store = ch._HistoryStore(  # pyright: ignore[reportPrivateUsage]
        tmp_path / "db.sqlite3", tmp_path / "old.json"
    )
    monkeypatch.setattr(ch, "_DEFAULT_STORE", store)


def test_append_and_load_history_roundtrip(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Append a record and reload it; clearing removes all rows.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    _fresh_store(monkeypatch, tmp_path)
    clear_history_file()
    cfg = SessionConfig(
        selected_packs=("p",),
        count=1,
        seed=_SEED,
        strict_types=True,
    )
    result = CheckResult(
        task_index=_TASK_INDEX,
        passed=True,
        actual_result=2,
    )
    append_check_record(
        task=_ui_task(),
        result=result,
        code=_CODE_PRINT,
        config=cfg,
        duration_sec=_DURATION_APPEND,
    )
    rows = load_entries_newest_first()
    assert len(rows) >= 1
    row = rows[0]
    assert isinstance(row, HistoryRowView)
    assert row.passed
    assert row.task_id == "h1"
    clear_history_file()
    assert load_entries_newest_first() == []


def test_export_history_writes_python_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Export one history row to a ``.py`` file with expected markers.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    _fresh_store(monkeypatch, tmp_path)
    clear_history_file()
    cfg = SessionConfig(
        selected_packs=("p",),
        count=1,
        seed=None,
        strict_types=False,
    )
    append_check_record(
        task=_ui_task(),
        result=CheckResult(
            task_index=_TASK_INDEX,
            passed=False,
            error_text=_ERROR_TEXT,
        ),
        code=_CODE_EXPORT,
        config=cfg,
        duration_sec=_DURATION_EXPORT,
    )
    row = load_entries_newest_first()[0]
    name = default_history_export_filename(row)
    assert name.endswith(".py")
    out = tmp_path / "exp.py"
    export_history_entry_to_python(row, out)
    text = out.read_text(encoding="utf-8")
    assert "INPUT_DATA" in text or "METADATA" in text
    clear_history_file()
