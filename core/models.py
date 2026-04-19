"""
This module defines the core data models and helper functions for
representing tasks, sessions, check results, and UI-facing task rows in
a learning or coding practice application.

It works by parsing raw task payloads into immutable Task objects,
storing session-level settings in SessionConfig, tracking per-task
mutable state in TaskState, and then projecting this into TaskViewModel
rows with human-readable status text.

It contains type aliases for task status and input modes, default
timeout and per-task duration constants, and small parsers to normalize
task metadata fields such as check entry, input mode, keyword parameter,
starter code, and collection tags.

The TaskSession dataclass ties together a SessionConfig and a list of
Task objects with a parallel list of TaskState instances, initializing
default states in __post_init__ when none are provided.

Status-line utilities (_trim_status_line, _first_line,
_failed_status_line, _status_line_for_state) convert internal status
and error text into concise, single-line labels suitable for display in
the task list.

The top-level functions task_view_model and all_task_view_models
generate immutable TaskViewModel records from a session, providing the
UI layer with ready-to-bind representations of each task and its current
status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Literal, cast

from messages import (
    CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_TGHG,
    CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG,
    ERR_EXPECTED_DICT_SECTION_DINAMIC_POSTFIX_TGHG,
    KEY_CHECK_ENTRY_DINAMIC_POSTFIX_TGHG,
    KEY_CHECK_INPUT_DINAMIC_POSTFIX_TGHG,
    KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_TGHG,
    KEY_COLLECTIONS_DINAMIC_POSTFIX_TGHG,
    KEY_DESCRIPTION_DINAMIC_POSTFIX_TGHG,
    KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_TGHG,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_TGHG,
    KEY_STARTER_CODE_DINAMIC_POSTFIX_TGHG,
    KEY_TASK_ID_DINAMIC_POSTFIX_TGHG,
    KEY_TITLE_DINAMIC_POSTFIX_TGHG,
    NEWLINE_DINAMIC_POSTFIX_VH2R,
    STATUS_CHECKING_DINAMIC_POSTFIX_TGHG,
    STATUS_FAILED_DINAMIC_POSTFIX_TGHG,
    STATUS_LINE_ELLIPSIS_DINAMIC_POSTFIX_TGHG,
    STATUS_PASSED_DINAMIC_POSTFIX_TGHG,
    STATUS_PENDING_DINAMIC_POSTFIX_TGHG,
    STATUS_TEXT_CHECKING_DINAMIC_POSTFIX_TGHG,
    STATUS_TEXT_FAILED_DINAMIC_POSTFIX_TGHG,
    STATUS_TEXT_PASSED_DINAMIC_POSTFIX_TGHG,
    STATUS_TEXT_PENDING_DINAMIC_POSTFIX_TGHG,
)

_DEFAULT_CHECK_TIMEOUT_SEC: Final[int] = 3
_DEFAULT_PER_TASK_MINUTES: Final[int] = 5

type TaskStatus = Literal["pending", "checking", "passed", "failed"]
type CheckInputMode = Literal["positional", "keyword"]
type CheckerEntryMode = Literal["strict", "hybrid"]

_FIRST_LINE_INDEX: Final[int] = 0
_SPLIT_MAX_PARTS: Final[int] = 1
_STATUS_LINE_MAX_CHARS: Final[int] = 120
_STATUS_LINE_TRIM_CHARS: Final[int] = _STATUS_LINE_MAX_CHARS - len(
    STATUS_LINE_ELLIPSIS_DINAMIC_POSTFIX_TGHG,
)

_DEFAULT_COLLECTIONS: Final[tuple[str, ...]] = ()


def _default_task_status() -> TaskStatus:
    """Default ``TaskStatus`` for a newly created task row.

    Returns:
        Pending status aligned with the catalog string.
    """
    return cast(TaskStatus, STATUS_PENDING_DINAMIC_POSTFIX_TGHG)


def _as_object_dict(value: object) -> dict[str, object]:
    """Convert a JSON-like mapping into ``dict[str, object]``.

    Args:
        value: Raw task payload section expected to be a ``dict``.

    Returns:
        A new dictionary with string keys.

    Raises:
        TypeError: When ``value`` is not a ``dict`` instance.
    """
    if not isinstance(value, dict):
        raise TypeError(ERR_EXPECTED_DICT_SECTION_DINAMIC_POSTFIX_TGHG)
    return {str(key): item for key, item in value.items()}


def _as_str_tuple(value: object) -> tuple[str, ...]:
    """Normalize collection name tags from a payload field.

    Args:
        value: Raw ``collections`` field from a task payload.

    Returns:
        Tuple of string tags, or an empty tuple when unsupported.
    """
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return _DEFAULT_COLLECTIONS


def _parse_check_entry(payload: dict[str, object]) -> str:
    """Read ``check_entry`` as a stripped callable name.

    Args:
        payload: Raw task payload dictionary.

    Returns:
        Stripped entry name, or empty text when missing or non-string.
    """
    raw = payload.get(KEY_CHECK_ENTRY_DINAMIC_POSTFIX_TGHG)
    return raw.strip() if isinstance(raw, str) else ""


def _parse_check_input_mode(payload: dict[str, object]) -> CheckInputMode:
    """Read ``check_input`` as positional or keyword mode.

    Args:
        payload: Raw task payload dictionary.

    Returns:
        ``\"keyword\"`` only when explicitly set; otherwise positional.
    """
    raw = payload.get(KEY_CHECK_INPUT_DINAMIC_POSTFIX_TGHG)
    if raw == CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_TGHG:
        return cast(
            CheckInputMode,
            CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_TGHG,
        )
    return cast(
        CheckInputMode,
        CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_TGHG,
    )


def _parse_check_input_kw(payload: dict[str, object]) -> str | None:
    """Read optional ``check_input_kw`` for keyword invocation.

    Args:
        payload: Raw task payload dictionary.

    Returns:
        Stripped parameter name, or ``None`` when absent or blank.
    """
    raw = payload.get(KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_TGHG)
    return raw.strip() if isinstance(raw, str) and raw.strip() else None


def _parse_starter_code(payload: dict[str, object]) -> str | None:
    """Read optional ``starter_code`` from the payload.

    Args:
        payload: Raw task payload dictionary.

    Returns:
        ``None`` when the key is absent; otherwise a string form of the
        stored value (possibly empty).
    """
    if KEY_STARTER_CODE_DINAMIC_POSTFIX_TGHG not in payload:
        return None
    raw = payload[KEY_STARTER_CODE_DINAMIC_POSTFIX_TGHG]
    return "" if raw is None else str(raw)


@dataclass(frozen=True)
class Task:
    """Immutable task definition decoded from a task-pack payload."""

    task_id: str
    title: str
    description: str
    input_data: dict[str, object]
    expected_result: object
    collections: tuple[str, ...]
    pack_name: str
    check_entry: str
    check_input: CheckInputMode
    check_input_kw: str | None
    starter_code: str | None = None

    @classmethod
    def from_payload(
        cls,
        payload: dict[str, object],
        *,
        pack_name: str,
    ) -> Task:
        """Build a :class:`Task` from one decoded payload object.

        Args:
            payload: Raw task payload from a task pack.
            pack_name: Identifier of the pack that produced the task.

        Returns:
            Normalized immutable task model.
        """
        return cls(
            task_id=str(payload[KEY_TASK_ID_DINAMIC_POSTFIX_TGHG]),
            title=str(payload[KEY_TITLE_DINAMIC_POSTFIX_TGHG]),
            description=str(
                payload.get(KEY_DESCRIPTION_DINAMIC_POSTFIX_TGHG, ""),
            ),
            input_data=_as_object_dict(
                payload[KEY_INPUT_DATA_DINAMIC_POSTFIX_TGHG],
            ),
            expected_result=payload[KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_TGHG],
            collections=_as_str_tuple(
                payload.get(
                    KEY_COLLECTIONS_DINAMIC_POSTFIX_TGHG,
                    _DEFAULT_COLLECTIONS,
                ),
            ),
            pack_name=pack_name,
            check_entry=_parse_check_entry(payload),
            check_input=_parse_check_input_mode(payload),
            check_input_kw=_parse_check_input_kw(payload),
            starter_code=_parse_starter_code(payload),
        )


@dataclass(frozen=True)
class SessionConfig:
    """Immutable session parameters: packs, count, timers, and flags."""

    selected_packs: tuple[str, ...]
    count: int
    seed: int | None
    strict_types: bool
    checker_entry_mode: CheckerEntryMode = "hybrid"
    check_timeout_sec: int = _DEFAULT_CHECK_TIMEOUT_SEC
    per_task_minutes: int = _DEFAULT_PER_TASK_MINUTES


@dataclass
class CheckResult:
    """Outcome of checking one learner submission for a single task."""

    task_index: int
    passed: bool
    actual_result: object | None = None
    error_text: str | None = None


@dataclass
class TaskState:
    """Mutable per-task UI and checker state inside a session."""

    status: TaskStatus = field(default_factory=_default_task_status)
    code: str = ""
    result: CheckResult | None = None


@dataclass
class TaskSession:
    """Session with immutable tasks and mutable per-task states."""

    config: SessionConfig
    tasks: list[Task]
    states: list[TaskState] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Populate ``states`` when the caller passes an empty list."""
        if not self.states:
            self.states = [TaskState() for _ in self.tasks]


