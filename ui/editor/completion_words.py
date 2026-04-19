"""
This module builds the word-completion candidate list for the Python
code editor based on the current buffer and known symbols.

It works by merging Python keywords, public built-ins, inferred symbol
names, typing and stdlib hints, and all identifier-like tokens found in
the source, then returning a sorted list of unique strings.

It defines a compiled IDENTIFIER_RE pattern for matching identifiers,
using a configurable IDENTIFIER_PATTERN_DINAMIC_POSTFIX_VVO4 from the
messages catalog.

The helper _public_builtin_names filters out private built-in names
(those starting with a configured prefix) from an iterable of names,
such as dir(builtins).

_merged_completion_names calls infer_symbol_types to get inferred
symbols, extracts identifiers from the buffer, and unions these with
keywords, public built-ins, typing names (TYPING_NAMES), and
STDLIB_HINTS to create a comprehensive completion name set.

The public build_word_list function simply delegates to
_merged_completion_names and returns the result as a stable,
alphabetically sorted list, which is used by the editors autocompletion
logic.
"""

from __future__ import annotations

import keyword
import re
from collections.abc import Iterable

import builtins as py_builtins

from messages import (
    IDENTIFIER_PATTERN_DINAMIC_POSTFIX_VVO4,
    PRIVATE_NAME_PREFIX_DINAMIC_POSTFIX_VVO4,
)

from .constants import STDLIB_HINTS, TYPING_NAMES
from .type_inference import infer_symbol_types

IDENTIFIER_RE: re.Pattern[str] = re.compile(
    IDENTIFIER_PATTERN_DINAMIC_POSTFIX_VVO4
)


def _public_builtin_names(*, names: Iterable[str]) -> set[str]:
    """Collect built-in names that omit the private-name prefix.

    Args:
        names: Iterable of attribute names (e.g. from ``dir(builtins)``)

    Returns:
        Names that do not start with ``PRIVATE_NAME_PREFIX`` from
        ``messages``.
    """
    prefix = PRIVATE_NAME_PREFIX_DINAMIC_POSTFIX_VVO4
    return {name for name in names if not name.startswith(prefix)}


def _merged_completion_names(*, source: str) -> set[str]:
    """Merge keywords, hints, inferred symbols, and buffer tokens.

    Args:
        source: Python source text shown in the editor.

    Returns:
        Unique completion strings before sorting.
    """
    inferred = infer_symbol_types(source)
    from_buffer = set(IDENTIFIER_RE.findall(source))
    return (
        set(keyword.kwlist)
        | _public_builtin_names(names=dir(py_builtins))
        | set(inferred)
        | set(TYPING_NAMES)
        | set(STDLIB_HINTS)
        | from_buffer
    )


def build_word_list(source: str) -> list[str]:
    """Return a sorted list of unique completion candidates.

    Args:
        source: Current editor buffer contents.

    Returns:
        Stable sorted list built from merged name sets.
    """
    return sorted(_merged_completion_names(source=source))
