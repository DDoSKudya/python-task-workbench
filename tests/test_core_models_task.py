"""Tests for :mod:`core.models` task payloads."""

from __future__ import annotations

from typing import Final

from core.models import Task
from messages import (
    CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG,
    KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_TGHG,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_TGHG,
    KEY_TASK_ID_DINAMIC_POSTFIX_TGHG,
    KEY_TITLE_DINAMIC_POSTFIX_TGHG,
)

_PACK: Final[str] = "demo-pack"


def test_task_from_payload_minimal() -> None:
    """Parse a minimal payload into a :class:`Task` with defaults.

    Returns:
        None.
    """
    payload = {
        KEY_TASK_ID_DINAMIC_POSTFIX_TGHG: "tid",
        KEY_TITLE_DINAMIC_POSTFIX_TGHG: "Title",
        KEY_INPUT_DATA_DINAMIC_POSTFIX_TGHG: {"n": 1},
        KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_TGHG: 2,
    }
    task = Task.from_payload(payload, pack_name=_PACK)
    assert task.task_id == "tid"
    assert task.title == "Title"
    assert task.pack_name == _PACK
    assert task.input_data == {"n": 1}
    assert task.expected_result == 2
    assert task.check_input == CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG
    assert task.check_entry == ""
