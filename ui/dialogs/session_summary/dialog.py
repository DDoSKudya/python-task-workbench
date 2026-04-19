"""
This module implements a modal Qt dialog (SessionSummaryDialog) that
shows a summary of a sessions task results, including statistics and
per-task rows with optional drill-down into reports and code.

It works by composing a vertically structured layout with a header, a
body containing stats chips and a scrollable list of task rows, and a
footer with an OK button, and by wiring row-level action buttons to open
reusable detail dialogs.

It defines numerous constants for sizing, margins, spacing, icon
dimensions, and a small set that controls which statistics chips are
hidden when their value is zero.

The SessionSummaryDialog constructor sets window properties, then builds
the header, divider, body layout (via _build_body_layout), and footer,
passing counts, task-row models, and the “all passed” flag to drive the
UI.

The _build_body_layout method creates a row of “chips” summarizing
counts for OK, bad, pending, and checking tasks, optionally adds a
success banner when all tasks passed, and constructs a scrollable list
host that contains individual task summary rows.

Each stats chip is built with _build_stats_chip, which produces a small
styled frame with the numeric value and label, and selectively omitted
for zero-valued labels configured in HIDDEN_ZERO_LABELS.

The _build_task_row method builds one row showing a status mark (using
mark_for_status and mark_object_name), a task number, a wrapped title
label, and an optional actions widget returned by _build_actions.

_build_actions creates icon buttons for viewing a report (if report_text
exists) and code (if code_text exists), hooking them up with
functools.partial to _show_report_sheet and _show_code_sheet.

The _create_action_button helper standardizes the appearance and
behavior of these icon buttons, setting object name, size, icon,
tooltip, and cursor.

Detail dialogs for report and code are delegated to DetailTextDialog via
_show_detail_sheet, with _show_code_sheet truncating long code bodies
and appending an ellipsis suffix when needed.

The footer is built by _build_footer, which shows a full-width OK
button (same layout as the new-session start button) that calls
accept() to close the dialog once the user has reviewed the summary.

Within the overall application, this dialog is presented at the end of a
session to give users a concise overview of how they performed and easy
access to per-task feedback.
"""

from __future__ import annotations

from functools import partial

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from messages import (
    CHIP_BAD_OBJECT_DINAMIC_POSTFIX_27PR,
    CHIP_NEUTRAL_OBJECT_DINAMIC_POSTFIX_27PR,
    CHIP_OK_OBJECT_DINAMIC_POSTFIX_27PR,
    CHIP_WARN_OBJECT_DINAMIC_POSTFIX_27PR,
    CODE_BUTTON_TOOLTIP_DINAMIC_POSTFIX_27PR,
    CODE_SUFFIX_ELLIPSIS_DINAMIC_POSTFIX_27PR,
    CODE_WINDOW_TITLE_DINAMIC_POSTFIX_27PR,
    EMPTY_BODY_FALLBACK_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_CHIP_LABEL_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_CHIP_VALUE_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_DIALOG_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_DIVIDER_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_FOOTER_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_HEADER_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_ICON_BUTTON_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_LIST_HOST_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_OK_BUTTON_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_ROW_ACTIONS_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_SCROLL_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_SCROLL_VIEWPORT_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_SECTION_CAPS_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_STATS_ROW_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_SUCCESS_BANNER_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_SUCCESS_TEXT_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_TASK_NUM_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_TASK_ROW_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_TASK_TITLE_DINAMIC_POSTFIX_27PR,
    OBJECT_NAME_TITLE_DINAMIC_POSTFIX_27PR,
    OK_BUTTON_TEXT_DINAMIC_POSTFIX_27PR,
    REPORT_BUTTON_TOOLTIP_DINAMIC_POSTFIX_27PR,
    REPORT_WINDOW_TITLE_DINAMIC_POSTFIX_27PR,
    STATS_BAD_LABEL_DINAMIC_POSTFIX_27PR,
    STATS_CHECKING_LABEL_DINAMIC_POSTFIX_27PR,
    STATS_OK_LABEL_DINAMIC_POSTFIX_27PR,
    STATS_PENDING_LABEL_DINAMIC_POSTFIX_27PR,
    SUCCESS_BANNER_TEXT_DINAMIC_POSTFIX_27PR,
    TITLE_SECTION_TASKS_DINAMIC_POSTFIX_27PR,
)
from ui import icons

