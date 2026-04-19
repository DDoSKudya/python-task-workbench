"""
This module creates a small Qt trash (delete) icon from an SVG template
for use in the user interface.

It works by formatting a catalog-provided SVG template with a stroke
color and trash-body markup, then passing the resulting SVG string to a
rendering helper that returns a square QIcon of a specified size.

It defines the constant TRASH_ICON_SIZE, two internal helpers _icon_svg
and _build_icon, and one public factory function icon_trash that wraps
these helpers with default stroke and size values from the message
catalog.

Within the broader system, this module provides a consistent,
theme-aware delete icon that can be reused across toolbars and actions
without duplicating SVG or styling logic.
"""

from __future__ import annotations

from PyQt6.QtGui import QIcon
from typing import Final

from messages import (
    SVG_TEMPLATE_DINAMIC_POSTFIX_E48A,
    TRASH_BODY_DINAMIC_POSTFIX_E48A,
    TRASH_ICON_STROKE_DINAMIC_POSTFIX_E48A,
)

from .render import svg_icon

TRASH_ICON_SIZE: Final[int] = 14


def _icon_svg(*, stroke: str, body: str) -> str:
    """Format one SVG document from catalog template and body markup.

    Args:
        stroke: Value for the template ``stroke`` placeholder (catalog
            color).
        body: Inner SVG elements (paths, groups) from the message
            catalog.

    Returns:
        Complete SVG ``str`` ready for :func:`svg_icon`.
    """
    return SVG_TEMPLATE_DINAMIC_POSTFIX_E48A.format(stroke=stroke, body=body)


def _build_icon(*, body: str, stroke: str, size: int) -> QIcon:
    """Render catalog SVG body into a square ``QIcon``.

    Args:
        body: Inner SVG markup from the message catalog.
        stroke: Stroke color passed into :func:`_icon_svg`.
        size: Icon width and height in pixels.

    Returns:
        ``QIcon`` backed by a single normal/off pixmap.
    """
    return svg_icon(
        svg=_icon_svg(stroke=stroke, body=body),
        size=size,
    )


def icon_trash(
    *,
    stroke: str = TRASH_ICON_STROKE_DINAMIC_POSTFIX_E48A,
    size: int = TRASH_ICON_SIZE,
) -> QIcon:
    """Build the trash (delete) icon.

    Args:
        stroke: SVG stroke color; defaults to the trash-specific catalog
            stroke token (often a destructive accent).
        size: Square icon side length in pixels; defaults to
            ``TRASH_ICON_SIZE`` (compact for toolbars).

    Returns:
        A ``QIcon`` for delete or remove actions.
    """
    return _build_icon(
        body=TRASH_BODY_DINAMIC_POSTFIX_E48A,
        stroke=stroke,
        size=size,
    )
