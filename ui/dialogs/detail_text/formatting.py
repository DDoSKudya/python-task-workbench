"""
This module normalizes and wraps code text for display in a read-only
UI, making it easier to read without horizontal scrolling while
preserving indentation.

It works by cleaning up tabs and trailing spaces, dedenting common
indentation, wrapping each logical line at a configured width, and
trimming extraneous leading and trailing newlines.

It defines constants for wrap width, indent spacing, and
message-provided characters and tokens (newline, space, tab, tab
replacement, empty line).

The helper _normalize_line_endings replaces tabs with a configured
sequence and strips trailing spaces from each line, while
_strip_newlines removes leading and trailing newline characters from a
text block.

The _wrap_line function computes the leading space indentation of a
line, uses textwrap.TextWrapper to wrap the non-indented content to
WRAP_MAX_WIDTH, and applies a deeper indent for wrapped continuations,
returning a list of wrapped lines.

The main normalize_code_for_view function composes these steps: it
normalizes line endings, dedents the text, splits into lines, wraps
each line with _wrap_line, joins the wrapped lines with the newline
character, and strips surrounding newlines, returning a final string
suitable for UI code views.
"""

from __future__ import annotations

import textwrap

from messages import (
    EMPTY_LINE_DINAMIC_POSTFIX_ZZ8F,
    NEWLINE_CHAR_DINAMIC_POSTFIX_ZZ8F,
    SPACE_CHAR_DINAMIC_POSTFIX_ZZ8F,
    TAB_CHAR_DINAMIC_POSTFIX_ZZ8F,
    TAB_REPLACEMENT_DINAMIC_POSTFIX_ZZ8F,
)

WRAP_MAX_WIDTH: int = 84
WRAP_INDENT_SPACES: int = 4


def _normalize_line_endings(text: str) -> str:
    """Normalize tabs and trailing spaces for each line.

    Args:
        text: Raw input text.

    Returns:
        Text with normalized indentation and trimmed line endings.
    """
    normalized: str = text.replace(
        TAB_CHAR_DINAMIC_POSTFIX_ZZ8F, TAB_REPLACEMENT_DINAMIC_POSTFIX_ZZ8F
    )
    return NEWLINE_CHAR_DINAMIC_POSTFIX_ZZ8F.join(
        line.rstrip() for line in normalized.splitlines()
    )


def _wrap_line(line: str) -> list[str]:
    """Wrap one code line preserving its indentation.

    Args:
        line: Source line to wrap.

    Returns:
        Wrapped lines with the same base indentation.
    """
    if not line.strip():
        return [EMPTY_LINE_DINAMIC_POSTFIX_ZZ8F]
    indent_len: int = len(line) - len(
        line.lstrip(SPACE_CHAR_DINAMIC_POSTFIX_ZZ8F)
    )
    indent: str = SPACE_CHAR_DINAMIC_POSTFIX_ZZ8F * indent_len
    wrapper: textwrap.TextWrapper = textwrap.TextWrapper(
        width=WRAP_MAX_WIDTH,
        break_long_words=False,
        break_on_hyphens=False,
        initial_indent=indent,
        subsequent_indent=indent
        + SPACE_CHAR_DINAMIC_POSTFIX_ZZ8F * WRAP_INDENT_SPACES,
    )
    return wrapper.fill(
        line.lstrip(SPACE_CHAR_DINAMIC_POSTFIX_ZZ8F)
    ).splitlines()


def _strip_newlines(text: str) -> str:
    """Trim leading and trailing newline characters from text.

    Args:
        text: Input text payload.

    Returns:
        Text without surrounding newline separators.
    """
    return text.strip(NEWLINE_CHAR_DINAMIC_POSTFIX_ZZ8F)


def normalize_code_for_view(text: str) -> str:
    """Normalize code text for read-only UI presentation.

    Args:
        text: Raw code text.

    Returns:
        Normalized and softly wrapped code text.
    """
    normalized: str = _normalize_line_endings(text)
    normalized = _strip_newlines(textwrap.dedent(normalized))
    wrapped: list[str] = []
    lines: list[str] = normalized.splitlines()
    for line in lines:
        wrapped.extend(_wrap_line(line))
    return _strip_newlines(NEWLINE_CHAR_DINAMIC_POSTFIX_ZZ8F.join(wrapped))
