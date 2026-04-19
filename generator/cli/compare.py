"""
This module provides utilities to normalize arbitrary Python values into
a stable shape and to perform strict, path-aware deep comparisons
between two values.

It works by turning nested mappings, sequences, sets, and scalars into a
constrained “normalized” form and by recursively traversing two
structures to collect human-readable mismatch messages.

It defines type aliases for scalars and normalized values, plus a helper
_is_scalar used to guard the scalar set accepted in both normalization
and comparison logic.

The normalize function standardizes structures by stringifying dict
keys, converting tuples to lists, enforcing that sets only contain
scalar items, and converting non-scalar leaf values to strings.

The strict_compare function is the main comparison entry point, first
checking type equality and then delegating to specialized helpers for
mappings, sequences, sets, or scalars while tracking a logical “path”
into the structure.

Helper functions _compare_mapping, _compare_sequence, _compare_set, and
_compare_scalar each generate mismatch descriptions using templated
messages that mention missing/extra keys, length differences, set
inequality, or value differences at specific paths.

Within the broader system, this module is likely used for detailed
expected-vs-actual comparisons in tests or grading, providing precise,
user-facing diagnostics about where complex data structures disagree.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from typing import TypeGuard

from messages import (
    CHILD_PATH_TEMPLATE_DINAMIC_POSTFIX_PY68,
    DEFAULT_ROOT_PATH_DINAMIC_POSTFIX_PY68,
    ERR_ONLY_SCALAR_SET_ITEMS_DINAMIC_POSTFIX_PY68,
    EXTRA_KEYS_TEMPLATE_DINAMIC_POSTFIX_PY68,
    LENGTH_MISMATCH_TEMPLATE_DINAMIC_POSTFIX_PY68,
    MISSING_KEYS_TEMPLATE_DINAMIC_POSTFIX_PY68,
    SET_MISMATCH_TEMPLATE_DINAMIC_POSTFIX_PY68,
    TYPE_MISMATCH_TEMPLATE_DINAMIC_POSTFIX_PY68,
    VALUE_MISMATCH_TEMPLATE_DINAMIC_POSTFIX_PY68,
)

type Scalar = str | int | float | bool | None
type Normalized = (
    Scalar | list["Normalized"] | dict[str, "Normalized"] | set[Scalar]
)


def _is_scalar(value: object) -> TypeGuard[Scalar]:
    """Return whether a value belongs to the scalar comparison set.

    Args:
        value: Candidate value.

    Returns:
        ``True`` when value is a supported scalar.
    """
    return isinstance(value, (str, int, float, bool, type(None)))


def normalize(value: object) -> Normalized:
    """Normalize an arbitrary value into a stable, comparable structure.

    The goal is to ensure that:
    - dict keys become strings
    - tuples become lists
    - nested containers are normalized recursively

    Args:
        value: Any input value to normalize.

    Returns:
        A normalized value that is safe to compare recursively.
    """
    if isinstance(value, Mapping):
        return {str(k): normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(item) for item in value]
    if isinstance(value, set):
        normalized_items: set[Scalar] = set()
        for item in value:
            normalized = normalize(item)
            if not _is_scalar(normalized):
                raise TypeError(ERR_ONLY_SCALAR_SET_ITEMS_DINAMIC_POSTFIX_PY68)
            normalized_items.add(normalized)
        return normalized_items
    return value if _is_scalar(value) else str(value)


def strict_compare(
    expected: object,
    actual: object,
    path: str = DEFAULT_ROOT_PATH_DINAMIC_POSTFIX_PY68,
) -> list[str]:
    """Compare two values recursively and report differences.

    Args:
        expected: Expected value.
        actual: Actual value.
        path: Path prefix for human-readable issue messages.

    Returns:
        List of mismatch descriptions. Empty list means values match.
    """
    if type(expected) is not type(actual):
        return [
            TYPE_MISMATCH_TEMPLATE_DINAMIC_POSTFIX_PY68.format(
                path=path,
                expected_type=type(expected).__name__,
                actual_type=type(actual).__name__,
            )
        ]
    if isinstance(expected, Mapping) and isinstance(actual, Mapping):
        return _compare_mapping(expected, actual, path)
    if _is_scalar(expected) and _is_scalar(actual):
        return _compare_scalar(expected, actual, path)
    if isinstance(expected, Sequence) and isinstance(actual, Sequence):
        return _compare_sequence(expected, actual, path)
    if isinstance(expected, set) and isinstance(actual, set):
        return _compare_set(expected, actual, path)
    return _compare_scalar(expected, actual, path)


def _compare_mapping(
    expected: Mapping[object, object],
    actual: Mapping[object, object],
    path: str,
) -> list[str]:
    """Compare two mapping values recursively.

    Args:
        expected: Expected mapping.
        actual: Actual mapping.
        path: Path prefix.

    Returns:
        List of mismatches.
    """
    issues: list[str] = []
    expected_keys = set(expected.keys())
    actual_keys = set(actual.keys())
    missing = expected_keys - actual_keys
    extra = actual_keys - expected_keys
    if missing:
        missing_display = sorted(repr(k) for k in missing)
        issues.append(
            MISSING_KEYS_TEMPLATE_DINAMIC_POSTFIX_PY68.format(
                path=path, keys=missing_display
            )
        )
    if extra:
        extra_display = sorted(repr(k) for k in extra)
        issues.append(
            EXTRA_KEYS_TEMPLATE_DINAMIC_POSTFIX_PY68.format(
                path=path, keys=extra_display
            )
        )
    for key in expected_keys & actual_keys:
        issues.extend(
            strict_compare(
                expected[key],
                actual[key],
                CHILD_PATH_TEMPLATE_DINAMIC_POSTFIX_PY68.format(
                    path=path, key=key
                ),
            )
        )
    return issues


def _compare_sequence(
    expected: Sequence[object], actual: Sequence[object], path: str
) -> list[str]:
    """Compare two sequences recursively.

    Args:
        expected: Expected sequence.
        actual: Actual sequence.
        path: Path prefix.

    Returns:
        List of mismatches.
    """
    issues: list[str] = []
    if len(expected) != len(actual):
        issues.append(
            LENGTH_MISMATCH_TEMPLATE_DINAMIC_POSTFIX_PY68.format(
                path=path, expected_len=len(expected), actual_len=len(actual)
            )
        )
    for idx, (exp_item, act_item) in enumerate(zip(expected, actual)):
        issues.extend(
            strict_compare(
                exp_item,
                act_item,
                CHILD_PATH_TEMPLATE_DINAMIC_POSTFIX_PY68.format(
                    path=path, key=idx
                ),
            )
        )
    return issues


def _compare_set(
    expected: set[object], actual: set[object], path: str
) -> list[str]:
    """Compare two sets.

    Args:
        expected: Expected set.
        actual: Actual set.
        path: Path prefix.

    Returns:
        List of mismatches.
    """
    return (
        []
        if expected == actual
        else [SET_MISMATCH_TEMPLATE_DINAMIC_POSTFIX_PY68.format(path=path)]
    )


def _compare_scalar(expected: object, actual: object, path: str) -> list[str]:
    """Compare two scalar values.

    Args:
        expected: Expected scalar value.
        actual: Actual scalar value.
        path: Path prefix.

    Returns:
        List of mismatches.
    """
    return (
        []
        if expected == actual
        else [
            VALUE_MISMATCH_TEMPLATE_DINAMIC_POSTFIX_PY68.format(
                path=path, expected=expected, actual=actual
            )
        ]
    )
