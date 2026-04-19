"""
This module provides utilities for pretty-printing nested Python values
and summarizing their container structure for CLI output.

It works by rendering dicts, lists, tuples, and sets into deterministic
multi-line text with sorted keys and one element per line, and by
computing concise “signatures” that describe container shapes without
showing all contents.

It defines formatting-related constants and a _PrettyRenderer class that
encapsulates indentation, scalar rendering via repr, and type-specific
rendering for dicts, lists, tuples, and sets using message-driven
templates.

The to_pretty function is the main entry point for full rendering,
instantiating _PrettyRenderer with a configured indent unit and
delegating to its render method for arbitrary values.

The preview_value function builds a truncated copy of a nested value,
limiting each container to a given number of items while preserving
record-like dicts whose values are non-container scalars.

Helper functions _dict_signature, _list_signature, _tuple_signature, and
_set_signature generate descriptive signatures based on a small sample
of elements, and structure_signature dispatches among them or falls back
to the type name for scalars.

Within the broader system, this module underpins CLI diagnostics and
task exports by turning complex data structures into readable text and
by giving users quick insight into the shape of values without
overwhelming detail.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from typing import Final

from messages import (
    CLOSE_DICT_DINAMIC_POSTFIX_F0CN,
    CLOSE_LIST_DINAMIC_POSTFIX_F0CN,
    CLOSE_TUPLE_DINAMIC_POSTFIX_F0CN,
    COMMA_SUFFIX_DINAMIC_POSTFIX_F0CN,
    DICT_EMPTY_SIGNATURE_DINAMIC_POSTFIX_F0CN,
    DICT_KEY_VALUE_TEMPLATE_DINAMIC_POSTFIX_F0CN,
    DICT_SIGNATURE_TEMPLATE_DINAMIC_POSTFIX_F0CN,
    EMPTY_DICT_DINAMIC_POSTFIX_F0CN,
    EMPTY_LIST_DINAMIC_POSTFIX_F0CN,
    EMPTY_SET_DINAMIC_POSTFIX_F0CN,
    EMPTY_TUPLE_DINAMIC_POSTFIX_F0CN,
    INDENT_UNIT_DINAMIC_POSTFIX_F0CN,
    LINE_BREAK_DINAMIC_POSTFIX_F0CN,
    LIST_EMPTY_SIGNATURE_DINAMIC_POSTFIX_F0CN,
    LIST_SIGNATURE_TEMPLATE_DINAMIC_POSTFIX_F0CN,
    OPEN_DICT_DINAMIC_POSTFIX_F0CN,
    OPEN_LIST_DINAMIC_POSTFIX_F0CN,
    OPEN_TUPLE_DINAMIC_POSTFIX_F0CN,
    SEQUENCE_ITEM_TEMPLATE_DINAMIC_POSTFIX_F0CN,
    SET_EMPTY_SIGNATURE_DINAMIC_POSTFIX_F0CN,
    SET_SIGNATURE_TEMPLATE_DINAMIC_POSTFIX_F0CN,
    TUPLE_EMPTY_SIGNATURE_DINAMIC_POSTFIX_F0CN,
    TUPLE_SIGNATURE_TEMPLATE_DINAMIC_POSTFIX_F0CN,
)

DEFAULT_PREVIEW_LIMIT: Final[int] = 3
TUPLE_SIGNATURE_SAMPLE_SIZE: Final[int] = 3
CONTAINER_TYPES: Final[tuple[type[object], ...]] = (
    dict,
    list,
    tuple,
    set,
)
SIGNATURE_SEPARATOR_SUFFIX: Final[str] = " "


class _PrettyRenderer:
    """Render nested Python values into stable multi-line text."""

    def __init__(self, indent_unit: str) -> None:
        """Initialize a renderer for pretty terminal output.

        Args:
            indent_unit: Indentation unit used per nesting depth.
        """
        self._indent_unit = indent_unit

    def render(self, value: object) -> str:
        """Render an arbitrary Python value.

        Args:
            value: Any Python value.

        Returns:
            A human-readable string representation.
        """
        return self._render(value, depth=0)

    def _scalar_text(self, item: object) -> str:
        """Return scalar representation used for ordering and printing.

        Args:
            item: Value to render.

        Returns:
            Stable scalar representation.
        """
        return repr(item)

    def _render_sequence(
        self,
        items: Iterable[object],
        *,
        open_bracket: str,
        close_bracket: str,
        depth: int,
    ) -> str:
        """Render list-like sequence with one item per line.

        Args:
            items: Sequence items to render.
            open_bracket: Opening bracket token.
            close_bracket: Closing bracket token.
            depth: Current indentation depth.

        Returns:
            Multi-line rendered sequence.
        """
        indent = self._indent_unit * depth
        next_indent = self._indent_unit * (depth + 1)
        lines: list[str] = [open_bracket]
        for child in items:
            rendered_child = self._render(child, depth=depth + 1)
            lines.append(
                SEQUENCE_ITEM_TEMPLATE_DINAMIC_POSTFIX_F0CN.format(
                    indent=next_indent, value=rendered_child
                )
            )
        lines.append(f"{indent}{close_bracket}")
        return LINE_BREAK_DINAMIC_POSTFIX_F0CN.join(lines)

    def _render_dict(self, item: Mapping[object, object], depth: int) -> str:
        """Render mapping with sorted keys and indented values.

        Args:
            item: Mapping value to render.
            depth: Current indentation depth.

        Returns:
            Multi-line mapping representation.
        """
        if not item:
            return EMPTY_DICT_DINAMIC_POSTFIX_F0CN
        indent = self._indent_unit * depth
        next_indent = self._indent_unit * (depth + 1)
        lines: list[str] = [OPEN_DICT_DINAMIC_POSTFIX_F0CN]
        for key in sorted(item.keys(), key=self._scalar_text):
            rendered_value = self._render(item[key], depth=depth + 1)
            rendered_key = self._scalar_text(key)
            lines.append(
                DICT_KEY_VALUE_TEMPLATE_DINAMIC_POSTFIX_F0CN.format(
                    indent=next_indent, key=rendered_key, value=rendered_value
                )
            )
        lines.append(f"{indent}{CLOSE_DICT_DINAMIC_POSTFIX_F0CN}")
        return LINE_BREAK_DINAMIC_POSTFIX_F0CN.join(lines)

    def _render_set(self, item: set[object], depth: int) -> str:
        """Render set values with deterministic ordering.

        Args:
            item: Set to render.
            depth: Current indentation depth.

        Returns:
            Rendered set representation.
        """
        if not item:
            return EMPTY_SET_DINAMIC_POSTFIX_F0CN
        sorted_items = sorted(item, key=self._scalar_text)
        return self._render_sequence(
            sorted_items,
            open_bracket=OPEN_DICT_DINAMIC_POSTFIX_F0CN,
            close_bracket=CLOSE_DICT_DINAMIC_POSTFIX_F0CN,
            depth=depth,
        )

    def _render_list(self, item: list[object], depth: int) -> str:
        """Render list values using stable multi-line formatting.

        Args:
            item: List to render.
            depth: Current indentation depth.

        Returns:
            Rendered list representation.
        """
        if not item:
            return EMPTY_LIST_DINAMIC_POSTFIX_F0CN
        return self._render_sequence(
            item,
            open_bracket=OPEN_LIST_DINAMIC_POSTFIX_F0CN,
            close_bracket=CLOSE_LIST_DINAMIC_POSTFIX_F0CN,
            depth=depth,
        )

    def _render_tuple(self, item: tuple[object, ...], depth: int) -> str:
        """Render tuple values using stable multi-line formatting.

        Args:
            item: Tuple to render.
            depth: Current indentation depth.

        Returns:
            Rendered tuple representation.
        """
        if not item:
            return EMPTY_TUPLE_DINAMIC_POSTFIX_F0CN
        return self._render_sequence(
            item,
            open_bracket=OPEN_TUPLE_DINAMIC_POSTFIX_F0CN,
            close_bracket=CLOSE_TUPLE_DINAMIC_POSTFIX_F0CN,
            depth=depth,
        )

    def _render(self, item: object, depth: int) -> str:
        """Render any supported value recursively.

        Args:
            item: Value to render.
            depth: Current indentation depth.

        Returns:
            Rendered representation for the value.
        """
        if isinstance(item, dict):
            return self._render_dict(item, depth)
        if isinstance(item, list):
            return self._render_list(item, depth)
        if isinstance(item, tuple):
            return self._render_tuple(item, depth)
        if isinstance(item, set):
            return self._render_set(item, depth)
        return self._scalar_text(item)


def to_pretty(value: object) -> str:
    """Render a Python value as a stable multi-line representation.

    The output is intended for terminal display and favors readability:

    - dictionaries are rendered with keys sorted by their ``repr``;
    - lists, tuples, and sets are rendered with one element per line;
    - scalars are rendered via ``repr``.

    Args:
        value: Any Python value.

    Returns:
        A human-readable string representation.
    """
    return _PrettyRenderer(
        indent_unit=INDENT_UNIT_DINAMIC_POSTFIX_F0CN
    ).render(value)


def preview_value(value: object, limit: int = DEFAULT_PREVIEW_LIMIT) -> object:
    """Build a shallow preview of a nested value.

    The function truncates container types to at most ``limit``
    elements, while keeping dictionaries with scalar-like values intact
    to preserve the "record" feel in CLI output.

    Args:
        value: Any Python value.
        limit: Maximum number of elements to keep for container
        previews.

    Returns:
        A value structurally similar to the input, but truncated.
    """
    if isinstance(value, dict):
        is_record_like = all(
            not isinstance(item, CONTAINER_TYPES) for item in value.values()
        )
        items = (
            value.items() if is_record_like else list(value.items())[:limit]
        )
        return {k: preview_value(v, limit=limit) for k, v in items}
    if isinstance(value, list):
        return [preview_value(item, limit=limit) for item in value[:limit]]
    if isinstance(value, tuple):
        return tuple(
            preview_value(item, limit=limit) for item in value[:limit]
        )
    if isinstance(value, set):
        preview_items = sorted(value, key=repr)[:limit]
        return {preview_value(item, limit=limit) for item in preview_items}
    return value


def _dict_signature(value: dict[object, object]) -> str:
    """Build signature text for dictionary values.

    Args:
        value: Dictionary value.

    Returns:
        Signature string describing dictionary structure.
    """
    if not value:
        return DICT_EMPTY_SIGNATURE_DINAMIC_POSTFIX_F0CN
    first_key = next(iter(value))
    key_type = type(first_key).__name__
    inner = structure_signature(value[first_key])
    return DICT_SIGNATURE_TEMPLATE_DINAMIC_POSTFIX_F0CN.format(
        key_type=key_type,
        inner=inner,
    )


def _list_signature(value: list[object]) -> str:
    """Build signature text for list values.

    Args:
        value: List value.

    Returns:
        Signature string describing list structure.
    """
    if not value:
        return LIST_EMPTY_SIGNATURE_DINAMIC_POSTFIX_F0CN
    return LIST_SIGNATURE_TEMPLATE_DINAMIC_POSTFIX_F0CN.format(
        inner=structure_signature(value[0]),
    )


def _tuple_signature(value: tuple[object, ...]) -> str:
    """Build signature text for tuple values.

    Args:
        value: Tuple value.

    Returns:
        Signature string describing tuple structure.
    """
    if not value:
        return TUPLE_EMPTY_SIGNATURE_DINAMIC_POSTFIX_F0CN
    samples = value[:TUPLE_SIGNATURE_SAMPLE_SIZE]
    separator = (
        f"{COMMA_SUFFIX_DINAMIC_POSTFIX_F0CN}{SIGNATURE_SEPARATOR_SUFFIX}"
    )
    inner = separator.join(structure_signature(item) for item in samples)
    return TUPLE_SIGNATURE_TEMPLATE_DINAMIC_POSTFIX_F0CN.format(inner=inner)


def _set_signature(value: set[object]) -> str:
    """Build signature text for set values.

    Args:
        value: Set value.

    Returns:
        Signature string describing set structure.
    """
    if not value:
        return SET_EMPTY_SIGNATURE_DINAMIC_POSTFIX_F0CN
    sample = next(iter(value))
    inner = structure_signature(sample)
    return SET_SIGNATURE_TEMPLATE_DINAMIC_POSTFIX_F0CN.format(inner=inner)


def structure_signature(value: object) -> str:
    """Return a concise string describing the structure of a value.

    This is used in CLI output to quickly identify container nesting
    without printing the full content.

    Args:
        value: Any Python value.

    Returns:
        A short structure signature string.
    """
    if isinstance(value, dict):
        return _dict_signature(value)
    if isinstance(value, list):
        return _list_signature(value)
    if isinstance(value, tuple):
        return _tuple_signature(value)
    if isinstance(value, set):
        return _set_signature(value)
    return type(value).__name__
