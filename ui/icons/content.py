"""
This module creates small Qt icons for content-related actions,
specifically a file-with-text icon and a code-brackets icon, using SVG
templates.

It works by formatting a shared SVG template with catalog-supplied
stroke color and body markup, then passing the result to a rendering
helper that turns the SVG into a square QIcon of a given size.

It defines the constant CONTENT_ICON_SIZE, two internal helpers
_icon_svg and _build_icon, and two public factory functions
icon_file_text and icon_code that wrap these helpers with different SVG
bodies and default parameters.

Within the broader system, this module provides consistently sized
content icons for use in the UI, keeping their appearance driven by a
centralized message catalog and a shared SVG rendering pipeline.
"""

from __future__ import annotations

from PyQt6.QtGui import QIcon
from typing import Final

from messages import (
    CODE_BODY_DINAMIC_POSTFIX_NPDL,
    DEFAULT_ICON_STROKE_DINAMIC_POSTFIX_NPDL,
    FILE_TEXT_BODY_DINAMIC_POSTFIX_NPDL,
    SVG_TEMPLATE_DINAMIC_POSTFIX_NPDL,
)

from .render import svg_icon

CONTENT_ICON_SIZE: Final[int] = 16


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
    return SVG_TEMPLATE_DINAMIC_POSTFIX_NPDL.format(stroke=stroke, body=body)


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


def icon_file_text(
    *,
    stroke: str = DEFAULT_ICON_STROKE_DINAMIC_POSTFIX_NPDL,
    size: int = CONTENT_ICON_SIZE,
) -> QIcon:
    """Build the file-with-lines (document) icon.

    Args:
        stroke: SVG stroke color; defaults to the catalog stroke token.
        size: Square icon side length in pixels; defaults to
        ``CONTENT_ICON_SIZE`` (smaller than the default chrome icons).

    Returns:
        A ``QIcon`` for file or document-related actions.
    """
    return _build_icon(
        body=FILE_TEXT_BODY_DINAMIC_POSTFIX_NPDL,
        stroke=stroke,
        size=size,
    )


def icon_code(
    *,
    stroke: str = DEFAULT_ICON_STROKE_DINAMIC_POSTFIX_NPDL,
    size: int = CONTENT_ICON_SIZE,
) -> QIcon:
    """Build the code brackets icon.

    Args:
        stroke: SVG stroke color; defaults to the catalog stroke token.
        size: Square icon side length in pixels; defaults to
            ``CONTENT_ICON_SIZE``.

    Returns:
        A ``QIcon`` for code or editor-related actions.
    """
    return _build_icon(
        body=CODE_BODY_DINAMIC_POSTFIX_NPDL,
        stroke=stroke,
        size=size,
    )
