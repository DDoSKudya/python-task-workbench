"""
This module exports generated tasks to disk either as a human-readable
Markdown document or as a pytest-ready Python file, depending on
application configuration.

It works by converting each Task into a serializable payload, choosing
an output path and format based on AppConfig, rendering the payload
list into text, and writing the result with UTF-8 encoding.

It defines constants for required pytest keys, pretty-print width, index
offsets, path separators, and many message-driven templates and keys
used to structure the exported content.

The task_to_payload function flattens a Task into a dictionary of
primitive values and lists, including metadata such as collections,
constraints, hints, pitfalls, analogy, complexity, input data, and
check-related fields.

The export_tasks function orchestrates the export flow, short-circuiting
when export is disabled, computing the destination filename, building
per-task payloads, rendering either pytest or Markdown text via
_render_export_content, and returning the resulting file path as a
string.

Helper functions _render_pytest and _render_markdown generate
format-specific output, while _render_markdown_task constructs the
per-task Markdown block including headers, metadata lines, description,
and a fenced code block showing pretty-printed input data.

Utility helpers like _string_list, _format_constraints, _int_field,
_str_field, and _dict_field sanitize and normalize payload values so
that missing or oddly typed fields degrade gracefully in the exported
files.
"""

from __future__ import annotations

import pprint
from collections.abc import Iterable, Sequence

from pathlib import Path
from typing import Final

from generator.app_config import AppConfig
from generator.models import Task
from messages import (
    CODE_BLOCK_FENCE_DINAMIC_POSTFIX_Y8BW,
    CODE_BLOCK_LANGUAGE_DINAMIC_POSTFIX_Y8BW,
    DEFAULT_MARKDOWN_FILENAME_DINAMIC_POSTFIX_Y8BW,
    DEFAULT_PYTEST_FILENAME_DINAMIC_POSTFIX_Y8BW,
    EMPTY_CONSTRAINTS_FALLBACK_DINAMIC_POSTFIX_Y8BW,
    EMPTY_STRING_DINAMIC_POSTFIX_Y8BW,
    EMPTY_VALUE_FALLBACK_DINAMIC_POSTFIX_Y8BW,
    ENCODING_UTF8_DINAMIC_POSTFIX_Y8BW,
    EXPORT_FORMAT_MARKDOWN_DINAMIC_POSTFIX_Y8BW,
    EXPORT_FORMAT_NONE_DINAMIC_POSTFIX_Y8BW,
    EXPORT_FORMAT_PYTEST_DINAMIC_POSTFIX_Y8BW,
    KEY_ANALOGY_DINAMIC_POSTFIX_Y8BW,
    KEY_CHECK_ENTRY_DINAMIC_POSTFIX_Y8BW,
    KEY_CHECK_INPUT_DINAMIC_POSTFIX_Y8BW,
    KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_Y8BW,
    KEY_COLLECTIONS_DINAMIC_POSTFIX_Y8BW,
    KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_Y8BW,
    KEY_COMPLEXITY_DINAMIC_POSTFIX_Y8BW,
    KEY_CONSTRAINTS_DINAMIC_POSTFIX_Y8BW,
    KEY_DESCRIPTION_DINAMIC_POSTFIX_Y8BW,
    KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_Y8BW,
    KEY_INDEX_DINAMIC_POSTFIX_Y8BW,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_Y8BW,
    KEY_STARTER_CODE_DINAMIC_POSTFIX_Y8BW,
    KEY_TASK_ID_DINAMIC_POSTFIX_Y8BW,
    KEY_TITLE_DINAMIC_POSTFIX_Y8BW,
    MARKDOWN_COLLECTIONS_TEMPLATE_DINAMIC_POSTFIX_Y8BW,
    MARKDOWN_COMPLEXITY_TEMPLATE_DINAMIC_POSTFIX_Y8BW,
    MARKDOWN_CONSTRAINTS_TEMPLATE_DINAMIC_POSTFIX_Y8BW,
    MARKDOWN_ID_TEMPLATE_DINAMIC_POSTFIX_Y8BW,
    MARKDOWN_TASK_HEADER_TEMPLATE_DINAMIC_POSTFIX_Y8BW,
    MARKDOWN_TITLE_DINAMIC_POSTFIX_Y8BW,
    NEWLINE_DINAMIC_POSTFIX_Y8BW,
    PYTEST_TASKS_VAR_DINAMIC_POSTFIX_Y8BW,
    PYTEST_TEST_FUNC_NAME_DINAMIC_POSTFIX_Y8BW,
)

from .formatting import to_pretty

PYTEST_REQUIRED_KEYS: Final[tuple[str, str, str]] = (
    KEY_TASK_ID_DINAMIC_POSTFIX_Y8BW,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_Y8BW,
    KEY_DESCRIPTION_DINAMIC_POSTFIX_Y8BW,
)
PFORMAT_WIDTH: Final[int] = 79
PAYLOAD_INDEX_START: Final[int] = 1
PATH_STR_SEPARATOR: Final[str] = ", "
PYTEST_REQUIRED_KEY_TEMPLATE: Final[str] = "{key!r} in task"
type TaskPayload = dict[str, object]


