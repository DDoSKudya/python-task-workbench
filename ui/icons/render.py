"""
This module converts SVG strings into Qt icons, providing a small
utility layer for rasterizing SVG artwork into square QIcon instances
used throughout the UI.

It works by stripping and encoding the SVG text, rendering it via
QSvgRenderer onto a transparent QPixmap with antialiasing, and then
wrapping that pixmap into a QIcon with a single Normal/Off state.

It defines constants DEFAULT_ICON_SIZE and SVG_CANVAS_ORIGIN, a private
_render_svg function that performs the rasterization into a QPixmap,
and a public svg_icon function that exposes a simple SVG-to-QIcon API
with a default size.

Within the broader system, this module underpins all SVG-based icon
factories, ensuring consistent rendering quality, sizing, and
transparency handling for the applications icon set.
"""

from __future__ import annotations

from PyQt6.QtCore import QByteArray, QRectF, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from typing import Final

from messages import (
    SVG_TRIM_CHARS_DINAMIC_POSTFIX_2TJK,
    UTF8_ENCODING_DINAMIC_POSTFIX_2TJK,
)

DEFAULT_ICON_SIZE: Final[int] = 20
SVG_CANVAS_ORIGIN: Final[float] = 0.0


def _render_svg(*, svg: str, size: int) -> QPixmap:
    """Rasterize SVG markup to a square pixmap with a transparent
    background.

    Args:
        svg: Full SVG document as a string.
        size: Edge length of the square pixmap in pixels.

    Returns:
        A ``QPixmap`` of ``size`` x ``size`` with anti-aliased SVG
        content.
    """
    data = QByteArray(
        svg.strip(SVG_TRIM_CHARS_DINAMIC_POSTFIX_2TJK).encode(
            UTF8_ENCODING_DINAMIC_POSTFIX_2TJK,
        )
    )
    renderer = QSvgRenderer(data)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    side = float(size)
    target = QRectF(
        SVG_CANVAS_ORIGIN,
        SVG_CANVAS_ORIGIN,
        side,
        side,
    )
    renderer.render(painter, target)
    painter.end()
    return pixmap


def svg_icon(svg: str, size: int = DEFAULT_ICON_SIZE) -> QIcon:
    """Build a ``QIcon`` whose only pixmap comes from ``svg``.

    Args:
        svg: Full SVG document as a string.
        size: Square icon side length in pixels; defaults to
            ``DEFAULT_ICON_SIZE``.

    Returns:
        ``QIcon`` with one ``Normal`` / ``Off`` pixmap produced by
        :func:`_render_svg`.
    """
    pixmap = _render_svg(svg=svg, size=size)
    icon = QIcon()
    icon.addPixmap(
        pixmap,
        mode=QIcon.Mode.Normal,
        state=QIcon.State.Off,
    )
    return icon
