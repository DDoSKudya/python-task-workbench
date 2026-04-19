"""
This module defines the core “task” data model for the generator, plus
helpers to derive task families and to normalize raw payloads into
strongly-typed task instances.

It works by interpreting mapping-like payloads (from task packs or JSON)
into a GeneratedTask dataclass, coercing fields like input data,
collections, hints, and check configuration into consistent types and
defaults.

It contains type aliases for task input/result types and payload
mappings, and a task_family_from_id function that derives a logical
family key from auto-generated task IDs by slicing parts between
separators.

Helper functions such as _is_str_key_object_dict, _optional_str,
_string_collection, _check_input_mode, and _input_data validate and
normalize individual payload fields, including enforcing that input_data
is mapping-like and that check_input is one of the supported modes.

The GeneratedTask dataclass (aliased as Task) holds all task metadata
used by generator and CLI layers: identifiers, description, input and
expected result, collections, constraints, hints, pitfalls, analogy,
complexity, starter code, and checker configuration.

Its from_dict constructor uses the helper functions to build an
immutable instance from a raw payload, applying sensible fallbacks for
missing description, optional strings, collections, and check-related
fields.
"""

from __future__ import annotations

from collections.abc import Mapping

from dataclasses import dataclass, field
from typing import Final, TypeGuard, cast

from core.models import CheckInputMode
from messages import (
    AUTO_TASK_PREFIX_DINAMIC_POSTFIX_P2VG,
    CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_TGHG,
    CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG,
    EMPTY_DESCRIPTION_DINAMIC_POSTFIX_P2VG,
    ERR_INPUT_DATA_MAPPING_REQUIRED_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_ANALOGY_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_CHECK_ENTRY_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_CHECK_INPUT_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_CHECK_INPUT_KW_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_COLLECTIONS_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_COMMON_PITFALLS_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_COMPLEXITY_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_CONSTRAINTS_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_DESCRIPTION_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_DIFFICULTY_HINTS_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_EXPECTED_RESULT_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_INPUT_DATA_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_OPTIMAL_TOOL_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_PATTERN_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_STARTER_CODE_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_TASK_ID_KEY_DINAMIC_POSTFIX_P2VG,
    PAYLOAD_TITLE_KEY_DINAMIC_POSTFIX_P2VG,
    TASK_ID_SEPARATOR_DINAMIC_POSTFIX_P2VG,
)

from .settings import AUTO_FAMILY_PARTS_MIN

AUTO_FAMILY_SLICE_START: Final[int] = 2
AUTO_FAMILY_SLICE_END: Final[int] = -1
type TaskInputData = dict[str, object]
type TaskResult = object
type TaskPayload = Mapping[str, object]
type StringCollection = list[str] | tuple[str, ...]


def task_family_from_id(task_id: str) -> str:
    """Extract a logical task family key from a task identifier.

    Args:
        task_id: Task identifier.

    Returns:
        Family key derived from the task identifier.
    """
    if task_id.startswith(AUTO_TASK_PREFIX_DINAMIC_POSTFIX_P2VG):
        parts = task_id.split(TASK_ID_SEPARATOR_DINAMIC_POSTFIX_P2VG)
        return (
            TASK_ID_SEPARATOR_DINAMIC_POSTFIX_P2VG.join(
                parts[AUTO_FAMILY_SLICE_START:AUTO_FAMILY_SLICE_END]
            )
            if len(parts) >= AUTO_FAMILY_PARTS_MIN
            else task_id
        )
    return task_id


def _is_str_key_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    """Return whether value is a dictionary with string keys.

    Args:
        value: Candidate mapping-like object.

    Returns:
        ``True`` when ``value`` is compatible with ``dict[str,
        object]``.
    """
    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)


def _optional_str(payload: TaskPayload, key: str) -> str | None:
    """Read optional string field from payload.

    Args:
        payload: Source payload mapping.
        key: Field name.

    Returns:
        String value if present and string-like, else ``None``.
    """
    raw = payload.get(key)
    return raw if isinstance(raw, str) else None


def _string_collection(payload: TaskPayload, key: str) -> tuple[str, ...]:
    """Read list-like string collection from payload.

    Args:
        payload: Source payload mapping.
        key: Field name.

    Returns:
        Tuple of string values.
    """
    raw = payload.get(key)
    if not isinstance(raw, (list, tuple)):
        return ()
    return tuple(str(item) for item in raw)


def _check_input_mode(raw: object) -> CheckInputMode:
    """Normalize raw check-input mode value to supported literal.

    Args:
        raw: Raw payload value from ``check_input``.

    Returns:
        ``keyword`` for explicit keyword mode, otherwise positional.
    """
    if raw == CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_TGHG:
        return cast(
            CheckInputMode,
            CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_TGHG,
        )
    return cast(
        CheckInputMode,
        CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG,
    )


def _default_check_input_mode() -> CheckInputMode:
    """Return default check-input mode for new generated tasks.

    Returns:
        Default positional check-input mode literal.
    """
    return cast(
        CheckInputMode,
        CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG,
    )


