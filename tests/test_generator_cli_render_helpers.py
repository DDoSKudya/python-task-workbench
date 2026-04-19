"""Extra tests for :mod:`generator.cli.render_terminal` helpers."""

from __future__ import annotations

from typing import Final

from generator.cli.render_terminal import (
    _joined,  # pyright: ignore[reportPrivateUsage]
)
from generator.cli.render_terminal import (
    _non_empty_description_lines,  # pyright: ignore[reportPrivateUsage]
)
from generator.cli.render_terminal import (
    _numbered_description_hints,  # pyright: ignore[reportPrivateUsage]
)
from generator.cli.render_terminal import (
    DETAIL_LINES_THRESHOLD,
)
from generator.models import GeneratedTask

_MIN_HINTS: Final[int] = 1


def test_joined_uses_separator() -> None:
    """Joined text contains each fragment.

    Returns:
        None.
    """
    text = _joined(["a", "b"])
    assert "a" in text
    assert "b" in text


def test_non_empty_description_lines() -> None:
    """Strip blank lines from multiline descriptions.

    Returns:
        None.
    """
    task = GeneratedTask.from_dict(
        {
            "task_id": "x",
            "title": "t",
            "description": "  line1  \n\n  line2  ",
            "input_data": {},
            "expected_result": 0,
        }
    )
    lines = _non_empty_description_lines(task)
    assert lines == ["line1", "line2"]


def test_numbered_description_hints_filters() -> None:
    """Hints list retains numbered lines when present.

    Returns:
        None.
    """
    lines = ["1) first", "plain", "2) second"]
    got = _numbered_description_hints(lines)
    assert len(got) >= _MIN_HINTS


def test_detail_threshold_constant() -> None:
    """Detail threshold is a positive integer.

    Returns:
        None.
    """
    assert DETAIL_LINES_THRESHOLD >= 1
