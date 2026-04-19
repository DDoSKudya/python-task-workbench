"""
This module generates a Python “solution template” file for a batch of
tasks, giving learners pre-filled metadata, stub solution functions,
and a simple local preview harness.

It works by converting each Task into a serializable payload,
pretty-printing the task list and IDs, generating numbered function
stubs and corresponding answer-call lines, and assembling them into a
single source file written to disk.

It defines formatting constants for pretty-print width, list and
separator syntax, indentation, and docstring lines, plus type aliases
and helper functions to build task payloads and extract task IDs.

The _functions_and_answers and _function_block helpers create per-task
solution functions and ANSWERS list entries that call those functions
with the correct task index into the tasks payload.

The _content_lines and _main_block_lines helpers construct the full
template source, including module-level metadata, tasks and answers
lists, and an if __name__ == "__main__" block that prints each task and
its computed result for quick manual checking.

The public function write_solution_template orchestrates these pieces:
it builds the payload and IDs from the generated tasks, formats them
with pprint, generates all code blocks, joins lines with double line
breaks, and writes the final template file using the configured
encoding.
"""

from __future__ import annotations

import pprint
from collections.abc import Sequence

from pathlib import Path
from typing import Final

from generator.models import Task
from generator.settings import DEFAULT_STATE_FILE
from messages import (
    ANSWER_CALL_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
    ANSWERS_LIST_NAME_DINAMIC_POSTFIX_1J4Y,
    DOUBLE_LINE_BREAK_DINAMIC_POSTFIX_1J4Y,
    EMPTY_LINE_DINAMIC_POSTFIX_1J4Y,
    FINAL_ANSWERS_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
    IF_MAIN_LINE_DINAMIC_POSTFIX_1J4Y,
    LINE_BREAK_DINAMIC_POSTFIX_1J4Y,
    LOCAL_CHECK_HEADER_LINE_DINAMIC_POSTFIX_1J4Y,
    RESULT_LINE_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
    SEPARATOR_CHAR_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_FUNCTION_DEF_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_FUNCTION_DOCSTRING_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_FUNCTION_NAME_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_FUNCTION_RETURN_LINE_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_FUNCTION_TODO_LINE_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_TEMPLATE_DOCSTRING_LINE_1_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_TEMPLATE_DOCSTRING_LINE_2_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_TEMPLATE_DOCSTRING_LINE_3_DINAMIC_POSTFIX_1J4Y,
    STATE_FILE_NAME_DINAMIC_POSTFIX_1J4Y,
    SUBSEPARATOR_CHAR_DINAMIC_POSTFIX_1J4Y,
    TASK_FIELD_COLLECTIONS_DINAMIC_POSTFIX_1J4Y,
    TASK_FIELD_DESCRIPTION_DINAMIC_POSTFIX_1J4Y,
    TASK_FIELD_ID_DINAMIC_POSTFIX_1J4Y,
    TASK_FIELD_INDEX_DINAMIC_POSTFIX_1J4Y,
    TASK_FIELD_INPUT_DATA_DINAMIC_POSTFIX_1J4Y,
    TASK_FIELD_TITLE_DINAMIC_POSTFIX_1J4Y,
    TASK_HEADER_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
    TASK_IDS_NAME_DINAMIC_POSTFIX_1J4Y,
    TASK_LOOP_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
    TASK_VAR_NAME_DINAMIC_POSTFIX_1J4Y,
    TASKS_LIST_NAME_DINAMIC_POSTFIX_1J4Y,
    TEMPLATE_ENCODING_DINAMIC_POSTFIX_1J4Y,
)

PPRINT_WIDTH: Final[int] = 79
DEFAULT_TASK_INDEX_OFFSET: Final[int] = 1
FIRST_INDEX: Final[int] = 1
INDEX_TO_LIST_OFFSET: Final[int] = 1
SEPARATOR_WIDTH: Final[int] = 79
INDENT_UNIT: Final[str] = "    "
LIST_OPEN: Final[str] = "["
LIST_CLOSE: Final[str] = "]"
type TaskPayload = dict[str, object]

TEMPLATE_DOCSTRING_LINES: Final[tuple[str, ...]] = (
    '"""',
    SOLUTION_TEMPLATE_DOCSTRING_LINE_1_DINAMIC_POSTFIX_1J4Y,
    "",
    SOLUTION_TEMPLATE_DOCSTRING_LINE_2_DINAMIC_POSTFIX_1J4Y,
    SOLUTION_TEMPLATE_DOCSTRING_LINE_3_DINAMIC_POSTFIX_1J4Y,
    "",
    '"""',
)
SOLUTION_FUNCTION_DOCSTRING_LINES: Final[tuple[str, ...]] = (
    SOLUTION_FUNCTION_DOCSTRING_DINAMIC_POSTFIX_1J4Y,
)