@dataclass(frozen=True)
class TaskViewModel:
    """Read-only row model for the task list in the main window."""

    index: int
    task_id: str
    title: str
    pack_name: str
    status: TaskStatus
    status_line: str


def _trim_status_line(line: str) -> str:
    """Trim a status line to the configured maximum width.

    Args:
        line: Full single-line status text.

    Returns:
        Original text when short enough; otherwise truncated with an
        ellipsis suffix.
    """
    if len(line) <= _STATUS_LINE_MAX_CHARS:
        return line
    head = line[:_STATUS_LINE_TRIM_CHARS]
    return f"{head}{STATUS_LINE_ELLIPSIS_DINAMIC_POSTFIX_TGHG}"


def _first_line(text: str) -> str:
    """Return the first logical line of a multi-line string.

    Args:
        text: Arbitrary text, often a checker error block.

    Returns:
        Text before the first newline (after ``strip`` on the whole
        block).
    """
    return text.strip().split(
        NEWLINE_DINAMIC_POSTFIX_VH2R,
        _SPLIT_MAX_PARTS,
    )[_FIRST_LINE_INDEX]


def _failed_status_line(state: TaskState) -> str:
    """Build the status line for a failed task row.

    Args:
        state: Task state that must be ``failed``.

    Returns:
        First error line when present, else the generic failure label.
    """
    if state.result and state.result.error_text:
        return _trim_status_line(_first_line(state.result.error_text))
    return STATUS_TEXT_FAILED_DINAMIC_POSTFIX_TGHG


