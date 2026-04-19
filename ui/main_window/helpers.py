"""
This module provides small UI helpers for labeling pack names,
configuring monospaced fonts, and detecting “empty” code-like text
blocks.

It works by mapping a specific internal pack identifier to a localized
label, constructing a QFont with a predefined list of monospace family
fallbacks and style hint, and checking whether a string is blank or
equals one of several placeholder representations of empty data
structures.

It defines constants for monospace font family fallbacks, a tuple of
empty-block marker strings, and a frozen set EMPTY_MONO_BLOCK_MARKERS,
plus three functions: pack_label, mono_font, and is_empty_mono_block.

Within the broader system, this module standardizes how packs are
labeled in the UI, ensures consistent monospace typography for
code-like widgets, and helps decide when a monospace text field should
be treated as effectively empty.
"""

from __future__ import annotations

from PyQt6.QtGui import QFont
from typing import Final

from messages import (
    CLASSIC_PLUS_LABEL_DINAMIC_POSTFIX_J9OV,
    CLASSIC_PLUS_PACK_NAME_DINAMIC_POSTFIX_J9OV,
)

_MONO_FONT_FAMILY_FALLBACKS: Final[tuple[str, ...]] = (
    "JetBrains Mono",
    "Fira Code",
    "Consolas",
)

_EMPTY_MONO_BLOCK_MARKER_STRINGS: Final[tuple[str, ...]] = (
    "{}",
    "[]",
    "()",
    "null",
    "None",
    "set()",
    "dict()",
    "list()",
)
EMPTY_MONO_BLOCK_MARKERS: Final[frozenset[str]] = frozenset(
    _EMPTY_MONO_BLOCK_MARKER_STRINGS,
)


def pack_label(pack: str) -> str:
    """Map an internal pack id to the label shown in the UI.

    Args:
        pack: Pack identifier (e.g. from task metadata).

    Returns:
        The localized ``classic_plus`` label when ``pack`` matches the
        catalog id; otherwise ``pack`` unchanged.
    """
    if pack == CLASSIC_PLUS_PACK_NAME_DINAMIC_POSTFIX_J9OV:
        return CLASSIC_PLUS_LABEL_DINAMIC_POSTFIX_J9OV
    return pack


def mono_font(point_size: int) -> QFont:
    """Build a monospaced ``QFont`` for code-style widgets.

    Args:
        point_size: Point size passed to ``QFont.setPointSize``.

    Returns:
        Font with monospace style hint and fallback family list.
    """
    font = QFont()
    font.setFamilies(list(_MONO_FONT_FAMILY_FALLBACKS))
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(point_size)
    return font


def is_empty_mono_block(text: str) -> bool:
    """Return whether ``text`` is blank or only empty-structure
    placeholders.

    Args:
        text: Raw text from a monospace field.

    Returns:
        ``True`` if stripped text is empty or matches
        ``EMPTY_MONO_BLOCK_MARKERS``.
    """
    normalized = text.strip()
    return (not normalized) or (normalized in EMPTY_MONO_BLOCK_MARKERS)