def _task_payload(generated: Sequence[Task]) -> list[TaskPayload]:
    """Build serializable payload rows for template data section.

    Args:
        generated: Generated tasks in order.

    Returns:
        List of task payload dictionaries.
    """
    return [
        {
            TASK_FIELD_INDEX_DINAMIC_POSTFIX_1J4Y: idx
            + DEFAULT_TASK_INDEX_OFFSET,
            TASK_FIELD_ID_DINAMIC_POSTFIX_1J4Y: task.task_id,
            TASK_FIELD_TITLE_DINAMIC_POSTFIX_1J4Y: task.title,
            TASK_FIELD_DESCRIPTION_DINAMIC_POSTFIX_1J4Y: task.description,
            TASK_FIELD_COLLECTIONS_DINAMIC_POSTFIX_1J4Y: list(
                task.collections
            ),
            TASK_FIELD_INPUT_DATA_DINAMIC_POSTFIX_1J4Y: task.input_data,
        }
        for idx, task in enumerate(generated)
    ]


def _task_ids(generated: Sequence[Task]) -> list[str]:
    """Extract task identifiers in generation order.

    Args:
        generated: Generated tasks in order.

    Returns:
        List of task ids.
    """
    return [task.task_id for task in generated]


def _function_block(function_name: str) -> str:
    """Build one solution-function source block.

    Args:
        function_name: Target function name.

    Returns:
        Multi-line function block string.
    """
    lines = [
        SOLUTION_FUNCTION_DEF_TEMPLATE_DINAMIC_POSTFIX_1J4Y.format(
            name=function_name
        ),
        *SOLUTION_FUNCTION_DOCSTRING_LINES,
        SOLUTION_FUNCTION_TODO_LINE_DINAMIC_POSTFIX_1J4Y,
        SOLUTION_FUNCTION_RETURN_LINE_DINAMIC_POSTFIX_1J4Y,
    ]
    return LINE_BREAK_DINAMIC_POSTFIX_1J4Y.join(lines)


def _functions_and_answers(
    generated: Sequence[Task],
) -> tuple[list[str], list[str]]:
    """Build function blocks and answer-call lines.

    Args:
        generated: Generated tasks in order.

    Returns:
        Tuple ``(function_blocks, answer_lines)``.
    """
    function_blocks: list[str] = []
    answer_lines: list[str] = []
    for idx, _ in enumerate(generated, start=FIRST_INDEX):
        function_name = (
            SOLUTION_FUNCTION_NAME_TEMPLATE_DINAMIC_POSTFIX_1J4Y.format(
                index=idx
            )
        )
        function_blocks.append(_function_block(function_name))
        answer_lines.append(
            ANSWER_CALL_TEMPLATE_DINAMIC_POSTFIX_1J4Y.format(
                name=function_name,
                tasks_name=TASKS_LIST_NAME_DINAMIC_POSTFIX_1J4Y,
                task_index=idx - INDEX_TO_LIST_OFFSET,
            )
        )
    return (function_blocks, answer_lines)


def _content_lines(
    *,
    task_rows: str,
    task_ids: list[str],
    function_blocks: list[str],
    answer_lines: list[str],
) -> list[str]:
    """Build full template file content as line list.

    Args:
        task_rows: Pretty-printed tasks payload literal.
        task_ids: Task ids for metadata section.
        function_blocks: Generated solution function source blocks.
        answer_lines: Calls used to fill ``ANSWERS``.

    Returns:
        Ordered file lines ready for final join.
    """
    return [
        *TEMPLATE_DOCSTRING_LINES,
        EMPTY_LINE_DINAMIC_POSTFIX_1J4Y,
        f"{STATE_FILE_NAME_DINAMIC_POSTFIX_1J4Y} = {DEFAULT_STATE_FILE!r}",
        f"{TASK_IDS_NAME_DINAMIC_POSTFIX_1J4Y} = {task_ids!r}",
        EMPTY_LINE_DINAMIC_POSTFIX_1J4Y,
        f"{TASKS_LIST_NAME_DINAMIC_POSTFIX_1J4Y} = {task_rows}",
        EMPTY_LINE_DINAMIC_POSTFIX_1J4Y,
        *function_blocks,
        EMPTY_LINE_DINAMIC_POSTFIX_1J4Y,
        f"{ANSWERS_LIST_NAME_DINAMIC_POSTFIX_1J4Y} = {LIST_OPEN}",
        *answer_lines,
        LIST_CLOSE,
        EMPTY_LINE_DINAMIC_POSTFIX_1J4Y,
        *_main_block_lines(),
        EMPTY_LINE_DINAMIC_POSTFIX_1J4Y,
    ]