from ..detail_text import DetailTextDialog
from .constants import SUMMARY_ICON_SIZE, SUMMARY_ICON_STROKE
from .marks import mark_for_status, mark_object_name
from .models import SessionSummaryTaskRow

WINDOW_MIN_WIDTH: int = 480
WINDOW_WIDTH: int = 560
WINDOW_HEIGHT: int = 540
ROOT_MARGIN: int = 0
ROOT_SPACING: int = 0
HEADER_LEFT_MARGIN: int = 24
HEADER_RIGHT_MARGIN: int = 20
BODY_LEFT_MARGIN: int = 24
BODY_RIGHT_MARGIN: int = 24
BODY_TOP_MARGIN: int = 20
BODY_BOTTOM_MARGIN: int = 16
BODY_SPACING: int = 16
STATS_SPACING: int = 10
CHIP_HORIZONTAL_MARGIN: int = 14
CHIP_VERTICAL_MARGIN: int = 12
CHIP_SPACING: int = 4
BANNER_HORIZONTAL_MARGIN: int = 14
BANNER_VERTICAL_MARGIN: int = 10
LIST_HOST_LEFT_MARGIN: int = 4
LIST_HOST_TOP_MARGIN: int = 4
LIST_HOST_RIGHT_MARGIN: int = 12
LIST_HOST_BOTTOM_MARGIN: int = 4
LIST_SPACING: int = 10
TASK_ROW_LEFT_MARGIN: int = 12
TASK_ROW_TOP_MARGIN: int = 8
TASK_ROW_RIGHT_MARGIN: int = 12
TASK_ROW_BOTTOM_MARGIN: int = 8
TASK_ROW_SPACING: int = 12
TASK_MARK_WIDTH: int = 28
ACTION_SPACING: int = 6
ACTION_BUTTON_SIZE: int = 34
SCROLL_MIN_HEIGHT: int = 220
FOOTER_LEFT_MARGIN: int = 20
FOOTER_TOP_MARGIN: int = 16
FOOTER_RIGHT_MARGIN: int = 20
FOOTER_BOTTOM_MARGIN: int = 16
FOOTER_SPACING: int = 10
OK_BUTTON_HEIGHT: int = 44
OK_BUTTON_MIN_WIDTH: int = 200
CODE_PREVIEW_LIMIT: int = 8000
HIDDEN_ZERO_LABELS: frozenset[str] = frozenset(
    {
        STATS_PENDING_LABEL_DINAMIC_POSTFIX_27PR,
        STATS_CHECKING_LABEL_DINAMIC_POSTFIX_27PR,
    }
)
LAYOUT_STRETCH: int = 1
NO_STRETCH: int = 0
ZERO_VALUE: int = 0


