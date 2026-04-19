"""
This module builds themed Qt icons from SVG templates for specific UI
symbols like settings, clipboard list, and clock.

It works by filling a shared SVG template with catalog-provided body
markup and stroke colors, then passing the result to a rendering helper
that returns a QIcon of a given size.

It defines a constant CLOCK_ICON_SIZE, two internal helpers _icon_svg
and _build_icon, and three public factory functions icon_settings,
icon_clipboard_list, and icon_clock that wrap the helpers with different
SVG bodies and default stroke/size values.

Within the broader system, this module centralizes creation of key
toolbar or action icons so that their appearance, colors, and sizes
stay consistent and can be driven from the shared message catalog.
"""

from __future__ import annotations

from PyQt6.QtGui import QIcon
from typing import Final

from messages import (
    CLIPBOARD_LIST_BODY_DINAMIC_POSTFIX_CT67,
    CLOCK_BODY_DINAMIC_POSTFIX_CT67,
    CLOCK_ICON_STROKE_DINAMIC_POSTFIX_CT67,
    DEFAULT_ICON_STROKE_DINAMIC_POSTFIX_CT67,
    SETTINGS_BODY_DINAMIC_POSTFIX_CT67,
    SVG_TEMPLATE_DINAMIC_POSTFIX_CT67,
)

from .render import DEFAULT_ICON_SIZE, svg_icon

CLOCK_ICON_SIZE: Final[int] = 24


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
    return SVG_TEMPLATE_DINAMIC_POSTFIX_CT67.format(stroke=stroke, body=body)


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


def icon_settings(
    *,
    stroke: str = DEFAULT_ICON_STROKE_DINAMIC_POSTFIX_CT67,
    size: int = DEFAULT_ICON_SIZE,
) -> QIcon:
    """Build the settings (gear) icon.

    Args:
        stroke: SVG stroke color; defaults to the catalog stroke token.
        size: Square icon side length in pixels; uses
        ``DEFAULT_ICON_SIZE`` from :mod:`ui.icons.render` when omitted.

    Returns:
        A ``QIcon`` for settings/actions.
    """
    return _build_icon(
        body=SETTINGS_BODY_DINAMIC_POSTFIX_CT67,
        stroke=stroke,
        size=size,
    )


def icon_clipboard_list(
    *,
    stroke: str = DEFAULT_ICON_STROKE_DINAMIC_POSTFIX_CT67,
    size: int = DEFAULT_ICON_SIZE,
) -> QIcon:
    """Build the clipboard-with-list icon.

    Args:
        stroke: SVG stroke color; defaults to the catalog stroke token.
        size: Square icon side length in pixels; uses
        ``DEFAULT_ICON_SIZE`` from :mod:`ui.icons.render` when omitted.

    Returns:
        A ``QIcon`` for clipboard or list-related actions.
    """
    return _build_icon(
        body=CLIPBOARD_LIST_BODY_DINAMIC_POSTFIX_CT67,
        stroke=stroke,
        size=size,
    )


def icon_clock(
    *,
    stroke: str = CLOCK_ICON_STROKE_DINAMIC_POSTFIX_CT67,
    size: int = CLOCK_ICON_SIZE,
) -> QIcon:
    """Build the clock icon (distinct default stroke and size).

    Args:
        stroke: SVG stroke color; defaults to the clock-specific catalog
            stroke token.
        size: Square icon side length in pixels; defaults to
            ``CLOCK_ICON_SIZE``.

    Returns:
        A ``QIcon`` for time or history-related actions.
    """
    return _build_icon(
        body=CLOCK_BODY_DINAMIC_POSTFIX_CT67,
        stroke=stroke,
        size=size,
    )