def _main_block_lines() -> list[str]:
    """Build ``if __name__ == \"__main__\"`` template block lines.

    Returns:
        Ordered source lines for local answer preview execution.
    """
    line_indent = INDENT_UNIT
    nested_indent = f"{INDENT_UNIT}{INDENT_UNIT}"
    answers_preview = FINAL_ANSWERS_TEMPLATE_DINAMIC_POSTFIX_1J4Y.format(
        answers_name=ANSWERS_LIST_NAME_DINAMIC_POSTFIX_1J4Y,
    )
    return [
        IF_MAIN_LINE_DINAMIC_POSTFIX_1J4Y,
        (
            f"{line_indent}print("
            f"{SEPARATOR_CHAR_DINAMIC_POSTFIX_1J4Y!r} * {SEPARATOR_WIDTH})"
        ),
        f"{line_indent}print({LOCAL_CHECK_HEADER_LINE_DINAMIC_POSTFIX_1J4Y!r})",
        (
            f"{line_indent}print("
            f"{SEPARATOR_CHAR_DINAMIC_POSTFIX_1J4Y!r} * {SEPARATOR_WIDTH})"
        ),
        TASK_LOOP_TEMPLATE_DINAMIC_POSTFIX_1J4Y.format(
            tasks_name=TASKS_LIST_NAME_DINAMIC_POSTFIX_1J4Y
        ),
        (
            f"{nested_indent}idx = "
            f"{TASK_VAR_NAME_DINAMIC_POSTFIX_1J4Y}"
            f"[{TASK_FIELD_INDEX_DINAMIC_POSTFIX_1J4Y!r}]"
        ),
        (
            f"{nested_indent}task_id = "
            f"{TASK_VAR_NAME_DINAMIC_POSTFIX_1J4Y}"
            f"[{TASK_FIELD_ID_DINAMIC_POSTFIX_1J4Y!r}]"
        ),
        (
            f"{nested_indent}title = "
            f"{TASK_VAR_NAME_DINAMIC_POSTFIX_1J4Y}"
            f"[{TASK_FIELD_TITLE_DINAMIC_POSTFIX_1J4Y!r}]"
        ),
        TASK_HEADER_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
        (
            f"{nested_indent}result = "
            f"{ANSWERS_LIST_NAME_DINAMIC_POSTFIX_1J4Y}"
            f"[idx - {INDEX_TO_LIST_OFFSET}]"
        ),
        RESULT_LINE_TEMPLATE_DINAMIC_POSTFIX_1J4Y,
        (
            f"{nested_indent}print("
            f"{SUBSEPARATOR_CHAR_DINAMIC_POSTFIX_1J4Y!r} * {SEPARATOR_WIDTH})"
        ),
        f"{line_indent}print({answers_preview!r})",
        f"{line_indent}print({ANSWERS_LIST_NAME_DINAMIC_POSTFIX_1J4Y})",
    ]


def write_solution_template(
    generated: Sequence[Task], solution_file: str
) -> None:
    """Write a solution template file for the generated tasks.

    Args:
        generated: Generated tasks in order.
        solution_file: Target file path.

    Returns:
        None.
    """
    path = Path(solution_file)
    tasks_payload = _task_payload(generated)
    task_ids = _task_ids(generated)
    task_rows = pprint.pformat(
        tasks_payload, width=PPRINT_WIDTH, sort_dicts=False
    )
    function_blocks, answer_lines = _functions_and_answers(generated)
    content_lines = _content_lines(
        task_rows=task_rows,
        task_ids=task_ids,
        function_blocks=function_blocks,
        answer_lines=answer_lines,
    )
    path.write_text(
        DOUBLE_LINE_BREAK_DINAMIC_POSTFIX_1J4Y.join(content_lines),
        encoding=TEMPLATE_ENCODING_DINAMIC_POSTFIX_1J4Y,
    )
