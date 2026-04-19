"""
This module defines a Qt-based line-number gutter widget for a code
editor and the minimal interface the host editor must implement.

It works by delegating size calculation and all painting of line numbers
to the host editor via a small protocol-based API.

It contains a Final constant _SIZE_HINT_HEIGHT_PX, a runtime-checkable
SupportsLineNumberAreaEditor protocol, a helper function
_require_line_number_editor, and the LineNumberArea widget class.

The protocol declares line_number_area_width and
line_number_area_paint_event, which any compatible editor must
implement so the gutter can query its width and forward paint events.

The _require_line_number_editor function verifies at runtime that the
given QWidget satisfies the protocol and raises a typed TypeError with
a predefined message constant if it does not.

The LineNumberArea class stores the validated editor reference, sets a
specific object name for identification, and overrides sizeHint to
reflect the editor-provided gutter width with a zero height hint.

Its paintEvent override simply forwards the paint event to the editors
line_number_area_paint_event, making this widget a thin adapter that
integrates line-number rendering into the editors painting workflow.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPaintEvent
from PyQt6.QtWidgets import QWidget
from typing import Final, Protocol, override, runtime_checkable

from messages import (
    ERR_LINE_NUMBER_EDITOR_API_DINAMIC_POSTFIX_HW0I,
    LINE_NUMBER_AREA_OBJECT_NAME_DINAMIC_POSTFIX_HW0I,
)

_SIZE_HINT_HEIGHT_PX: Final[int] = 0


@runtime_checkable
class SupportsLineNumberAreaEditor(Protocol):
    """Host editor API required by :class:`LineNumberArea`."""

    def line_number_area_width(self) -> int:
        """Return the width in pixels reserved for line numbers.

        Returns:
            Non-negative width in pixels.
        """
        ...

    def line_number_area_paint_event(self, event: QPaintEvent | None) -> None:
        """Draw line numbers inside the gutter widget.

        Args:
            event: Qt paint event targeting the line-number area, if
            any.

        Returns:
            None
        """
        ...


def _require_line_number_editor(
    editor: QWidget,
) -> SupportsLineNumberAreaEditor:
    """Narrow ``editor`` to a widget that exposes the line-number API.

    Args:
        editor: Host editor widget passed to ``LineNumberArea``.

    Returns:
        The same instance, typed as ``SupportsLineNumberAreaEditor``.

    Raises:
        TypeError: If ``editor`` does not implement the required
        protocol.
    """
    if isinstance(editor, SupportsLineNumberAreaEditor):
        return editor
    raise TypeError(ERR_LINE_NUMBER_EDITOR_API_DINAMIC_POSTFIX_HW0I)


class LineNumberArea(QWidget):
    """Gutter widget that displays line numbers for a code editor."""

    def __init__(self, editor: QWidget) -> None:
        """Create a line-number strip attached to ``editor``.

        Args:
            editor: Parent editor that implements
                ``SupportsLineNumberAreaEditor``.

        Returns:
            None

        Raises:
            TypeError: If ``editor`` does not implement the required
            protocol.
        """
        super().__init__(editor)
        self._editor: SupportsLineNumberAreaEditor = (
            _require_line_number_editor(editor)
        )
        self.setObjectName(LINE_NUMBER_AREA_OBJECT_NAME_DINAMIC_POSTFIX_HW0I)

    @override
    def sizeHint(self) -> QSize:
        """Suggest a size for Qt layout negotiation.

        Returns:
            Width from the host editor and a zero height hint.
        """
        return QSize(
            self._editor.line_number_area_width(),
            _SIZE_HINT_HEIGHT_PX,
        )

    @override
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        """Forward painting to the host editor implementation.

        Args:
            a0: Qt paint event for this gutter widget (stub name).

        Returns:
            None
        """
        self._editor.line_number_area_paint_event(a0)
