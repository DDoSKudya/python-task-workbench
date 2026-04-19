"""
This module implements Python syntax highlighting for a Qt text
document, with support for dark and light themes.

It works by compiling regular expression rules for Python keywords,
strings, comments, and numbers, then applying text formats to matching
ranges in each text block.

It defines a HighlightRule type alias, several compiled regex constants
for different token categories, and helper functions _create_format,
_color_for_theme, _keyword_string_comment_colors, _keyword_rules, and
_python_highlight_rules to construct the highlighting rules and
associated colors.

The _python_highlight_rules function builds a sequence of (pattern,
format) pairs, including one rule per Python keyword generated from a
template pattern and the standard keyword list.

The PythonHighlighter class subclasses QSyntaxHighlighter, initializes
its rule set based on the chosen theme in __init__, and overrides
highlightBlock to iterate over all rules and call setFormat for each
regex match in the given text.

Within the broader system, this class is responsible for visually
differentiating syntactic elements in a Python code editor, making the
code more readable while delegating actual colors and patterns to a
shared message catalog.
"""

from __future__ import annotations

import keyword
import re

from PyQt6.QtCore import QObject
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from typing import Final, override

from messages import (
    COMMENT_COLOR_DARK_DINAMIC_POSTFIX_NK00,
    COMMENT_COLOR_LIGHT_DINAMIC_POSTFIX_NK00,
    COMMENT_PATTERN_DINAMIC_POSTFIX_NK00,
    DOUBLE_QUOTED_STRING_PATTERN_DINAMIC_POSTFIX_NK00,
    KEYWORD_COLOR_DARK_DINAMIC_POSTFIX_NK00,
    KEYWORD_COLOR_LIGHT_DINAMIC_POSTFIX_NK00,
    KEYWORD_PATTERN_TEMPLATE_DINAMIC_POSTFIX_NK00,
    NUMBER_COLOR_DINAMIC_POSTFIX_NK00,
    NUMBER_PATTERN_DINAMIC_POSTFIX_NK00,
    SINGLE_QUOTED_STRING_PATTERN_DINAMIC_POSTFIX_NK00,
    STRING_COLOR_DARK_DINAMIC_POSTFIX_NK00,
    STRING_COLOR_LIGHT_DINAMIC_POSTFIX_NK00,
)

type HighlightRule = tuple[re.Pattern[str], QTextCharFormat]

_DOUBLE_QUOTED_STRING_RE: Final[re.Pattern[str]] = re.compile(
    DOUBLE_QUOTED_STRING_PATTERN_DINAMIC_POSTFIX_NK00
)
_SINGLE_QUOTED_STRING_RE: Final[re.Pattern[str]] = re.compile(
    SINGLE_QUOTED_STRING_PATTERN_DINAMIC_POSTFIX_NK00
)
_COMMENT_RE: Final[re.Pattern[str]] = re.compile(
    COMMENT_PATTERN_DINAMIC_POSTFIX_NK00
)
_NUMBER_RE: Final[re.Pattern[str]] = re.compile(
    NUMBER_PATTERN_DINAMIC_POSTFIX_NK00
)


def _create_format(*, color: str, bold: bool = False) -> QTextCharFormat:
    """Build a character format for one highlighting category.

    Args:
        color: Foreground color as a hex string (e.g. ``#RRGGBB``).
        bold: When ``True``, use bold font weight.

    Returns:
        A new ``QTextCharFormat`` with foreground (and optional bold)
        set.
    """
    text_format = QTextCharFormat()
    text_format.setForeground(QColor(color))
    if bold:
        text_format.setFontWeight(QFont.Weight.Bold)
    return text_format


def _color_for_theme(*, dark: bool, dark_color: str, light_color: str) -> str:
    """Pick a catalog color for the current light/dark theme.

    Args:
        dark: ``True`` when the editor uses the dark palette.
        dark_color: Hex color from the catalog for dark mode.
        light_color: Hex color from the catalog for light mode.

    Returns:
        The ``dark_color`` or ``light_color`` value, unchanged.
    """
    return dark_color if dark else light_color


