"""
This module builds filled Qt icons for playback-style controls,
specifically a play triangle and a stop square, using SVG templates.

It works by formatting a shared SVG template with a fill color and body
markup from a message catalog, then feeding the resulting SVG into a
rendering helper that returns a square QIcon of the requested size.

It defines the constant SQUARE_ICON_SIZE, two internal helpers
_filled_icon_svg and _build_filled_icon, and two public factory
functions icon_play_filled and icon_square_filled that provide default
colors and sizes for their respective shapes.

Within the broader system, this module centralizes creation of
consistent play/stop icons so that playback-related UI elements share
the same style, colors, and sizing conventions.
"""

from __future__ import annotations

from PyQt6.QtGui import QIcon
from typing import Final

from messages import (
    DEFAULT_FILL_COLOR_DINAMIC_POSTFIX_6KJF,
    PLAY_BODY_DINAMIC_POSTFIX_6KJF,
    SQUARE_BODY_DINAMIC_POSTFIX_6KJF,
    SVG_TEMPLATE_DINAMIC_POSTFIX_6KJF,
)

from .render import DEFAULT_ICON_SIZE, svg_icon

SQUARE_ICON_SIZE: Final[int] = 18


def _filled_icon_svg(*, color: str, body: str) -> str:
    """Format one filled SVG document from catalog template and body.

    Args:
        color: Value for the template ``color`` placeholder (catalog hex
        or CSS color).
        body: Inner SVG elements (paths, groups) from the message
        catalog.

    Returns:
        Complete SVG ``str`` ready for :func:`svg_icon`.
    """
    return SVG_TEMPLATE_DINAMIC_POSTFIX_6KJF.format(color=color, body=body)


def _build_filled_icon(*, body: str, color: str, size: int) -> QIcon:
    """Render catalog SVG body into a square filled ``QIcon``.

    Args:
        body: Inner SVG markup from the message catalog.
        color: Fill color passed into :func:`_filled_icon_svg`.
        size: Icon width and height in pixels.

    Returns:
        ``QIcon`` backed by a single normal/off pixmap.
    """
    return svg_icon(
        svg=_filled_icon_svg(color=color, body=body),
        size=size,
    )


def icon_play_filled(
    *,
    color: str = DEFAULT_FILL_COLOR_DINAMIC_POSTFIX_6KJF,
    size: int = DEFAULT_ICON_SIZE,
) -> QIcon:
    """Build the filled play (triangle) icon.

    Args:
        color: SVG fill color; defaults to the catalog fill token.
        size: Square icon side length in pixels; uses
        ``DEFAULT_ICON_SIZE`` from :mod:`ui.icons.render` when omitted.

    Returns:
        A ``QIcon`` for play or run actions.
    """
    return _build_filled_icon(
        body=PLAY_BODY_DINAMIC_POSTFIX_6KJF,
        color=color,
        size=size,
    )


def icon_square_filled(
    *,
    color: str = DEFAULT_FILL_COLOR_DINAMIC_POSTFIX_6KJF,
    size: int = SQUARE_ICON_SIZE,
) -> QIcon:
    """Build the filled square (stop) icon.

    Args:
        color: SVG fill color; defaults to the catalog fill token.
        size: Square icon side length in pixels; defaults to
        ``SQUARE_ICON_SIZE`` (slightly smaller than the play default).

    Returns:
        A ``QIcon`` for stop or square-indicator actions.
    """
    return _build_filled_icon(
        body=SQUARE_BODY_DINAMIC_POSTFIX_6KJF,
        color=color,
        size=size,
    )