def task_to_payload(task: Task, index: int) -> TaskPayload:
    """Convert a task into a serializable export payload.

    Args:
        task: Task instance.
        index: One-based index in the exported list.

    Returns:
        A payload dictionary suitable for Markdown and pytest exports.
    """
    out: TaskPayload = {
        KEY_INDEX_DINAMIC_POSTFIX_Y8BW: index,
        KEY_TASK_ID_DINAMIC_POSTFIX_Y8BW: task.task_id,
        KEY_TITLE_DINAMIC_POSTFIX_Y8BW: task.title,
        KEY_DESCRIPTION_DINAMIC_POSTFIX_Y8BW: task.description,
        KEY_COLLECTIONS_DINAMIC_POSTFIX_Y8BW: list(task.collections),
        KEY_CONSTRAINTS_DINAMIC_POSTFIX_Y8BW: list(task.constraints),
        KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_Y8BW: list(task.difficulty_hints),
        KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_Y8BW: list(task.common_pitfalls),
        KEY_ANALOGY_DINAMIC_POSTFIX_Y8BW: task.real_world_analogy,
        KEY_COMPLEXITY_DINAMIC_POSTFIX_Y8BW: task.estimated_complexity,
        KEY_INPUT_DATA_DINAMIC_POSTFIX_Y8BW: task.input_data,
    }
    if task.starter_code is not None:
        out[KEY_STARTER_CODE_DINAMIC_POSTFIX_Y8BW] = task.starter_code
    out[KEY_CHECK_ENTRY_DINAMIC_POSTFIX_Y8BW] = task.check_entry
    out[KEY_CHECK_INPUT_DINAMIC_POSTFIX_Y8BW] = task.check_input
    out[KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_Y8BW] = task.check_input_kw
    return out


def export_tasks(generated: list[Task], config: AppConfig) -> str | None:
    """Export generated tasks to a file based on config settings.

    Args:
        generated: Generated tasks in order.
        config: Application config containing export settings.

    Returns:
        Path to the exported file as a string, or None when export is
        disabled.
    """
    if config.export_format == EXPORT_FORMAT_NONE_DINAMIC_POSTFIX_Y8BW:
        return None
    export_path = _resolve_export_path(config)
    payloads = [
        task_to_payload(task, idx)
        for idx, task in enumerate(generated, start=PAYLOAD_INDEX_START)
    ]
    output = _render_export_content(
        payloads=payloads,
        export_format=config.export_format,
    )
    export_path.write_text(
        output,
        encoding=ENCODING_UTF8_DINAMIC_POSTFIX_Y8BW,
    )
    return str(export_path)


def _render_export_content(
    *, payloads: list[TaskPayload], export_format: str
) -> str:
    """Render export content for a requested format.

    Args:
        payloads: Prepared task payloads.
        export_format: Export format requested by config.

    Returns:
        Full text content for the export file.
    """
    if export_format == EXPORT_FORMAT_PYTEST_DINAMIC_POSTFIX_Y8BW:
        return _render_pytest(payloads)
    return _render_markdown(payloads)


def _resolve_export_path(config: AppConfig) -> Path:
    """Resolve the export destination path.

    Args:
        config: Application config containing export file settings.

    Returns:
        Destination path for the export.
    """
    default_name = (
        DEFAULT_MARKDOWN_FILENAME_DINAMIC_POSTFIX_Y8BW
        if config.export_format == EXPORT_FORMAT_MARKDOWN_DINAMIC_POSTFIX_Y8BW
        else DEFAULT_PYTEST_FILENAME_DINAMIC_POSTFIX_Y8BW
    )
    if config.export_file:
        return Path(config.export_file)
    return Path(config.state_file).with_name(default_name)


def _render_pytest(payload: list[TaskPayload]) -> str:
    """Render payload into a pytest-compatible Python file.

    Args:
        payload: Payload list.

    Returns:
        Full file contents as a string.
    """
    payload_repr = pprint.pformat(
        payload, width=PFORMAT_WIDTH, sort_dicts=False
    )
    required_checks = " and ".join(
        PYTEST_REQUIRED_KEY_TEMPLATE.format(key=key)
        for key in PYTEST_REQUIRED_KEYS
    )
    lines = [
        f"{PYTEST_TASKS_VAR_DINAMIC_POSTFIX_Y8BW} = {payload_repr}",
        EMPTY_STRING_DINAMIC_POSTFIX_Y8BW,
        f"def {PYTEST_TEST_FUNC_NAME_DINAMIC_POSTFIX_Y8BW}():",
        (
            f"    assert isinstance({PYTEST_TASKS_VAR_DINAMIC_POSTFIX_Y8BW}, "
            f"list) and {PYTEST_TASKS_VAR_DINAMIC_POSTFIX_Y8BW}"
        ),
        f"    for task in {PYTEST_TASKS_VAR_DINAMIC_POSTFIX_Y8BW}:",
        f"        assert {required_checks}",
        EMPTY_STRING_DINAMIC_POSTFIX_Y8BW,
    ]
    return NEWLINE_DINAMIC_POSTFIX_Y8BW.join(lines)