def _status_line_for_state(state: TaskState) -> str:
    """Map internal status to a one-line UI label.

    Args:
        state: Current task state.

    Returns:
        Short English text shown in the task list column.
    """
    if state.status == STATUS_CHECKING_DINAMIC_POSTFIX_TGHG:
        return STATUS_TEXT_CHECKING_DINAMIC_POSTFIX_TGHG
    if state.status == STATUS_PASSED_DINAMIC_POSTFIX_TGHG:
        return STATUS_TEXT_PASSED_DINAMIC_POSTFIX_TGHG
    if state.status == STATUS_FAILED_DINAMIC_POSTFIX_TGHG:
        return _failed_status_line(state)
    return STATUS_TEXT_PENDING_DINAMIC_POSTFIX_TGHG


def task_view_model(
    session: TaskSession,
    index: int,
) -> TaskViewModel:
    """Build one :class:`TaskViewModel` for ``session`` at ``index``.

    Args:
        session: Active task session.
        index: Zero-based task index.

    Returns:
        Immutable view row for UI binding.
    """
    task = session.tasks[index]
    state = session.states[index]
    return TaskViewModel(
        index=index,
        task_id=task.task_id,
        title=task.title,
        pack_name=task.pack_name,
        status=state.status,
        status_line=_status_line_for_state(state),
    )


def all_task_view_models(session: TaskSession) -> tuple[TaskViewModel, ...]:
    """Build view models for every task in session order.

    Args:
        session: Active task session.

    Returns:
        Tuple of rows aligned with ``session.tasks``.
    """
    return tuple(
        task_view_model(session=session, index=i)
        for i in range(len(session.tasks))
    )
