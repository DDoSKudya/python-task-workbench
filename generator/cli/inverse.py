"""
This module generates “inverse” variants of certain tasks by turning
aggregated expected results into flat record-based outputs.

It works by detecting tasks whose expected result is a non-empty mapping
from group keys to sequences of values and whose input data has exactly
one key, then constructing a new task that expects the aggregated
mapping as input and a flattened list of {group, value} rows as the
expected result.

It defines type aliases for aggregated mappings and restored rows, a
constant for the required input key count, and helper type guards
(_is_non_string_sequence, _is_aggregated_mapping, _aggregated_mapping)
to validate candidate tasks.

The _restored_rows helper expands the aggregated mapping into a list of
rows tagged with group and value, and sorts them deterministically
using _row_sort_key to ensure stable ordering.

The main function inverse_task returns either a new Task created via
dataclasses.replace with updated IDs, title suffix, fixed inverse
description, input/expected-result swap, pattern, and complexity, or
None when the original task cannot be safely inverted.

Within the larger system, this module supports “inverse mode”
generation, allowing some tasks to be flipped so that learners practice
reconstructing detailed records from aggregated data.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from dataclasses import replace
from typing import Final, TypeGuard

from generator.models import Task
from messages import (
    INVERSE_DESCRIPTION_DINAMIC_POSTFIX_EX6W,
    INVERSE_ESTIMATED_COMPLEXITY_DINAMIC_POSTFIX_EX6W,
    INVERSE_INPUT_KEY_DINAMIC_POSTFIX_EX6W,
    INVERSE_PATTERN_DINAMIC_POSTFIX_EX6W,
    INVERSE_TASK_ID_SUFFIX_DINAMIC_POSTFIX_EX6W,
    INVERSE_TITLE_SUFFIX_DINAMIC_POSTFIX_EX6W,
    OUTPUT_GROUP_KEY_DINAMIC_POSTFIX_EX6W,
    OUTPUT_VALUE_KEY_DINAMIC_POSTFIX_EX6W,
)

REQUIRED_INPUT_KEYS_COUNT: Final[int] = 1
type AggregatedMapping = Mapping[object, Sequence[object]]
type RestoredRow = dict[str, object]


def _is_non_string_sequence(value: object) -> TypeGuard[Sequence[object]]:
    """Return whether value is a sequence excluding string-like types.

    Args:
        value: Candidate value.

    Returns:
        ``True`` when value is ``Sequence[object]`` and not text/bytes.
    """
    if isinstance(value, (str, bytes, bytearray)):
        return False
    return isinstance(value, Sequence)


def _is_aggregated_mapping(value: object) -> TypeGuard[AggregatedMapping]:
    """Return whether value is a non-empty aggregated mapping.

    Args:
        value: Candidate expected-result value.

    Returns:
        ``True`` for non-empty mappings where all values are sequences.
    """
    if not isinstance(value, Mapping) or not value:
        return False
    return all(_is_non_string_sequence(item) for item in value.values())


def _aggregated_mapping(value: object) -> AggregatedMapping | None:
    """Validate expected result as aggregated mapping of sequences.

    Args:
        value: Candidate expected result from the source task.

    Returns:
        Aggregated mapping when valid and non-empty, else ``None``.
    """
    return value if _is_aggregated_mapping(value) else None


def _row_sort_key(row: RestoredRow) -> tuple[str, str]:
    """Build stable sorting key for a restored row.

    Args:
        row: Row in ``{group, value}`` form.

    Returns:
        Tuple key used for deterministic ordering.
    """
    return (
        str(row[OUTPUT_GROUP_KEY_DINAMIC_POSTFIX_EX6W]),
        str(row[OUTPUT_VALUE_KEY_DINAMIC_POSTFIX_EX6W]),
    )


def _restored_rows(aggregated: AggregatedMapping) -> list[RestoredRow]:
    """Restore flat rows from aggregated mapping.

    Args:
        aggregated: Mapping from group key to sequence of values.

    Returns:
        Sorted list of rows in ``{group, value}`` shape.
    """
    restored: list[RestoredRow] = []
    for group_key, values in aggregated.items():
        restored.extend(
            {
                OUTPUT_GROUP_KEY_DINAMIC_POSTFIX_EX6W: group_key,
                OUTPUT_VALUE_KEY_DINAMIC_POSTFIX_EX6W: value,
            }
            for value in values
        )
    restored.sort(key=_row_sort_key)
    return restored


def inverse_task(task: Task) -> Task | None:
    """Build an inverse version of an aggregated task.

    The inverse task expects aggregated data as the input and requires
    the solver to reconstruct a flat list of records in the
    ``{group: <key>, value: <item>}`` form.

    Args:
        task: Source task to invert.

    Returns:
        A new task instance with adjusted input and expected result,
        or ``None`` if the task cannot be inverted safely.
    """
    if len(task.input_data) != REQUIRED_INPUT_KEYS_COUNT:
        return None
    aggregated = _aggregated_mapping(task.expected_result)
    if aggregated is None:
        return None
    restored = _restored_rows(aggregated)
    if not restored:
        return None
    inverse_input = {INVERSE_INPUT_KEY_DINAMIC_POSTFIX_EX6W: aggregated}
    return replace(
        task,
        task_id=f"{task.task_id}{INVERSE_TASK_ID_SUFFIX_DINAMIC_POSTFIX_EX6W}",
        title=f"{task.title}{INVERSE_TITLE_SUFFIX_DINAMIC_POSTFIX_EX6W}",
        description=INVERSE_DESCRIPTION_DINAMIC_POSTFIX_EX6W,
        input_data=inverse_input,
        expected_result=restored,
        pattern=INVERSE_PATTERN_DINAMIC_POSTFIX_EX6W,
        estimated_complexity=INVERSE_ESTIMATED_COMPLEXITY_DINAMIC_POSTFIX_EX6W,
    )
