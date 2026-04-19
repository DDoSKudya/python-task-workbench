"""Tests for checker formatting and code preparation helpers."""

from __future__ import annotations

from typing import Final

import pytest

from core import checker as ch

_ENTRY_SOLVE: Final[str] = "solve"
_LONG_STRING_LEN: Final[int] = 500
_SHORT_REPR_LIMIT: Final[int] = 40
_SHORT_REPR_MAX_LEN: Final[int] = 45


def test_format_mismatch_message_includes_types() -> None:
    """Mismatch text names expected and actual Python types.

    Returns:
        None.
    """
    msg = ch.format_mismatch_message(expected=1, actual="1")
    assert "int" in msg
    assert "str" in msg


def test_format_executor_traceback_empty() -> None:
    """Non-empty string is returned for an empty traceback buffer.

    Returns:
        None.
    """
    out = ch.format_executor_traceback("", entry=_ENTRY_SOLVE)
    assert isinstance(out, str)
    assert len(out) > 0


def test_prepare_code_strips_and_adds_newline() -> None:
    """Strip surrounding whitespace and ensure trailing newline.

    Returns:
        None.
    """
    assert (
        ch._prepare_code("  x = 1\n\t")  # pyright: ignore[reportPrivateUsage]
        == "x = 1\n"
    )


def test_prepare_code_empty_raises() -> None:
    """Reject whitespace-only source.

    Returns:
        None.
    """
    with pytest.raises(ValueError):
        ch._prepare_code("   \n\t  ")  # pyright: ignore[reportPrivateUsage]


def test_normalize_nested() -> None:
    """Normalize dict keys and tuple values for comparison.

    Returns:
        None.
    """
    assert ch._normalize(  # pyright: ignore[reportPrivateUsage]
        {"a": (1, 2), 3: "x"}
    ) == {
        "3": "x",
        "a": [1, 2],
    }


def test_strict_compare_requires_same_type() -> None:
    """Strict compare distinguishes ``int`` from ``float``.

    Returns:
        None.
    """
    assert ch._strict_compare(1, 1)  # pyright: ignore[reportPrivateUsage]
    assert not ch._strict_compare(  # pyright: ignore[reportPrivateUsage]
        1, 1.0
    )


def test_parse_exception_tail_value_error() -> None:
    """Parse exception name and message from a tail line.

    Returns:
        None.
    """
    name, msg = (
        ch._parse_exception_tail(  # pyright: ignore[reportPrivateUsage]
            "ValueError: bad"
        )
    )
    assert name == "ValueError"
    assert "bad" in msg


def test_hint_for_runtime_error_type_error() -> None:
    """Produce a hint for common ``TypeError`` subscript cases.

    Returns:
        None.
    """
    hint = ch._hint_for_runtime_error(  # pyright: ignore[reportPrivateUsage]
        "TypeError",
        "'list' object is not subscriptable",
    )
    assert hint is not None


def test_short_repr_truncates_long_values() -> None:
    """Long strings are truncated with an ellipsis marker.

    Returns:
        None.
    """
    long = "x" * _LONG_STRING_LEN
    text = ch._short_repr(  # pyright: ignore[reportPrivateUsage]
        long, limit=_SHORT_REPR_LIMIT
    )
    assert len(text) <= _SHORT_REPR_MAX_LEN
    assert "…" in text or len(text) < len(long)
