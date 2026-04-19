"""
This module builds a check-mark (success) Qt icon from an SVG template
for use in the UI.

It works by formatting a catalog-provided SVG template with stroke
color, stroke width, and check shape markup, then passing the resulting
SVG string to a rendering helper that returns a square QIcon of a
specified size.

It defines the constant MARK_ICON_SIZE, an internal _icon_svg helper
that expands the SVG template, an internal _build_icon helper that
calls svg_icon, and a public icon_check factory function that supplies
default stroke and size values from the message catalog.

Within the broader system, this module provides a reusable, theme-aware
check icon for success or completion indicators, keeping SVG structure
and styling centralized and consistent.
"""

from __future__ import annotations

from PyQt6.QtGui import QIcon
from typing import Final

from messages import (
    CHECK_BODY_DINAMIC_POSTFIX_CX4Z,
    CHECK_ICON_STROKE_DINAMIC_POSTFIX_CX4Z,
    CHECK_STROKE_WIDTH_DINAMIC_POSTFIX_CX4Z,
    SVG_TEMPLATE_DINAMIC_POSTFIX_CX4Z,
)

from .render import svg_icon

MARK_ICON_SIZE: Final[int] = 16


def _icon_svg(*, stroke: str, stroke_width: str, body: str) -> str:
    """Format one SVG document from catalog template and shape markup.

    Args:
        stroke: Value for the template ``stroke`` placeholder (catalog
            color).
        stroke_width: Value for the ``stroke_width`` placeholder
        (catalog token, e.g. CSS width).
        body: Inner SVG elements from the message catalog.

    Returns:
        Complete SVG ``str`` ready for :func:`svg_icon`.
    """
    return SVG_TEMPLATE_DINAMIC_POSTFIX_CX4Z.format(
        stroke=stroke,
        stroke_width=stroke_width,
        body=body,
    )


def _build_icon(*, stroke: str, size: int) -> QIcon:
    """Render the check-mark shape into a square ``QIcon``.

    Args:
        stroke: Stroke color passed into :func:`_icon_svg`.
        size: Icon width and height in pixels.

    Returns:
        ``QIcon`` backed by a single normal/off pixmap.
    """
    return svg_icon(
        svg=_icon_svg(
            stroke=stroke,
            stroke_width=CHECK_STROKE_WIDTH_DINAMIC_POSTFIX_CX4Z,
            body=CHECK_BODY_DINAMIC_POSTFIX_CX4Z,
        ),
        size=size,
    )


def icon_check(
    *,
    stroke: str = CHECK_ICON_STROKE_DINAMIC_POSTFIX_CX4Z,
    size: int = MARK_ICON_SIZE,
) -> QIcon:
    """Build the check (success) mark icon.

    Args:
        stroke: SVG stroke color; defaults to the check-specific catalog
            stroke token.
        size: Square icon side length in pixels; defaults to
            ``MARK_ICON_SIZE``.

    Returns:
        A ``QIcon`` for success or completion indicators.
    """
    return _build_icon(stroke=stroke, size=size)
