"""Tests for :mod:`generator.cli.formatting`."""

from __future__ import annotations

from typing import Final

from generator.cli.formatting import (
    preview_value,
    structure_signature,
    to_pretty,
)

_PREVIEW_LIMIT: Final[int] = 2


def test_to_pretty_sorts_dict_keys() -> None:
    """Pretty output lists ``a`` before ``z`` for sorted keys.

    Returns:
        None.
    """
    text = to_pretty({"z": 1, "a": 2})
    assert text.index("a") < text.index("z")


def test_preview_value_truncates_list() -> None:
    """List preview respects the element limit.

    Returns:
        None.
    """
    prev = preview_value([1, 2, 3, 4, 5], limit=_PREVIEW_LIMIT)
    assert prev == [1, 2]


def test_preview_value_record_dict_untruncated() -> None:
    """Small dict payloads are returned whole.

    Returns:
        None.
    """
    data = {"x": 1, "y": 2, "z": 3}
    assert preview_value(data, limit=_PREVIEW_LIMIT) == data


def test_structure_signature_primitives() -> None:
    """Primitives map to simple type labels.

    Returns:
        None.
    """
    assert structure_signature(3.5) == "float"
    assert "dict" in structure_signature({"a": 1})
