"""
This module provides utilities to pretty-print nested Python containers
and to summarize their structural shape as compact signatures.

It works by recursively walking mappings, sequences, and sets, producing
deterministic, multi-line string representations with configurable
brackets, commas, and indentation tokens taken from the messages module.

It defines constants for formatting primitives (indent unit, newline,
separators, empty-literal templates, and signature templates) that make
the output consistent and localization-friendly.

The pretty function is the main entry point, delegating to _render,
which dispatches on type to specialized helpers for mappings, sequences
(lists and tuples), and sets, ensuring one element per line and stable
ordering for sets.

The structure_signature function and its helpers (_mapping_signature,
_list_signature, _tuple_signature, _set_signature) compute concise,
type-level descriptions of containers based on a small sample of their
contents, such as the first element or first key/value pair.

Within the broader system, this module underpins user-facing
explanations and mismatch messages by turning complex values into
readable text and by exposing human-friendly descriptions of data
shapes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence, Set

from typing import Final

from messages import (
    COMMA_SEPARATOR_DINAMIC_POSTFIX_SLAM,
    DICT_LEFT_DINAMIC_POSTFIX_VH2R,
    DICT_RIGHT_DINAMIC_POSTFIX_VH2R,
    DICT_SIG_TMPL_DINAMIC_POSTFIX_VH2R,
    EMPTY_DICT_DINAMIC_POSTFIX_VH2R,
    EMPTY_DICT_SIG_DINAMIC_POSTFIX_VH2R,
    EMPTY_LIST_DINAMIC_POSTFIX_VH2R,
    EMPTY_LIST_SIG_DINAMIC_POSTFIX_VH2R,
    EMPTY_SET_DINAMIC_POSTFIX_VH2R,
    EMPTY_SET_SIG_DINAMIC_POSTFIX_VH2R,
    EMPTY_TUPLE_DINAMIC_POSTFIX_VH2R,
    EMPTY_TUPLE_SIG_DINAMIC_POSTFIX_VH2R,
    INDENT_UNIT_DINAMIC_POSTFIX_F0CN,
    LIST_LEFT_DINAMIC_POSTFIX_VH2R,
    LIST_RIGHT_DINAMIC_POSTFIX_VH2R,
    LIST_SIG_TMPL_DINAMIC_POSTFIX_VH2R,
    NEWLINE_DINAMIC_POSTFIX_VH2R,
    SET_SIG_TMPL_DINAMIC_POSTFIX_VH2R,
    TRAILING_COMMA_DINAMIC_POSTFIX_VH2R,
    TUPLE_LEFT_DINAMIC_POSTFIX_VH2R,
    TUPLE_RIGHT_DINAMIC_POSTFIX_VH2R,
    TUPLE_SIG_TMPL_DINAMIC_POSTFIX_VH2R,
)

_INDENT: Final[str] = INDENT_UNIT_DINAMIC_POSTFIX_F0CN
_NEWLINE: Final[str] = NEWLINE_DINAMIC_POSTFIX_VH2R
_SEPARATOR: Final[str] = COMMA_SEPARATOR_DINAMIC_POSTFIX_SLAM
_EMPTY_DICT: Final[str] = EMPTY_DICT_DINAMIC_POSTFIX_VH2R
_EMPTY_LIST: Final[str] = EMPTY_LIST_DINAMIC_POSTFIX_VH2R
_EMPTY_TUPLE: Final[str] = EMPTY_TUPLE_DINAMIC_POSTFIX_VH2R
_EMPTY_SET: Final[str] = EMPTY_SET_DINAMIC_POSTFIX_VH2R
_EMPTY_DICT_SIG: Final[str] = EMPTY_DICT_SIG_DINAMIC_POSTFIX_VH2R
_EMPTY_LIST_SIG: Final[str] = EMPTY_LIST_SIG_DINAMIC_POSTFIX_VH2R
_EMPTY_TUPLE_SIG: Final[str] = EMPTY_TUPLE_SIG_DINAMIC_POSTFIX_VH2R
_EMPTY_SET_SIG: Final[str] = EMPTY_SET_SIG_DINAMIC_POSTFIX_VH2R
_DICT_SIG_TMPL: Final[str] = DICT_SIG_TMPL_DINAMIC_POSTFIX_VH2R
_LIST_SIG_TMPL: Final[str] = LIST_SIG_TMPL_DINAMIC_POSTFIX_VH2R
_TUPLE_SIG_TMPL: Final[str] = TUPLE_SIG_TMPL_DINAMIC_POSTFIX_VH2R
_SET_SIG_TMPL: Final[str] = SET_SIG_TMPL_DINAMIC_POSTFIX_VH2R
_MAX_TUPLE_SIG_ITEMS: Final[int] = 3

_LIST_LEFT: Final[str] = LIST_LEFT_DINAMIC_POSTFIX_VH2R
_LIST_RIGHT: Final[str] = LIST_RIGHT_DINAMIC_POSTFIX_VH2R
_TUPLE_LEFT: Final[str] = TUPLE_LEFT_DINAMIC_POSTFIX_VH2R
_TUPLE_RIGHT: Final[str] = TUPLE_RIGHT_DINAMIC_POSTFIX_VH2R
_DICT_LEFT: Final[str] = DICT_LEFT_DINAMIC_POSTFIX_VH2R
_DICT_RIGHT: Final[str] = DICT_RIGHT_DINAMIC_POSTFIX_VH2R
_TRAILING_COMMA: Final[str] = TRAILING_COMMA_DINAMIC_POSTFIX_VH2R
_DEPTH_STEP: Final[int] = 1


def _indents_for_depth(depth: int) -> tuple[str, str]:
    """Compute indentation strings for the current nesting level.

    Args:
        depth: Zero-based nesting depth for the opening line.

    Returns:
        A pair ``(line_indent, child_indent)`` using ``_INDENT`` units.
    """
    unit = _INDENT
    return (unit * depth, unit * (depth + _DEPTH_STEP))


def pretty(value: object) -> str:
    """Render nested values into a deterministic multiline string.

    Args:
        value: Any Python object to display.

    Returns:
        Pretty-printed text for mappings, sequences, sets, and scalars.
    """
    return _render(value=value, depth=0)


def _render(value: object, depth: int) -> str:
    """Recursively render one value at the given indentation depth.

    Args:
        value: Object to render.
        depth: Current nesting depth for indentation.

    Returns:
        Multiline representation with stable formatting.
    """
    if isinstance(value, Mapping):
        return _render_mapping(value=value, depth=depth)
    if isinstance(value, list):
        return _render_sequence(
            value=value,
            depth=depth,
            left=_LIST_LEFT,
            right=_LIST_RIGHT,
            empty=_EMPTY_LIST,
        )
    if isinstance(value, tuple):
        return _render_sequence(
            value=value,
            depth=depth,
            left=_TUPLE_LEFT,
            right=_TUPLE_RIGHT,
            empty=_EMPTY_TUPLE,
        )
    return _render_set(value=value) if isinstance(value, Set) else repr(value)


def _render_mapping(value: Mapping[object, object], depth: int) -> str:
    """Render a mapping with one key-value pair per line.

    Args:
        value: Mapping to render.
        depth: Current nesting depth for indentation.

    Returns:
        Bracketed mapping string with aligned indentation.
    """
    if not value:
        return _EMPTY_DICT
    indent, next_indent = _indents_for_depth(depth)
    child_depth = depth + _DEPTH_STEP
    lines: list[str] = [_DICT_LEFT]
    for key, item in value.items():
        rendered = _render(item, child_depth)
        line = f"{next_indent}{key!r}: {rendered}{_TRAILING_COMMA}"
        lines.append(line)
    lines.append(f"{indent}{_DICT_RIGHT}")
    return _NEWLINE.join(lines)


def _render_sequence(
    *,
    value: Sequence[object],
    depth: int,
    left: str,
    right: str,
    empty: str,
) -> str:
    """Render list-like values with one element per line.

    Args:
        value: Sequence to render.
        depth: Current nesting depth.
        left: Opening bracket token.
        right: Closing bracket token.
        empty: Literal used when ``value`` is empty.

    Returns:
        Formatted multiline sequence string.
    """
    if not value:
        return empty
    indent, next_indent = _indents_for_depth(depth)
    child_depth = depth + _DEPTH_STEP
    lines: list[str] = [left]
    for item in value:
        rendered = _render(item, child_depth)
        lines.append(f"{next_indent}{rendered}{_TRAILING_COMMA}")
    lines.append(f"{indent}{right}")
    return _NEWLINE.join(lines)


def _render_set(value: Set[object]) -> str:
    """Render a set using sorted ``repr`` keys for stable output.

    Args:
        value: Set or frozenset-like value implementing ``Set``.

    Returns:
        Empty set literal, or bracketed comma-separated ``repr`` items.
    """
    if not value:
        return _EMPTY_SET
    normalized = sorted(repr(item) for item in value)
    body = _SEPARATOR.join(normalized)
    return f"{_LIST_LEFT}{body}{_LIST_RIGHT}"


def structure_signature(value: object) -> str:
    """Return a compact signature for nested container shapes.

    Args:
        value: Value to inspect.

    Returns:
        Signature describing the outermost container and element types.
    """
    if isinstance(value, Mapping):
        return _mapping_signature(value)
    if isinstance(value, list):
        return _list_signature(value)
    if isinstance(value, tuple):
        return _tuple_signature(value)
    if isinstance(value, Set):
        return _set_signature(value)
    return type(value).__name__


def _mapping_signature(value: Mapping[object, object]) -> str:
    """Build a mapping signature from the first key-value pair.

    Args:
        value: Non-empty or empty mapping.

    Returns:
        ``dict[empty]`` or a ``dict[key -> inner]`` style signature.
    """
    if not value:
        return _EMPTY_DICT_SIG
    key = next(iter(value))
    inner = structure_signature(value[key])
    return _DICT_SIG_TMPL.format(
        key_type=type(key).__name__,
        value_sig=inner,
    )


def _list_signature(value: list[object]) -> str:
    """Build a list signature from the first element.

    Args:
        value: List instance.

    Returns:
        ``list[empty]`` or ``list[inner]`` for the first item.
    """
    if not value:
        return _EMPTY_LIST_SIG
    inner = structure_signature(value[0])
    return _LIST_SIG_TMPL.format(item_sig=inner)


def _tuple_signature(value: tuple[object, ...]) -> str:
    """Build a tuple signature from up to three item types.

    Args:
        value: Tuple instance.

    Returns:
        ``tuple[empty]`` or ``tuple[type, ...]`` preview string.
    """
    if not value:
        return _EMPTY_TUPLE_SIG
    preview = value[:_MAX_TUPLE_SIG_ITEMS]
    items = _SEPARATOR.join(type(item).__name__ for item in preview)
    return _TUPLE_SIG_TMPL.format(items=items)


def _set_signature(value: Set[object]) -> str:
    """Build a set signature from one arbitrary element.

    Args:
        value: Non-empty or empty set-like value.

    Returns:
        ``set[empty]`` or ``set[item_type]``.
    """
    if not value:
        return _EMPTY_SET_SIG
    item = next(iter(value))
    return _SET_SIG_TMPL.format(item_type=type(item).__name__)
