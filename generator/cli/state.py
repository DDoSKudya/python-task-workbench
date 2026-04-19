"""
This module manages persistence of generated tasks and their history in
a JSON “state” file for the task generator.

It works by serializing Task objects and a bounded list of recent task
IDs into a JSON payload, and by reading that payload back to restore
tasks or just their IDs, handling missing or invalid files gracefully.

It defines type aliases for state and task payloads, JSON formatting
constants, and a helper _is_state_payload that guards against non-dict
or non-string-keyed decoded values.

The _task_to_payload, _load_state_payload, and _dump_state_payload
helpers encapsulate conversion between Task instances and
JSON-serializable dicts, as well as safe reading/writing of the state
file with the configured encoding and indentation.

load_history_from_state and _bounded_history provide history management,
loading past task IDs and trimming the combined list to
STATE_HISTORY_MAX items so history stays bounded over time.

load_tasks_from_state reconstructs full Task objects from the persisted
payload (via Task.from_dict) and rejects malformed state with a
ValueError, while save_state builds a fresh payload with updated tasks
and history and writes it out, making this module the central state
layer for CLI sessions.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from pathlib import Path
from typing import Final, TypeGuard

from generator.models import GeneratedTask
from generator.settings import STATE_HISTORY_MAX
from messages import (
    INVALID_STATE_TASKS_ERROR_DINAMIC_POSTFIX_IC2E,
    KEY_ANALOGY_DINAMIC_POSTFIX_IC2E,
    KEY_COLLECTIONS_DINAMIC_POSTFIX_IC2E,
    KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_IC2E,
    KEY_COMPLEXITY_DINAMIC_POSTFIX_IC2E,
    KEY_CONSTRAINTS_DINAMIC_POSTFIX_IC2E,
    KEY_DESCRIPTION_DINAMIC_POSTFIX_IC2E,
    KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_IC2E,
    KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_IC2E,
    KEY_HISTORY_TASK_IDS_DINAMIC_POSTFIX_IC2E,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_IC2E,
    KEY_OPTIMAL_TOOL_DINAMIC_POSTFIX_IC2E,
    KEY_PATTERN_DINAMIC_POSTFIX_IC2E,
    KEY_TASK_ID_DINAMIC_POSTFIX_IC2E,
    KEY_TASKS_DINAMIC_POSTFIX_IC2E,
    KEY_TITLE_DINAMIC_POSTFIX_IC2E,
    STATE_ENCODING_DINAMIC_POSTFIX_IC2E,
)

JSON_ENSURE_ASCII: Final[bool] = False
JSON_INDENT: Final[int] = 2
type StatePayload = dict[str, object]
type TaskPayload = dict[str, object]


def _empty_state_payload() -> StatePayload:
    """Build a new empty state payload mapping.

    Returns:
        New empty payload dictionary.
    """
    return {}


def _is_state_payload(value: object) -> TypeGuard[StatePayload]:
    """Return whether value is a dictionary with string keys.

    Args:
        value: Candidate decoded JSON value.

    Returns:
        ``True`` when ``value`` is ``dict[str, object]``-compatible.
    """
    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)


def _task_to_payload(task: GeneratedTask) -> TaskPayload:
    """Convert one task model into a serializable payload.

    Args:
        task: Source task model.

    Returns:
        JSON-serializable task mapping for state persistence.
    """
    return {
        KEY_TASK_ID_DINAMIC_POSTFIX_IC2E: task.task_id,
        KEY_TITLE_DINAMIC_POSTFIX_IC2E: task.title,
        KEY_DESCRIPTION_DINAMIC_POSTFIX_IC2E: task.description,
        KEY_COLLECTIONS_DINAMIC_POSTFIX_IC2E: list(task.collections),
        KEY_OPTIMAL_TOOL_DINAMIC_POSTFIX_IC2E: task.optimal_tool,
        KEY_PATTERN_DINAMIC_POSTFIX_IC2E: task.pattern,
        KEY_CONSTRAINTS_DINAMIC_POSTFIX_IC2E: list(task.constraints),
        KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_IC2E: list(task.difficulty_hints),
        KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_IC2E: list(task.common_pitfalls),
        KEY_ANALOGY_DINAMIC_POSTFIX_IC2E: task.real_world_analogy,
        KEY_COMPLEXITY_DINAMIC_POSTFIX_IC2E: task.estimated_complexity,
        KEY_INPUT_DATA_DINAMIC_POSTFIX_IC2E: task.input_data,
        KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_IC2E: task.expected_result,
    }


def _load_state_payload(path: Path) -> StatePayload:
    """Load a state payload from a JSON file.

    Args:
        path: Path to the state file.

    Returns:
        Parsed payload mapping. Returns an empty mapping if the file
        does not exist or cannot be parsed.
    """
    if not path.exists():
        return _empty_state_payload()
    try:
        raw = json.loads(
            path.read_text(encoding=STATE_ENCODING_DINAMIC_POSTFIX_IC2E)
        )
    except (OSError, ValueError):
        return _empty_state_payload()
    return raw if _is_state_payload(raw) else _empty_state_payload()


def _dump_state_payload(payload: Mapping[str, object], path: Path) -> None:
    """Write a state payload to a JSON file.

    Args:
        payload: Payload to write.
        path: Path to the state file.

    Returns:
        None.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT
        ),
        encoding=STATE_ENCODING_DINAMIC_POSTFIX_IC2E,
    )


