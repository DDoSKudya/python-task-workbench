"""
This module renders coding tasks to the terminal, including metadata,
input shape, optional examples, and step-by-step hints for learners.

It works by formatting Task objects into structured text blocks with
separators, titles, collections, constraints, descriptions, input data,
expected-result structure, and optionally previews and full reference
answers.

It defines constants for separator width, hint templates for beginners
and more detailed guidance, and parses a configured set of numbered
hint prefixes used to detect step-like lines in task descriptions.

Helper functions _joined, _non_empty_description_lines, and
_numbered_description_hints assemble human-readable lists
(collections/constraints) and extract meaningful and numbered hint lines
from the description text.

The step_hints function chooses which hints to show by preferring
explicit difficulty_hints, then numbered description lines, then
falling back to detail or beginner hint sets based on how long the
description is.

The main render_task function prints the task header and metadata, shows
the raw description and input, prints a structural signature of the
expected result, and conditionally prints hints, an example input/output
preview, and the full reference expected result depending on the
provided flags.
"""

from __future__ import annotations

from collections.abc import Sequence

from typing import Final

from generator.models import Task
from messages import (
    COMMA_SEPARATOR_DINAMIC_POSTFIX_SLAM,
    CONSTRAINTS_TEMPLATE_DINAMIC_POSTFIX_SLAM,
    EXPECTED_PREVIEW_HEADER_DINAMIC_POSTFIX_SLAM,
    EXPECTED_STRUCTURE_HEADER_DINAMIC_POSTFIX_SLAM,
    HINT_BEGINNER_LINE_1_DINAMIC_POSTFIX_SLAM,
    HINT_BEGINNER_LINE_2_DINAMIC_POSTFIX_SLAM,
    HINT_BEGINNER_LINE_3_DINAMIC_POSTFIX_SLAM,
    HINT_DETAIL_LINE_1_DINAMIC_POSTFIX_SLAM,
    HINT_DETAIL_LINE_2_DINAMIC_POSTFIX_SLAM,
    HINT_DETAIL_LINE_3_DINAMIC_POSTFIX_SLAM,
    HINT_LINE_TEMPLATE_DINAMIC_POSTFIX_SLAM,
    HINT_NUMBERED_PREFIXES_DINAMIC_POSTFIX_SLAM,
    HINT_PREFIX_SEPARATOR_DINAMIC_POSTFIX_SLAM,
    INPUT_HEADER_DINAMIC_POSTFIX_SLAM,
    INPUT_PREVIEW_HEADER_DINAMIC_POSTFIX_SLAM,
    REFERENCE_RESULT_HEADER_DINAMIC_POSTFIX_SLAM,
    RUN_EXAMPLE_HEADER_DINAMIC_POSTFIX_SLAM,
    SEPARATOR_CHAR_DINAMIC_POSTFIX_SLAM,
    STEP_HINTS_HEADER_DINAMIC_POSTFIX_SLAM,
    SUBSEPARATOR_CHAR_DINAMIC_POSTFIX_SLAM,
    TASK_HEADER_TEMPLATE_DINAMIC_POSTFIX_SLAM,
    TASK_META_TEMPLATE_DINAMIC_POSTFIX_SLAM,
)

from .formatting import preview_value, structure_signature, to_pretty

SEPARATOR_WIDTH: Final[int] = 80
ENUMERATE_START_INDEX: Final[int] = 1
BEGINNER_HINTS: Final[tuple[str, str, str]] = (
    HINT_BEGINNER_LINE_1_DINAMIC_POSTFIX_SLAM,
    HINT_BEGINNER_LINE_2_DINAMIC_POSTFIX_SLAM,
    HINT_BEGINNER_LINE_3_DINAMIC_POSTFIX_SLAM,
)
DETAIL_FALLBACK_HINTS: Final[tuple[str, str, str]] = (
    HINT_DETAIL_LINE_1_DINAMIC_POSTFIX_SLAM,
    HINT_DETAIL_LINE_2_DINAMIC_POSTFIX_SLAM,
    HINT_DETAIL_LINE_3_DINAMIC_POSTFIX_SLAM,
)
NUMBERED_HINT_PREFIXES: Final[frozenset[str]] = frozenset(
    HINT_NUMBERED_PREFIXES_DINAMIC_POSTFIX_SLAM.split(
        HINT_PREFIX_SEPARATOR_DINAMIC_POSTFIX_SLAM
    )
)
NUMBERED_HINT_PREFIX_LEN: Final[int] = 2
DETAIL_LINES_THRESHOLD: Final[int] = 3