def _keyword_string_comment_colors(*, dark: bool) -> tuple[str, str, str]:
    """Resolve keyword, string, and comment colors for ``dark`` mode.

    Args:
        dark: ``True`` when the editor uses the dark palette.

    Returns:
        ``(keyword_hex, string_hex, comment_hex)`` from the message
        catalog.
    """
    keyword_hex = _color_for_theme(
        dark=dark,
        dark_color=KEYWORD_COLOR_DARK_DINAMIC_POSTFIX_NK00,
        light_color=KEYWORD_COLOR_LIGHT_DINAMIC_POSTFIX_NK00,
    )
    string_hex = _color_for_theme(
        dark=dark,
        dark_color=STRING_COLOR_DARK_DINAMIC_POSTFIX_NK00,
        light_color=STRING_COLOR_LIGHT_DINAMIC_POSTFIX_NK00,
    )
    comment_hex = _color_for_theme(
        dark=dark,
        dark_color=COMMENT_COLOR_DARK_DINAMIC_POSTFIX_NK00,
        light_color=COMMENT_COLOR_LIGHT_DINAMIC_POSTFIX_NK00,
    )
    return keyword_hex, string_hex, comment_hex


def _keyword_rules(
    keyword_format: QTextCharFormat,
) -> tuple[HighlightRule, ...]:
    """Build one rule per Python keyword using the shared keyword
    format.

    Args:
        keyword_format: Format applied to every ``keyword.kwlist``
        entry.

    Returns:
        Tuple of ``(pattern, format)`` pairs in keyword list order.
    """
    template = KEYWORD_PATTERN_TEMPLATE_DINAMIC_POSTFIX_NK00
    return tuple(
        (
            re.compile(template.format(word=re.escape(word))),
            keyword_format,
        )
        for word in keyword.kwlist
    )


def _python_highlight_rules(*, dark: bool) -> tuple[HighlightRule, ...]:
    """Assemble all highlight rules for Python text blocks.

    Args:
        dark: ``True`` when the editor uses the dark palette.

    Returns:
        Rules in application order: keywords, strings, comments,
        numbers.
    """
    keyword_hex, string_hex, comment_hex = _keyword_string_comment_colors(
        dark=dark
    )
    keyword_format = _create_format(color=keyword_hex, bold=True)
    string_format = _create_format(color=string_hex)
    comment_format = _create_format(color=comment_hex)
    number_format = _create_format(color=NUMBER_COLOR_DINAMIC_POSTFIX_NK00)
    tail: tuple[HighlightRule, ...] = (
        (_DOUBLE_QUOTED_STRING_RE, string_format),
        (_SINGLE_QUOTED_STRING_RE, string_format),
        (_COMMENT_RE, comment_format),
        (_NUMBER_RE, number_format),
    )
    return _keyword_rules(keyword_format) + tail


class PythonHighlighter(QSyntaxHighlighter):
    """Apply Python-oriented styles to a ``QTextDocument``."""

    def __init__(self, parent: QObject | None, *, dark: bool = True) -> None:
        """Create a highlighter and compile rules for the given theme.

        Args:
            parent: Qt parent (typically the document's editor or
            document).
            dark: ``True`` to use dark-theme colors from the message
            catalog.

        Returns:
            None
        """
        super().__init__(parent)
        self._rules: tuple[HighlightRule, ...] = _python_highlight_rules(
            dark=dark
        )

    @override
    def highlightBlock(self, text: str | None) -> None:
        """Run every rule against ``text`` and call ``setFormat`` for
        hits.

        Args:
            text: UTF-8 text of the current block, or ``None`` if
            missing.

        Returns:
            None
        """
        if text is None:
            return
        for pattern, text_format in self._rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, text_format)
