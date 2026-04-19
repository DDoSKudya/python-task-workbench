"""Tests for :mod:`ui.editor.completion_words`."""

from __future__ import annotations

from typing import Final

from ui.editor.completion_words import (
    _public_builtin_names,  # pyright: ignore[reportPrivateUsage]
)
from ui.editor.completion_words import (
    build_word_list,
)

_MIN_WORDS: Final[int] = 50
_SAMPLE_SRC: Final[str] = "def f(input_data: dict) -> None:\n    pass\n"


def test_public_builtin_names_skips_dunders() -> None:
    """Dunder names are removed from builtins suggestions.

    Returns:
        None.
    """
    names = _public_builtin_names(names=["__doc__", "len", "abs"])
    assert "len" in names
    assert "abs" in names
    assert "__doc__" not in names


def test_build_word_list_includes_keywords_and_infer() -> None:
    """Word list includes keywords and parameter names from source.

    Returns:
        None.
    """
    words = build_word_list(_SAMPLE_SRC)
    assert "def" in words
    assert "input_data" in words
    assert len(words) > _MIN_WORDS
