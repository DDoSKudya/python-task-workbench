"""Tests for :mod:`generator.cli.compare`."""

from __future__ import annotations

from typing import Final

import pytest

from generator.cli.compare import normalize, strict_compare

_ISSUE_COUNT_ONE: Final[int] = 1


def test_normalize_mapping_and_sequence() -> None:
    """Normalize maps tuples to lists under string keys.

    Returns:
        None.
    """
    assert normalize({"a": (1, 2)}) == {"a": [1, 2]}


def test_normalize_set_requires_scalar_items() -> None:
    """Sets with non-hashable items cannot be normalized.

    Returns:
        None.
    """
    with pytest.raises(TypeError):
        normalize({(1, 2)})


def test_strict_compare_equal_dicts() -> None:
    """Equal dicts yield no structural issues.

    Returns:
        None.
    """
    assert strict_compare({"a": 1}, {"a": 1}) == []


def test_strict_compare_type_mismatch() -> None:
    """List vs tuple reports a single issue string.

    Returns:
        None.
    """
    issues = strict_compare([1], (1,))
    assert len(issues) == _ISSUE_COUNT_ONE
    assert "list" in issues[0]
    assert "tuple" in issues[0]