def _render_markdown(payload: list[TaskPayload]) -> str:
    """Render payload into a human-readable Markdown document.

    Args:
        payload: Payload list.

    Returns:
        Full Markdown contents as a string.
    """
    lines: list[str] = [
        MARKDOWN_TITLE_DINAMIC_POSTFIX_Y8BW,
        EMPTY_STRING_DINAMIC_POSTFIX_Y8BW,
    ]
    for item in payload:
        lines.extend(_render_markdown_task(item))
    return NEWLINE_DINAMIC_POSTFIX_Y8BW.join(lines)


def _render_markdown_task(item: TaskPayload) -> Iterable[str]:
    """Render a single task payload into Markdown lines.

    Args:
        item: Task payload.

    Returns:
        Iterable of Markdown lines.
    """
    index = _int_field(item, KEY_INDEX_DINAMIC_POSTFIX_Y8BW)
    task_id = _str_field(item, KEY_TASK_ID_DINAMIC_POSTFIX_Y8BW)
    description = _str_field(item, KEY_DESCRIPTION_DINAMIC_POSTFIX_Y8BW)
    collections = PATH_STR_SEPARATOR.join(
        _string_list(item.get(KEY_COLLECTIONS_DINAMIC_POSTFIX_Y8BW))
    )
    constraints = _format_constraints(
        _string_list(item.get(KEY_CONSTRAINTS_DINAMIC_POSTFIX_Y8BW))
    )
    complexity = (
        item.get(KEY_COMPLEXITY_DINAMIC_POSTFIX_Y8BW)
        or EMPTY_VALUE_FALLBACK_DINAMIC_POSTFIX_Y8BW
    )
    input_data = _dict_field(item, KEY_INPUT_DATA_DINAMIC_POSTFIX_Y8BW)
    return [
        MARKDOWN_TASK_HEADER_TEMPLATE_DINAMIC_POSTFIX_Y8BW.format(index=index),
        MARKDOWN_ID_TEMPLATE_DINAMIC_POSTFIX_Y8BW.format(task_id=task_id),
        MARKDOWN_COLLECTIONS_TEMPLATE_DINAMIC_POSTFIX_Y8BW.format(
            collections=collections
        ),
        MARKDOWN_COMPLEXITY_TEMPLATE_DINAMIC_POSTFIX_Y8BW.format(
            complexity=complexity
        ),
        MARKDOWN_CONSTRAINTS_TEMPLATE_DINAMIC_POSTFIX_Y8BW.format(
            constraints=constraints
        ),
        EMPTY_STRING_DINAMIC_POSTFIX_Y8BW,
        description,
        EMPTY_STRING_DINAMIC_POSTFIX_Y8BW,
        (
            f"{CODE_BLOCK_FENCE_DINAMIC_POSTFIX_Y8BW}"
            f"{CODE_BLOCK_LANGUAGE_DINAMIC_POSTFIX_Y8BW}"
        ),
        to_pretty(input_data),
        CODE_BLOCK_FENCE_DINAMIC_POSTFIX_Y8BW,
        EMPTY_STRING_DINAMIC_POSTFIX_Y8BW,
    ]


def _string_list(value: object) -> list[str]:
    """Convert a payload value to a list of strings.

    Args:
        value: Payload value.

    Returns:
        List of strings.
    """
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return []


def _format_constraints(constraints: list[str]) -> str:
    """Format constraints for Markdown output.

    Args:
        constraints: Constraints list.

    Returns:
        Human-readable string.
    """
    return (
        PATH_STR_SEPARATOR.join(constraints)
        if constraints
        else EMPTY_CONSTRAINTS_FALLBACK_DINAMIC_POSTFIX_Y8BW
    )


def _int_field(item: TaskPayload, key: str) -> int:
    """Read an integer field from a task payload.

    Args:
        item: Task payload.
        key: Key to read.

    Returns:
        Integer value.
    """
    raw = item.get(key)
    return raw if isinstance(raw, int) else int(str(raw))


def _str_field(item: TaskPayload, key: str) -> str:
    """Read a string field from a task payload.

    Args:
        item: Task payload.
        key: Key to read.

    Returns:
        String value.
    """
    return str(item.get(key, EMPTY_STRING_DINAMIC_POSTFIX_Y8BW))


def _dict_field(item: TaskPayload, key: str) -> dict[str, object]:
    """Read a dict-like field from a task payload.

    Args:
        item: Task payload.
        key: Key to read.

    Returns:
        Dictionary value, or an empty dict.
    """
    raw = item.get(key)
    return raw if isinstance(raw, dict) else {}