class SessionSummaryDialog(QDialog):
    """Show modal dialog with session summary results."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        heading: str,
        ok_n: int,
        bad_n: int,
        pend_n: int,
        chk_n: int,
        task_rows: list[SessionSummaryTaskRow],
        all_passed: bool,
    ) -> None:
        """Initialize session summary dialog.

        Args:
            parent: Optional parent widget.
            heading: Dialog heading title.
            ok_n: Number of correct tasks.
            bad_n: Number of incorrect tasks.
            pend_n: Number of pending tasks.
            chk_n: Number of tasks in progress.
            task_rows: Per-task summary rows.
            all_passed: Whether all tasks passed.

        """
        super().__init__(parent)
        self.setObjectName(OBJECT_NAME_DIALOG_DINAMIC_POSTFIX_27PR)
        self.setWindowTitle(heading)
        self.setModal(True)
        self.setMinimumWidth(WINDOW_MIN_WIDTH)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        root: QVBoxLayout = QVBoxLayout(self)
        root.setContentsMargins(
            ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN
        )
        root.setSpacing(ROOT_SPACING)
        root.addWidget(self._build_header(heading))
        root.addWidget(self._build_divider())
        root.addLayout(
            self._build_body_layout(
                ok_n=ok_n,
                bad_n=bad_n,
                pend_n=pend_n,
                chk_n=chk_n,
                task_rows=task_rows,
                all_passed=all_passed,
            ),
            LAYOUT_STRETCH,
        )
        root.addWidget(self._build_footer())

    def _build_body_layout(
        self,
        *,
        ok_n: int,
        bad_n: int,
        pend_n: int,
        chk_n: int,
        task_rows: list[SessionSummaryTaskRow],
        all_passed: bool,
    ) -> QVBoxLayout:
        """Build body layout with stats and task rows.

        Args:
            ok_n: Number of correct tasks.
            bad_n: Number of incorrect tasks.
            pend_n: Number of pending tasks.
            chk_n: Number of tasks in progress.
            task_rows: Summary rows for tasks.
            all_passed: Whether all tasks are solved.

        Returns:
            Configured body layout.
        """
        body: QVBoxLayout = QVBoxLayout()
        body.setContentsMargins(
            BODY_LEFT_MARGIN,
            BODY_TOP_MARGIN,
            BODY_RIGHT_MARGIN,
            BODY_BOTTOM_MARGIN,
        )
        body.setSpacing(BODY_SPACING)
        stats_row: QFrame = QFrame()
        stats_row.setObjectName(OBJECT_NAME_STATS_ROW_DINAMIC_POSTFIX_27PR)
        stats_layout: QHBoxLayout = QHBoxLayout(stats_row)
        stats_layout.setContentsMargins(
            ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN
        )
        stats_layout.setSpacing(STATS_SPACING)
        chips: list[tuple[str, int, str]] = [
            (
                STATS_OK_LABEL_DINAMIC_POSTFIX_27PR,
                ok_n,
                CHIP_OK_OBJECT_DINAMIC_POSTFIX_27PR,
            ),
            (
                STATS_BAD_LABEL_DINAMIC_POSTFIX_27PR,
                bad_n,
                CHIP_BAD_OBJECT_DINAMIC_POSTFIX_27PR,
            ),
            (
                STATS_PENDING_LABEL_DINAMIC_POSTFIX_27PR,
                pend_n,
                CHIP_NEUTRAL_OBJECT_DINAMIC_POSTFIX_27PR,
            ),
            (
                STATS_CHECKING_LABEL_DINAMIC_POSTFIX_27PR,
                chk_n,
                CHIP_WARN_OBJECT_DINAMIC_POSTFIX_27PR,
            ),
        ]
        for label, value, chip_name in chips:
            if value == ZERO_VALUE and label in HIDDEN_ZERO_LABELS:
                continue
            stats_layout.addWidget(
                self._build_stats_chip(label, value, chip_name),
                LAYOUT_STRETCH,
            )
        body.addWidget(stats_row)
        if all_passed:
            banner: QFrame = QFrame()
            banner.setObjectName(
                OBJECT_NAME_SUCCESS_BANNER_DINAMIC_POSTFIX_27PR
            )
            banner_layout: QHBoxLayout = QHBoxLayout(banner)
            banner_layout.setContentsMargins(
                BANNER_HORIZONTAL_MARGIN,
                BANNER_VERTICAL_MARGIN,
                BANNER_HORIZONTAL_MARGIN,
                BANNER_VERTICAL_MARGIN,
            )
            banner_label: QLabel = QLabel(
                SUCCESS_BANNER_TEXT_DINAMIC_POSTFIX_27PR
            )
            banner_label.setObjectName(
                OBJECT_NAME_SUCCESS_TEXT_DINAMIC_POSTFIX_27PR
            )
            banner_label.setWordWrap(True)
            banner_layout.addWidget(banner_label)
            body.addWidget(banner)
        section: QLabel = QLabel(TITLE_SECTION_TASKS_DINAMIC_POSTFIX_27PR)
        section.setObjectName(OBJECT_NAME_SECTION_CAPS_DINAMIC_POSTFIX_27PR)
        body.addWidget(section)
        list_host: QWidget = QWidget()
        list_host.setObjectName(OBJECT_NAME_LIST_HOST_DINAMIC_POSTFIX_27PR)
        list_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        list_layout: QVBoxLayout = QVBoxLayout(list_host)
        list_layout.setContentsMargins(
            LIST_HOST_LEFT_MARGIN,
            LIST_HOST_TOP_MARGIN,
            LIST_HOST_RIGHT_MARGIN,
            LIST_HOST_BOTTOM_MARGIN,
        )
        list_layout.setSpacing(LIST_SPACING)
        for row in task_rows:
            list_layout.addWidget(self._build_task_row(row))
        scroll: QScrollArea = QScrollArea()
        scroll.setObjectName(OBJECT_NAME_SCROLL_DINAMIC_POSTFIX_27PR)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        viewport = scroll.viewport()
        if viewport is not None:
            viewport.setObjectName(
                OBJECT_NAME_SCROLL_VIEWPORT_DINAMIC_POSTFIX_27PR
            )
            viewport.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        scroll.setWidget(list_host)
        scroll.setMinimumHeight(SCROLL_MIN_HEIGHT)
        body.addWidget(scroll, LAYOUT_STRETCH)
        return body

    def _build_footer(self) -> QFrame:
        """Build footer frame with accept button.

        Returns:
            Footer frame widget.
        """
        foot: QFrame = QFrame()
        foot.setObjectName(OBJECT_NAME_FOOTER_DINAMIC_POSTFIX_27PR)
        footer_layout: QHBoxLayout = QHBoxLayout(foot)
        footer_layout.setContentsMargins(
            FOOTER_LEFT_MARGIN,
            FOOTER_TOP_MARGIN,
            FOOTER_RIGHT_MARGIN,
            FOOTER_BOTTOM_MARGIN,
        )
        footer_layout.setSpacing(FOOTER_SPACING)
        ok_btn: QPushButton = QPushButton(OK_BUTTON_TEXT_DINAMIC_POSTFIX_27PR)
        ok_btn.setObjectName(OBJECT_NAME_OK_BUTTON_DINAMIC_POSTFIX_27PR)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        ok_btn.setFixedHeight(OK_BUTTON_HEIGHT)
        ok_btn.setMinimumWidth(OK_BUTTON_MIN_WIDTH)
        ok_btn.clicked.connect(self.accept)
        footer_layout.addWidget(ok_btn, LAYOUT_STRETCH)
        return foot

    def _build_header(self, heading: str) -> QFrame:
        """Build dialog header.

        Args:
            heading: Dialog title text.

        Returns:
            Header frame widget.
        """
        header: QFrame = QFrame()
        header.setObjectName(OBJECT_NAME_HEADER_DINAMIC_POSTFIX_27PR)
        layout: QHBoxLayout = QHBoxLayout(header)
        layout.setContentsMargins(
            HEADER_LEFT_MARGIN, ROOT_MARGIN, HEADER_RIGHT_MARGIN, ROOT_MARGIN
        )
        title_label: QLabel = QLabel(heading)
        title_label.setObjectName(OBJECT_NAME_TITLE_DINAMIC_POSTFIX_27PR)
        layout.addWidget(
            title_label, LAYOUT_STRETCH, Qt.AlignmentFlag.AlignVCenter
        )
        return header

    def _build_divider(self) -> QFrame:
        """Build divider frame below header.

        Returns:
            Divider frame widget.
        """
        divider: QFrame = QFrame()
        divider.setObjectName(OBJECT_NAME_DIVIDER_DINAMIC_POSTFIX_27PR)
        return divider

    def _build_stats_chip(
        self, label: str, value: int, chip_object_name: str
    ) -> QFrame:
        """Build one statistics chip.

        Args:
            label: Chip label text.
            value: Chip numeric value.
            chip_object_name: Object name for style.

        Returns:
            Chip frame widget.
        """
        chip: QFrame = QFrame()
        chip.setObjectName(chip_object_name)
        layout: QVBoxLayout = QVBoxLayout(chip)
        layout.setContentsMargins(
            CHIP_HORIZONTAL_MARGIN,
            CHIP_VERTICAL_MARGIN,
            CHIP_HORIZONTAL_MARGIN,
            CHIP_VERTICAL_MARGIN,
        )
        layout.setSpacing(CHIP_SPACING)
        value_label: QLabel = QLabel(str(value))
        value_label.setObjectName(OBJECT_NAME_CHIP_VALUE_DINAMIC_POSTFIX_27PR)
        label_widget: QLabel = QLabel(label)
        label_widget.setObjectName(OBJECT_NAME_CHIP_LABEL_DINAMIC_POSTFIX_27PR)
        label_widget.setWordWrap(True)
        layout.addWidget(value_label)
        layout.addWidget(label_widget)
        return chip

    def _build_task_row(self, row: SessionSummaryTaskRow) -> QFrame:
        """Build one summary row widget.

        Args:
            row: Session summary row model.

        Returns:
            Summary row frame.
        """
        frame: QFrame = QFrame()
        frame.setObjectName(OBJECT_NAME_TASK_ROW_DINAMIC_POSTFIX_27PR)
        layout: QHBoxLayout = QHBoxLayout(frame)
        layout.setContentsMargins(
            TASK_ROW_LEFT_MARGIN,
            TASK_ROW_TOP_MARGIN,
            TASK_ROW_RIGHT_MARGIN,
            TASK_ROW_BOTTOM_MARGIN,
        )
        layout.setSpacing(TASK_ROW_SPACING)
        mark: QLabel = QLabel(mark_for_status(row.status))
        mark.setObjectName(mark_object_name(row.status))
        mark.setFixedWidth(TASK_MARK_WIDTH)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num_label: QLabel = QLabel(f"#{row.num}")
        num_label.setObjectName(OBJECT_NAME_TASK_NUM_DINAMIC_POSTFIX_27PR)
        title_label: QLabel = QLabel(row.title)
        title_label.setObjectName(OBJECT_NAME_TASK_TITLE_DINAMIC_POSTFIX_27PR)
        title_label.setWordWrap(True)
        title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(mark, NO_STRETCH)
        layout.addWidget(num_label, NO_STRETCH)
        layout.addWidget(title_label, LAYOUT_STRETCH)
        actions = self._build_actions(row)
        if actions is not None:
            layout.addWidget(
                actions, NO_STRETCH, Qt.AlignmentFlag.AlignVCenter
            )
        return frame

    def _build_actions(self, row: SessionSummaryTaskRow) -> QWidget | None:
        """Build action buttons for one summary row.

        Args:
            row: Session summary row model.

        Returns:
            Actions widget or `None` when no actions exist.
        """
        if row.report_text is None and (not row.code_text):
            return None
        actions: QWidget = QWidget()
        actions.setObjectName(OBJECT_NAME_ROW_ACTIONS_DINAMIC_POSTFIX_27PR)
        layout: QHBoxLayout = QHBoxLayout(actions)
        layout.setContentsMargins(
            ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN
        )
        layout.setSpacing(ACTION_SPACING)
        if row.report_text is not None:
            report_button: QPushButton = self._create_action_button(
                icon=icons.icon_file_text(
                    stroke=SUMMARY_ICON_STROKE, size=SUMMARY_ICON_SIZE
                ),
                tooltip=REPORT_BUTTON_TOOLTIP_DINAMIC_POSTFIX_27PR,
            )
            report_button.clicked.connect(
                partial(self._show_report_sheet, row.report_text)
            )
            layout.addWidget(report_button)
        if row.code_text:
            code_button: QPushButton = self._create_action_button(
                icon=icons.icon_code(
                    stroke=SUMMARY_ICON_STROKE, size=SUMMARY_ICON_SIZE
                ),
                tooltip=CODE_BUTTON_TOOLTIP_DINAMIC_POSTFIX_27PR,
            )
            code_button.clicked.connect(
                partial(self._show_code_sheet, row.code_text)
            )
            layout.addWidget(code_button)
        return actions

    def _create_action_button(
        self, *, icon: QIcon, tooltip: str
    ) -> QPushButton:
        """Create summary row action button.

        Args:
            icon: Icon object for button.
            tooltip: Tooltip text.

        Returns:
            Configured button.
        """
        button: QPushButton = QPushButton()
        button.setObjectName(OBJECT_NAME_ICON_BUTTON_DINAMIC_POSTFIX_27PR)
        button.setIcon(icon)
        button.setIconSize(QSize(SUMMARY_ICON_SIZE, SUMMARY_ICON_SIZE))
        button.setFixedSize(ACTION_BUTTON_SIZE, ACTION_BUTTON_SIZE)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _show_detail_sheet(
        self,
        *,
        title: str,
        body: str,
        is_code: bool,
    ) -> None:
        """Open reusable detail dialog for summary row actions.

        Args:
            title: Window title text.
            body: Dialog body text.
            is_code: Whether to render body as code.
        """
        DetailTextDialog(
            self,
            window_title=title,
            body=body or EMPTY_BODY_FALLBACK_DINAMIC_POSTFIX_27PR,
            is_code=is_code,
        ).exec()

    def _show_report_sheet(self, text: str) -> None:
        """Open report details sheet.

        Args:
            text: Report content text.

        """
        self._show_detail_sheet(
            title=REPORT_WINDOW_TITLE_DINAMIC_POSTFIX_27PR,
            body=text,
            is_code=False,
        )

    def _show_code_sheet(self, code: str) -> None:
        """Open code details sheet.

        Args:
            code: Source code text.

        """
        body: str = code[:CODE_PREVIEW_LIMIT]
        if len(code) > CODE_PREVIEW_LIMIT:
            body += CODE_SUFFIX_ELLIPSIS_DINAMIC_POSTFIX_27PR
        self._show_detail_sheet(
            title=CODE_WINDOW_TITLE_DINAMIC_POSTFIX_27PR,
            body=body,
            is_code=True,
        )