def _input_data(payload: TaskPayload) -> TaskInputData:
    """Read and normalize ``input_data`` from payload.

    Args:
        payload: Source payload mapping.

    Returns:
        Input-data dictionary with string keys.
    """
    raw = payload[PAYLOAD_INPUT_DATA_KEY_DINAMIC_POSTFIX_P2VG]
    if _is_str_key_object_dict(raw):
        return dict(raw)
    if isinstance(raw, Mapping):
        return {str(key): value for key, value in raw.items()}
    raise TypeError(
        ERR_INPUT_DATA_MAPPING_REQUIRED_DINAMIC_POSTFIX_P2VG.format(
            field=PAYLOAD_INPUT_DATA_KEY_DINAMIC_POSTFIX_P2VG,
            actual_type=type(raw),
        )
    )


@dataclass(frozen=True)
class GeneratedTask:
    """Task definition used by generator and CLI layers."""

    task_id: str
    title: str
    description: str
    input_data: TaskInputData
    expected_result: TaskResult
    collections: tuple[str, ...]
    optimal_tool: str | None = None
    pattern: str | None = None
    constraints: tuple[str, ...] = ()
    difficulty_hints: tuple[str, ...] = ()
    common_pitfalls: tuple[str, ...] = ()
    real_world_analogy: str | None = None
    estimated_complexity: str | None = None
    starter_code: str | None = None
    check_entry: str = ""
    check_input: CheckInputMode = field(
        default_factory=_default_check_input_mode
    )
    check_input_kw: str | None = None

    @classmethod
    def from_dict(cls, payload: TaskPayload) -> GeneratedTask:
        """Build a task instance from a mapping payload.

        Args:
            payload: Source payload mapping.

        Returns:
            Parsed task instance.
        """
        return cls(
            task_id=str(payload[PAYLOAD_TASK_ID_KEY_DINAMIC_POSTFIX_P2VG]),
            title=str(payload[PAYLOAD_TITLE_KEY_DINAMIC_POSTFIX_P2VG]),
            description=str(
                payload.get(
                    PAYLOAD_DESCRIPTION_KEY_DINAMIC_POSTFIX_P2VG,
                    EMPTY_DESCRIPTION_DINAMIC_POSTFIX_P2VG,
                )
            ),
            input_data=_input_data(payload),
            expected_result=payload[
                PAYLOAD_EXPECTED_RESULT_KEY_DINAMIC_POSTFIX_P2VG
            ],
            collections=_string_collection(
                payload, PAYLOAD_COLLECTIONS_KEY_DINAMIC_POSTFIX_P2VG
            ),
            optimal_tool=_optional_str(
                payload, PAYLOAD_OPTIMAL_TOOL_KEY_DINAMIC_POSTFIX_P2VG
            ),
            pattern=_optional_str(
                payload, PAYLOAD_PATTERN_KEY_DINAMIC_POSTFIX_P2VG
            ),
            constraints=_string_collection(
                payload, PAYLOAD_CONSTRAINTS_KEY_DINAMIC_POSTFIX_P2VG
            ),
            difficulty_hints=_string_collection(
                payload, PAYLOAD_DIFFICULTY_HINTS_KEY_DINAMIC_POSTFIX_P2VG
            ),
            common_pitfalls=_string_collection(
                payload, PAYLOAD_COMMON_PITFALLS_KEY_DINAMIC_POSTFIX_P2VG
            ),
            real_world_analogy=_optional_str(
                payload, PAYLOAD_ANALOGY_KEY_DINAMIC_POSTFIX_P2VG
            ),
            estimated_complexity=_optional_str(
                payload, PAYLOAD_COMPLEXITY_KEY_DINAMIC_POSTFIX_P2VG
            ),
            starter_code=_starter_code_from_payload(payload),
            check_entry=_check_entry_from_payload(payload),
            check_input=_check_input_mode_from_payload(payload),
            check_input_kw=_check_input_kw_from_payload(payload),
        )


def _check_entry_from_payload(payload: TaskPayload) -> str:
    """Read `check_entry` field from payload.

    Args:
        payload: Source payload mapping.

    Returns:
        Stripped callable name or an empty string.
    """
    raw = payload.get(PAYLOAD_CHECK_ENTRY_KEY_DINAMIC_POSTFIX_P2VG)
    return raw.strip() if isinstance(raw, str) else ""


def _check_input_mode_from_payload(payload: TaskPayload) -> CheckInputMode:
    """Read `check_input` mode from payload.

    Args:
        payload: Source payload mapping.

    Returns:
        Check-input mode (`keyword` or `positional`).
    """
    raw = payload.get(PAYLOAD_CHECK_INPUT_KEY_DINAMIC_POSTFIX_P2VG)
    return _check_input_mode(raw)


def _check_input_kw_from_payload(payload: TaskPayload) -> str | None:
    """Read optional keyword argument name for check input.

    Args:
        payload: Source payload mapping.

    Returns:
        Stripped keyword argument name or ``None``.
    """
    raw = payload.get(PAYLOAD_CHECK_INPUT_KW_KEY_DINAMIC_POSTFIX_P2VG)
    return raw.strip() if isinstance(raw, str) and raw.strip() else None


def _starter_code_from_payload(payload: TaskPayload) -> str | None:
    """Read optional starter code from payload.

    Args:
        payload: Source payload mapping.

    Returns:
        Starter code string, empty string, or ``None``.
    """
    if PAYLOAD_STARTER_CODE_KEY_DINAMIC_POSTFIX_P2VG not in payload:
        return None
    raw = payload.get(PAYLOAD_STARTER_CODE_KEY_DINAMIC_POSTFIX_P2VG)
    return "" if raw is None else str(raw)


type Task = GeneratedTask
