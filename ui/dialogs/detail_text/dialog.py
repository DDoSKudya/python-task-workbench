"""
This module implements a reusable Qt dialog for showing detailed text or
code snippets in a read-only view.

It works by composing a QDialog with a header, a central QPlainTextEdit,
and a footer containing a close button, and by optionally configuring
the text area for code display with syntax highlighting.

It defines a series of layout and styling constants (sizes, margins,
font settings, tab stops, object names) that control the dialogs
appearance and behavior.

The DetailTextDialog class builds the widget tree in its constructor:
creating the root QVBoxLayout, adding a header frame with a title
label, a divider frame, a body layout containing the text view, and a
footer with a styled “Close” button wired to accept().

The _build_text_view method prepares the read-only QPlainTextEdit,
applies a fallback when the body text is empty, normalizes code when
is_code is true, sets line-wrapping mode, minimum height, and object
name, and calls _configure_code_view when showing code.

_configure_code_view sets a monospace font with a configurable point
size, adjusts tab-stop distance to emulate spaces, and attaches a
PythonHighlighter instance for syntax highlighting, integrating with the
shared ui.editor highlighting logic.

Helper methods _build_header, _build_divider, and _build_footer
encapsulate construction and styling of the dialogs sections, enabling
consistent look-and-feel and easier maintenance of the UI.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from messages import (
    CLOSE_BUTTON_TEXT_DINAMIC_POSTFIX_VXE0,
    EMPTY_BODY_FALLBACK_DINAMIC_POSTFIX_VXE0,
    OBJECT_NAME_BODY_CODE_DINAMIC_POSTFIX_VXE0,
    OBJECT_NAME_BODY_DINAMIC_POSTFIX_VXE0,
    OBJECT_NAME_DIALOG_DINAMIC_POSTFIX_VXE0,
    OBJECT_NAME_DIVIDER_DINAMIC_POSTFIX_VXE0,
    OBJECT_NAME_FOOTER_DINAMIC_POSTFIX_VXE0,
    OBJECT_NAME_HEADER_DINAMIC_POSTFIX_VXE0,
    OBJECT_NAME_OK_BUTTON_DINAMIC_POSTFIX_VXE0,
    OBJECT_NAME_TITLE_DINAMIC_POSTFIX_VXE0,
    SPACE_CHAR_DINAMIC_POSTFIX_VXE0,
)
from ui.editor import PythonHighlighter

from .formatting import normalize_code_for_view

DIALOG_WIDTH: int = 580
DIALOG_HEIGHT: int = 460
MIN_DIALOG_WIDTH: int = 420
MIN_DIALOG_HEIGHT: int = 300
BODY_MIN_HEIGHT: int = 220
OK_BUTTON_MIN_WIDTH: int = 168
OK_BUTTON_MIN_HEIGHT: int = 40
ROOT_MARGIN: int = 0
ROOT_SPACING: int = 0
HEADER_LEFT_MARGIN: int = 24
HEADER_RIGHT_MARGIN: int = 20
BODY_TOP_MARGIN: int = 16
BODY_BOTTOM_MARGIN: int = 12
FOOT_VERTICAL_MARGIN: int = 14
FOOTER_SPACING: int = 10
CODE_FONT_POINT_SIZE: int = 12
CODE_TAB_SPACES: int = 4
MONOSPACE_FONT_FAMILIES: tuple[str, ...] = (
    "JetBrains Mono",
    "Fira Code",
    "Cascadia Code",
    "Consolas",
)


class DetailTextDialog(QDialog):
    """Show a modal dialog with plain text or code details."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        window_title: str,
        body: str,
        is_code: bool = False,
    ) -> None:
        """Initialize detail text dialog.

        Args:
            parent: Parent widget.
            window_title: Window title text.
            body: Dialog body text content.
            is_code: Whether content should be shown as code.
        """
        super().__init__(parent)
        self._highlighter: PythonHighlighter | None = None
        self.setObjectName(OBJECT_NAME_DIALOG_DINAMIC_POSTFIX_VXE0)
        self.setWindowTitle(window_title)
        self.setModal(True)
        self.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        self.setMinimumSize(MIN_DIALOG_WIDTH, MIN_DIALOG_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        root: QVBoxLayout = QVBoxLayout(self)
        root.setContentsMargins(
            ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN
        )
        root.setSpacing(ROOT_SPACING)
        root.addWidget(self._build_header(window_title))
        root.addWidget(self._build_divider())
        text_view: QPlainTextEdit = self._build_text_view(
            body=body,
            is_code=is_code,
        )
        body_layout: QVBoxLayout = QVBoxLayout()
        body_layout.setContentsMargins(
            HEADER_LEFT_MARGIN,
            BODY_TOP_MARGIN,
            HEADER_LEFT_MARGIN,
            BODY_BOTTOM_MARGIN,
        )
        body_layout.setSpacing(ROOT_SPACING)
        body_layout.addWidget(text_view, 1)
        root.addLayout(body_layout, 1)
        root.addWidget(self._build_footer())

    def _build_header(self, window_title: str) -> QFrame:
        """Build dialog header frame.

        Args:
            window_title: Header title text.

        Returns:
            Configured header frame.
        """
        header: QFrame = QFrame()
        header.setObjectName(OBJECT_NAME_HEADER_DINAMIC_POSTFIX_VXE0)
        header_layout: QHBoxLayout = QHBoxLayout(header)
        header_layout.setContentsMargins(
            HEADER_LEFT_MARGIN, ROOT_MARGIN, HEADER_RIGHT_MARGIN, ROOT_MARGIN
        )
        title_label: QLabel = QLabel(window_title)
        title_label.setObjectName(OBJECT_NAME_TITLE_DINAMIC_POSTFIX_VXE0)
        header_layout.addWidget(title_label, 1, Qt.AlignmentFlag.AlignVCenter)
        return header

    def _build_divider(self) -> QFrame:
        """Build divider line widget.

        Returns:
            Configured divider frame.
        """
        divider: QFrame = QFrame()
        divider.setObjectName(OBJECT_NAME_DIVIDER_DINAMIC_POSTFIX_VXE0)
        return divider

    def _build_text_view(self, body: str, is_code: bool) -> QPlainTextEdit:
        """Build text area widget.

        Args:
            body: Dialog body text.
            is_code: Whether content is code.

        Returns:
            Configured text view widget.
        """
        text_view: QPlainTextEdit = QPlainTextEdit()
        text_view.setReadOnly(True)
        view_text: str = body or EMPTY_BODY_FALLBACK_DINAMIC_POSTFIX_VXE0
        if is_code:
            view_text = normalize_code_for_view(view_text)
        text_view.setPlainText(view_text)
        text_view.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.NoWrap
            if is_code
            else QPlainTextEdit.LineWrapMode.WidgetWidth
        )
        text_view.setObjectName(
            OBJECT_NAME_BODY_CODE_DINAMIC_POSTFIX_VXE0
            if is_code
            else OBJECT_NAME_BODY_DINAMIC_POSTFIX_VXE0
        )
        text_view.setMinimumHeight(BODY_MIN_HEIGHT)
        text_view.setTabChangesFocus(True)
        if is_code:
            self._configure_code_view(text_view)
        return text_view

    def _build_footer(self) -> QFrame:
        """Build dialog footer with close button.

        Returns:
            Configured footer frame.
        """
        footer: QFrame = QFrame()
        footer.setObjectName(OBJECT_NAME_FOOTER_DINAMIC_POSTFIX_VXE0)
        footer_layout: QHBoxLayout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(
            HEADER_LEFT_MARGIN,
            FOOT_VERTICAL_MARGIN,
            HEADER_LEFT_MARGIN,
            FOOT_VERTICAL_MARGIN,
        )
        footer_layout.setSpacing(FOOTER_SPACING)
        ok_button: QPushButton = QPushButton(
            CLOSE_BUTTON_TEXT_DINAMIC_POSTFIX_VXE0
        )
        ok_button.setObjectName(OBJECT_NAME_OK_BUTTON_DINAMIC_POSTFIX_VXE0)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setMinimumWidth(OK_BUTTON_MIN_WIDTH)
        ok_button.setMinimumHeight(OK_BUTTON_MIN_HEIGHT)
        ok_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        ok_button.clicked.connect(self.accept)
        footer_layout.addWidget(ok_button, 1)
        return footer

    def _configure_code_view(self, text_view: QPlainTextEdit) -> None:
        """Configure code-specific view settings.

        Args:
            text_view: Target text view widget.
        """
        font: QFont = QFont()
        font.setFamilies(list(MONOSPACE_FONT_FAMILIES))
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(CODE_FONT_POINT_SIZE)
        text_view.setFont(font)
        text_view.setTabStopDistance(
            text_view.fontMetrics().horizontalAdvance(
                SPACE_CHAR_DINAMIC_POSTFIX_VXE0
            )
            * CODE_TAB_SPACES
        )
        self._highlighter = PythonHighlighter(text_view.document(), dark=False)