def load_history_from_state(state_file: str) -> list[str]:
    """Load previously generated task IDs from the state file.

    Args:
        state_file: Path to the state file.

    Returns:
        A list of task IDs (as strings). Returns an empty list if the
        file is missing or invalid.
    """
    payload = _load_state_payload(Path(state_file))
    history = payload.get(KEY_HISTORY_TASK_IDS_DINAMIC_POSTFIX_IC2E)
    return [str(item) for item in history] if isinstance(history, list) else []


def _bounded_history(
    *,
    existing: list[str],
    new_ids: list[str],
) -> list[str]:
    """Combine and trim history IDs to configured maximum size.

    Args:
        existing: Existing history IDs from saved state.
        new_ids: IDs from the current task batch.

    Returns:
        Trimmed history list that does not exceed ``STATE_HISTORY_MAX``.
    """
    merged = existing + new_ids
    if len(merged) <= STATE_HISTORY_MAX:
        return merged
    return merged[-STATE_HISTORY_MAX:]


def load_tasks_from_state(state_file: str) -> list[GeneratedTask]:
    """Load tasks from the state file.

    Args:
        state_file: Path to the state file.

    Returns:
        A list of tasks restored from the state file.

    Raises:
        ValueError: If the state file contains an invalid payload.
    """
    payload = _load_state_payload(Path(state_file))
    tasks_raw = payload.get(KEY_TASKS_DINAMIC_POSTFIX_IC2E)
    if not isinstance(tasks_raw, list):
        raise ValueError(INVALID_STATE_TASKS_ERROR_DINAMIC_POSTFIX_IC2E)
    return [
        GeneratedTask.from_dict(item) for item in tasks_raw if _is_state_payload(item)
    ]


def save_state(tasks: list[GeneratedTask], state_file: str) -> None:
    """Save tasks and their history to the state file.

    Args:
        tasks: Tasks to store in the state file.
        state_file: Path to the state file.

    Returns:
        None.
    """
    path = Path(state_file)
    history = load_history_from_state(state_file)
    task_ids = [task.task_id for task in tasks]
    new_history = _bounded_history(existing=history, new_ids=task_ids)
    tasks_payload = [_task_to_payload(task) for task in tasks]
    payload: StatePayload = {
        KEY_HISTORY_TASK_IDS_DINAMIC_POSTFIX_IC2E: new_history,
        KEY_TASKS_DINAMIC_POSTFIX_IC2E: tasks_payload,
    }
    _dump_state_payload(payload, path)