def _joined(values: Sequence[str]) -> str:
    """Join textual values with configured comma separator.

    Args:
        values: Sequence of string values.

    Returns:
        Joined one-line string.
    """
    return COMMA_SEPARATOR_DINAMIC_POSTFIX_SLAM.join(values)


def _non_empty_description_lines(task: Task) -> list[str]:
    """Return stripped, non-empty lines from task description.

    Args:
        task: Task with description text.

    Returns:
        Ordered list of meaningful description lines.
    """
    return [
        line.strip() for line in task.description.splitlines() if line.strip()
    ]


def _numbered_description_hints(lines: Sequence[str]) -> list[str]:
    """Extract numbered hint lines from description lines.

    Args:
        lines: Pre-stripped description lines.

    Returns:
        Numbered lines that look like step hints.
    """
    return [
        line
        for line in lines
        if line[:NUMBERED_HINT_PREFIX_LEN] in NUMBERED_HINT_PREFIXES
    ]


def _print_example_block(task: Task) -> None:
    """Print preview input and expected result for a task.

    Args:
        task: Task to preview.

    Returns:
        None.
    """
    print(RUN_EXAMPLE_HEADER_DINAMIC_POSTFIX_SLAM)
    print(INPUT_PREVIEW_HEADER_DINAMIC_POSTFIX_SLAM)
    print(to_pretty(preview_value(task.input_data)))
    print(EXPECTED_PREVIEW_HEADER_DINAMIC_POSTFIX_SLAM)
    print(to_pretty(preview_value(task.expected_result)))


def _print_hints(task: Task) -> None:
    """Print numbered step hints for a task.

    Args:
        task: Task that provides hint sources.

    Returns:
        None.
    """
    print(STEP_HINTS_HEADER_DINAMIC_POSTFIX_SLAM)
    for idx, hint in enumerate(step_hints(task), start=ENUMERATE_START_INDEX):
        print(
            HINT_LINE_TEMPLATE_DINAMIC_POSTFIX_SLAM.format(
                index=idx, hint=hint
            )
        )


def step_hints(task: Task) -> list[str]:
    """Return step-by-step hints from task metadata or description.

    Args:
        task: Task with optional metadata hints and description.

    Returns:
        Ordered hints for terminal guidance.
    """
    if task.difficulty_hints:
        return list(task.difficulty_hints)
    description_lines = _non_empty_description_lines(task)
    numbered = _numbered_description_hints(description_lines)
    if numbered:
        return numbered
    if len(description_lines) >= DETAIL_LINES_THRESHOLD:
        return list(DETAIL_FALLBACK_HINTS)
    return list(BEGINNER_HINTS)


def render_task(
    task: Task,
    *,
    index: int,
    show_solution: bool,
    show_full_example: bool,
    hints_step: bool,
) -> None:
    """Print a task to the terminal.

    Args:
        task: Task to render.
        index: 1-based index in the current batch.
        show_solution: If True, prints the reference result.
        show_full_example: If True, prints input/output previews.
        hints_step: If True, prints step-by-step hints.

    Returns:
        None.
    """
    print(SEPARATOR_CHAR_DINAMIC_POSTFIX_SLAM * SEPARATOR_WIDTH)
    print(
        TASK_HEADER_TEMPLATE_DINAMIC_POSTFIX_SLAM.format(
            index=index, title=task.title
        )
    )
    collections_text = _joined(task.collections)
    print(
        TASK_META_TEMPLATE_DINAMIC_POSTFIX_SLAM.format(
            task_id=task.task_id, collections=collections_text
        )
    )
    if task.constraints:
        constraints_text = _joined(task.constraints)
        print(
            CONSTRAINTS_TEMPLATE_DINAMIC_POSTFIX_SLAM.format(
                constraints=constraints_text
            )
        )
    print(SUBSEPARATOR_CHAR_DINAMIC_POSTFIX_SLAM * SEPARATOR_WIDTH)
    print(task.description)
    print(INPUT_HEADER_DINAMIC_POSTFIX_SLAM)
    print(to_pretty(task.input_data))
    print(EXPECTED_STRUCTURE_HEADER_DINAMIC_POSTFIX_SLAM)
    print(structure_signature(task.expected_result))
    if hints_step:
        _print_hints(task)
    if show_full_example:
        _print_example_block(task)
    if show_solution:
        print(REFERENCE_RESULT_HEADER_DINAMIC_POSTFIX_SLAM)
        print(to_pretty(task.expected_result))
