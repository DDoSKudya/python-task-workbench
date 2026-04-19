"""
This module implements the Qt UI for browsing, filtering, inspecting,
and exporting check history entries in a non-modal dialog.

It works by loading HistoryRowView records from the core history store,
presenting them in a searchable QTableWidget, and providing secondary
dialogs and actions for detailed inspection, code/report viewing,
exporting to Python files, and clearing history.

It defines a large set of layout constants, sizing parameters, column
indices, and style-related values (including a CSS-like stylesheet)
that control both the main history dialog and the entry-details dialog.

The HistoryDialog class builds the main window with a header (title plus
clear/export buttons), a body containing a search bar and table, and a
footer showing the count of visible entries, wiring signals for search
filtering, cell clicks, and header button actions.

History rows are loaded via load_entries_newest_first, filtered in
_filtered_rows against the search text across several fields, and
mapped into table rows with timestamp, task cell text (using
task_cell_text and pack_label), a colored pass/fail mark, and an actions
widget containing report, code, and export buttons.

Export functions _export_row and _export_all_rows use Qt file dialogs
and the core export_history_entry_to_python /
export_history_rows_to_python APIs to write .py files to disk, with
error handling and confirmation via QMessageBox.

The _show_report and _show_code methods open a DetailTextDialog to show,
respectively, a textual report (result or error, with success fallback
and “actual” embedding) and a truncated code preview, optionally
appending a truncation suffix.

The _on_clear handler prompts the user for confirmation and, on
approval, calls clear_history_file and reloads the table, integrating
history management into the UI.

The HistoryEntryDetailsDialog class provides a structured modal view for
a single history entry, showing a metadata card with ID, time, pack,
status, and duration, and several text sections for input, expected
output, actual result, error text, and full code.

Sections in the details dialog use read-only QPlainTextEdit widgets,
optionally set to monospace fonts with PythonHighlighter for code-like
content and no line wrapping for code, offering a rich, inspectable view
of each checks context and outcome.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from functools import partial

from pathlib import Path
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QIcon, QShowEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.check_history import (
    HistoryRowView,
    clear_history_file,
    default_history_export_filename,
    export_history_entry_to_python,
    export_history_rows_to_python,
    load_entries_newest_first,
)
from messages import (
    CLEAR_HISTORY_DIALOG_TEXT_DINAMIC_POSTFIX_P101,
    CLEAR_HISTORY_DIALOG_TITLE_DINAMIC_POSTFIX_P101,
    CLEAR_HISTORY_TOOLTIP_DINAMIC_POSTFIX_P101,
    CODE_BUTTON_TOOLTIP_DINAMIC_POSTFIX_P101,
    CODE_TRUNCATION_SUFFIX_DINAMIC_POSTFIX_P101,
    CODE_WINDOW_TITLE_DINAMIC_POSTFIX_P101,
    COUNT_LABEL_TEMPLATE_DINAMIC_POSTFIX_P101,
    EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
    FAIL_COLOR_DINAMIC_POSTFIX_P101,
    FAIL_MARK_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_LABEL_DURATION_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_LABEL_ID_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_LABEL_PACK_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_LABEL_STATUS_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_LABEL_WHEN_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_SECTION_CODE_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_SECTION_ERROR_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_STATUS_FAILED_DINAMIC_POSTFIX_P101,
    HISTORY_DETAILS_STATUS_PASSED_DINAMIC_POSTFIX_P101,
    HISTORY_EXPORT_ALL_DONE_MESSAGE_DINAMIC_POSTFIX_P101,
    HISTORY_EXPORT_ALL_TEXT_DINAMIC_POSTFIX_P101,
    HISTORY_EXPORT_DIALOG_TITLE_DINAMIC_POSTFIX_P101,
    HISTORY_EXPORT_DIR_DIALOG_TITLE_DINAMIC_POSTFIX_P101,
    HISTORY_EXPORT_DONE_MESSAGE_DINAMIC_POSTFIX_P101,
    HISTORY_EXPORT_EMPTY_MESSAGE_DINAMIC_POSTFIX_P101,
    HISTORY_EXPORT_FILE_FILTER_DINAMIC_POSTFIX_P101,
    HISTORY_EXPORT_TOOLTIP_DINAMIC_POSTFIX_P101,
    HISTORY_ROW_DETAILS_TITLE_DINAMIC_POSTFIX_P101,
    HISTORY_TABLE_ACTIONS_DINAMIC_POSTFIX_P101,
    HISTORY_TABLE_RESULT_DINAMIC_POSTFIX_P101,
    HISTORY_TABLE_TASK_DINAMIC_POSTFIX_P101,
    HISTORY_TABLE_WHEN_DINAMIC_POSTFIX_P101,
    INPUT_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
    OBJECT_NAME_CLEAR_BUTTON_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_COUNT_LABEL_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_DIALOG_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_FOOTER_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_HEADER_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_PANEL_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_SEARCH_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_SECONDARY_BUTTON_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_TABLE_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_TABLE_HEADER_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_TABLE_ICON_BUTTON_DINAMIC_POSTFIX_P101,
    OBJECT_NAME_TITLE_DINAMIC_POSTFIX_P101,
    OUTPUT_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
    REPORT_ACTUAL_TEMPLATE_DINAMIC_POSTFIX_P101,
    REPORT_BUTTON_TOOLTIP_DINAMIC_POSTFIX_P101,
    REPORT_WINDOW_TITLE_DINAMIC_POSTFIX_P101,
    SEARCH_BUTTON_TEXT_DINAMIC_POSTFIX_P101,
    SEARCH_PLACEHOLDER_DINAMIC_POSTFIX_P101,
    SUCCESS_COLOR_DINAMIC_POSTFIX_P101,
    SUCCESS_MARK_DINAMIC_POSTFIX_P101,
    SUCCESS_REPORT_TEXT_DINAMIC_POSTFIX_P101,
    TASK_TOOLTIP_TEMPLATE_DINAMIC_POSTFIX_P101,
    TRASH_ICON_STROKE_DINAMIC_POSTFIX_P101,
    WINDOW_TITLE_DINAMIC_POSTFIX_P101,
)
from ui import icons
from ui.editor import PythonHighlighter

from ..common import pack_label
from ..detail_text import DetailTextDialog
from .cells import task_cell_text

DIALOG_WIDTH: int = 1100
DIALOG_HEIGHT: int = 600
MIN_DIALOG_WIDTH: int = 800
MIN_DIALOG_HEIGHT: int = 400
ROOT_MARGIN: int = 0
ROOT_SPACING: int = 0
HEADER_HEIGHT: int = 64
HEADER_LEFT_MARGIN: int = 24
HEADER_RIGHT_MARGIN: int = 16
PANEL_INNER_MARGIN: int = 16
PANEL_TOP_MARGIN: int = 14
PANEL_SPACING: int = 14
BODY_TOP_MARGIN: int = 16
BODY_BOTTOM_MARGIN: int = 12
FOOTER_SPACING: int = 8
SMALL_VERTICAL_MARGIN: int = 2
SEARCH_ROW_SPACING: int = 10
CLEAR_BUTTON_SIZE: int = 40
CLEAR_ICON_SIZE: int = 18
SEARCH_BUTTON_HEIGHT: int = 36
SEARCH_BUTTON_MIN_WIDTH: int = 88
ROW_HEIGHT: int = 48
TIMESTAMP_COLUMN_WIDTH: int = 158
STATUS_COLUMN_WIDTH: int = 56
ACTIONS_COLUMN_WIDTH: int = 88
ACTION_ICON_SIZE: int = 16
CODE_PREVIEW_LIMIT: int = 8000
TABLE_COL_TIMESTAMP: int = 0
TABLE_COL_TASK: int = 1
TABLE_COL_RESULT: int = 2
TABLE_COL_ACTIONS: int = 3
LAYOUT_STRETCH: int = 1
BUTTON_NO_STRETCH: int = 0
ROW_EXPORT_TEXT: str = "Py"
PY_FILE_SUFFIX: str = ".py"
HEADER_TEXT_PADDING: int = 24
ACTION_BUTTON_COUNT: int = 3
ACTION_BUTTON_SIZE: int = 28
ACTIONS_LAYOUT_PADDING: int = 0
ACTIONS_LAYOUT_SPACING: int = 2
RESULT_COLUMN_EXTRA_WIDTH: int = 12
TABLE_MIN_SECTION_SIZE: int = 32
TITLE_WIDTH_RATIO: int = 10
NORMALIZED_TS_FORMAT: str = "%d.%m.%Y %H:%M:%S"
DETAIL_DIALOG_WIDTH: int = 1240
DETAIL_DIALOG_HEIGHT: int = 920
DETAIL_MIN_DIALOG_WIDTH: int = 1080
DETAIL_MIN_DIALOG_HEIGHT: int = 760
DETAIL_ROOT_MARGIN_LEFT: int = 16
DETAIL_ROOT_MARGIN_TOP: int = 14
DETAIL_ROOT_MARGIN_RIGHT: int = 16
DETAIL_ROOT_MARGIN_BOTTOM: int = 14
DETAIL_ROOT_SPACING: int = 12
DETAIL_CARD_MARGIN_LEFT: int = 14
DETAIL_CARD_MARGIN_TOP: int = 12
DETAIL_CARD_MARGIN_RIGHT: int = 14
DETAIL_CARD_MARGIN_BOTTOM: int = 12
DETAIL_CARD_SPACING: int = 16
DETAIL_FIELD_GAP: int = 10
DETAIL_META_BLOCK_MARGIN_LEFT: int = 12
DETAIL_META_BLOCK_MARGIN_TOP: int = 10
DETAIL_META_BLOCK_MARGIN_RIGHT: int = 12
DETAIL_META_BLOCK_MARGIN_BOTTOM: int = 10
DETAIL_META_BLOCK_SPACING: int = 4
DETAIL_BODY_MIN_HEIGHT: int = 96
DETAIL_CODE_MIN_HEIGHT: int = 160
DETAIL_MONO_FONT_SIZE: int = 12
DETAIL_MONO_FONT_FAMILIES: tuple[str, ...] = (
    "JetBrains Mono",
    "Fira Code",
    "Cascadia Code",
    "Consolas",
)
DETAIL_DIALOG_OBJECT_NAME: str = "CT_HistoryEntryDetailsDialog"
DETAIL_META_CARD_OBJECT_NAME: str = "CT_HistoryEntryMetaCard"
DETAIL_SECTION_OBJECT_NAME: str = "CT_HistoryEntrySection"
DETAIL_META_BLOCK_OBJECT_NAME: str = "CT_HistoryMetaBlock"
DETAIL_META_KEY_OBJECT_NAME: str = "CT_HistoryEntryMetaKey"
DETAIL_META_VALUE_OBJECT_NAME: str = "CT_HistoryEntryMetaValue"
DETAIL_META_TITLE_OBJECT_NAME: str = "CT_HistoryEntryMetaTitle"
DETAIL_SECTION_TITLE_OBJECT_NAME: str = "CT_HistoryEntrySectionTitle"
DETAIL_BODY_OBJECT_NAME: str = "CT_HistoryEntryBody"
DETAIL_STYLE_SHEET: str = """
QDialog#CT_HistoryEntryDetailsDialog { background-color: #FFFFFF; }
QFrame#CT_HistoryEntryMetaCard, QFrame#CT_HistoryEntrySection {
    background-color: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
}
QFrame#CT_HistoryMetaBlock {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
}
QLabel#CT_HistoryEntryMetaKey {
    color: #6B7280;
    font-size: 11px;
    font-weight: 600;
}
QLabel#CT_HistoryEntryMetaValue {
    color: #111827;
    font-size: 13px;
    font-weight: 600;
}
QLabel#CT_HistoryEntryMetaTitle {
    color: #111827;
    font-size: 17px;
    font-weight: 700;
}
QLabel#CT_HistoryEntrySectionTitle {
    color: #111827;
    font-size: 12px;
    font-weight: 700;
}
QPlainTextEdit#CT_HistoryEntryBody {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    color: #111827;
    padding: 8px;
}
"""


class HistoryDialog(QDialog):
    """Show non-modal history dialog for solution checks."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize history dialog UI and load entries.

        Args:
            parent: Optional parent widget.

        Returns:
            None.
        """
        super().__init__(parent)
        self.setObjectName(OBJECT_NAME_DIALOG_DINAMIC_POSTFIX_P101)
        self.setWindowTitle(WINDOW_TITLE_DINAMIC_POSTFIX_P101)
        self.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        self.setMinimumSize(MIN_DIALOG_WIDTH, MIN_DIALOG_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._header_labels = (
            HISTORY_TABLE_WHEN_DINAMIC_POSTFIX_P101,
            HISTORY_TABLE_TASK_DINAMIC_POSTFIX_P101,
            HISTORY_TABLE_RESULT_DINAMIC_POSTFIX_P101,
            HISTORY_TABLE_ACTIONS_DINAMIC_POSTFIX_P101,
        )
        self._rows: list[HistoryRowView] = []
        self._visible_rows: list[HistoryRowView] = []
        self._search = QLineEdit()
        self._table = QTableWidget(BUTTON_NO_STRETCH, len(self._header_labels))
        self._count_lbl = QLabel()
        self._build_ui()
        self._reload()

    def _build_ui(self) -> None:
        """Build dialog widget tree.

        Returns:
            None.
        """
        root = QVBoxLayout(self)
        root.setContentsMargins(
            ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN
        )
        root.setSpacing(ROOT_SPACING)
        root.addWidget(self._build_header())
        root.addLayout(self._build_body(), LAYOUT_STRETCH)
        root.addWidget(self._build_footer())

    def _build_header(self) -> QFrame:
        """Build header bar with title and clear action.

        Returns:
            Configured header frame.
        """
        header = QFrame()
        header.setObjectName(OBJECT_NAME_HEADER_DINAMIC_POSTFIX_P101)
        header.setFixedHeight(HEADER_HEIGHT)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(
            HEADER_LEFT_MARGIN, ROOT_MARGIN, HEADER_RIGHT_MARGIN, ROOT_MARGIN
        )
        title = QLabel(WINDOW_TITLE_DINAMIC_POSTFIX_P101)
        title.setObjectName(OBJECT_NAME_TITLE_DINAMIC_POSTFIX_P101)
        clear_button = self._create_header_icon_button(
            icon=icons.icon_trash(
                stroke=TRASH_ICON_STROKE_DINAMIC_POSTFIX_P101,
                size=CLEAR_ICON_SIZE,
            ),
            tooltip=CLEAR_HISTORY_TOOLTIP_DINAMIC_POSTFIX_P101,
            callback=self._on_clear,
            object_name=OBJECT_NAME_CLEAR_BUTTON_DINAMIC_POSTFIX_P101,
        )
        export_button = self._create_header_icon_button(
            icon=icons.icon_file_text(
                stroke=SUCCESS_COLOR_DINAMIC_POSTFIX_P101,
                size=CLEAR_ICON_SIZE,
            ),
            tooltip=HISTORY_EXPORT_ALL_TEXT_DINAMIC_POSTFIX_P101,
            callback=self._export_all_rows,
            object_name=OBJECT_NAME_TABLE_ICON_BUTTON_DINAMIC_POSTFIX_P101,
        )
        layout.addWidget(title, LAYOUT_STRETCH, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(
            export_button, BUTTON_NO_STRETCH, Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(
            clear_button, BUTTON_NO_STRETCH, Qt.AlignmentFlag.AlignVCenter
        )
        return header

    def _create_header_icon_button(
        self,
        *,
        icon: QIcon,
        tooltip: str,
        callback: Callable[[], None],
        object_name: str,
    ) -> QPushButton:
        """Build a small icon-only button for the dialog header.

        Args:
            icon: Icon to render inside the button.
            tooltip: Tooltip text.
            callback: Slot invoked on click.
            object_name: Qt object name for styling.

        Returns:
            Configured icon button.
        """
        button = QPushButton()
        button.setObjectName(object_name)
        button.setFixedSize(CLEAR_BUTTON_SIZE, CLEAR_BUTTON_SIZE)
        button.setIcon(icon)
        button.setIconSize(QSize(CLEAR_ICON_SIZE, CLEAR_ICON_SIZE))
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(callback)
        return button

    def _build_body(self) -> QVBoxLayout:
        """Build body section with search and table.

        Returns:
            Configured body layout.
        """
        body = QVBoxLayout()
        body.setContentsMargins(
            HEADER_LEFT_MARGIN,
            BODY_TOP_MARGIN,
            HEADER_LEFT_MARGIN,
            BODY_BOTTOM_MARGIN,
        )
        body.setSpacing(ROOT_SPACING)
        panel = self._build_panel()
        body.addWidget(panel, LAYOUT_STRETCH)
        return body

    def _build_panel(self) -> QFrame:
        """Build main panel container.

        Returns:
            Configured panel frame.
        """
        panel = QFrame()
        panel.setObjectName(OBJECT_NAME_PANEL_DINAMIC_POSTFIX_P101)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            PANEL_INNER_MARGIN,
            PANEL_TOP_MARGIN,
            PANEL_INNER_MARGIN,
            PANEL_TOP_MARGIN,
        )
        layout.setSpacing(PANEL_SPACING)
        layout.addLayout(self._build_search_row())
        layout.addWidget(self._build_table(), LAYOUT_STRETCH)
        return panel

    def _build_search_row(self) -> QHBoxLayout:
        """Build search controls row.

        Returns:
            Configured search row layout.
        """
        search_row = QHBoxLayout()
        search_row.setSpacing(SEARCH_ROW_SPACING)
        self._search.setObjectName(OBJECT_NAME_SEARCH_DINAMIC_POSTFIX_P101)
        self._search.setPlaceholderText(
            SEARCH_PLACEHOLDER_DINAMIC_POSTFIX_P101
        )
        self._search.textChanged.connect(self._apply_filter)
        btn_find = QPushButton(SEARCH_BUTTON_TEXT_DINAMIC_POSTFIX_P101)
        btn_find.setObjectName(
            OBJECT_NAME_SECONDARY_BUTTON_DINAMIC_POSTFIX_P101
        )
        btn_find.setFixedHeight(SEARCH_BUTTON_HEIGHT)
        btn_find.setMinimumWidth(SEARCH_BUTTON_MIN_WIDTH)
        btn_find.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_find.clicked.connect(self._apply_filter)
        search_row.addWidget(self._search, LAYOUT_STRETCH)
        search_row.addWidget(btn_find, BUTTON_NO_STRETCH)
        return search_row

    def _build_table(self) -> QTableWidget:
        """Build history table widget.

        Returns:
            Configured table widget.
        """
        self._table.setObjectName(OBJECT_NAME_TABLE_DINAMIC_POSTFIX_P101)
        self._table.setHorizontalHeaderLabels(list(self._header_labels))
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._table.setShowGrid(True)
        vertical_header = self._table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
            vertical_header.setDefaultSectionSize(ROW_HEIGHT)
        header = self._table.horizontalHeader()
        if header is not None:
            header.setObjectName(OBJECT_NAME_TABLE_HEADER_DINAMIC_POSTFIX_P101)
            header.setHighlightSections(False)
            header.setSectionResizeMode(
                TABLE_COL_TIMESTAMP, QHeaderView.ResizeMode.Fixed
            )
            header.setSectionResizeMode(
                TABLE_COL_TASK, QHeaderView.ResizeMode.Stretch
            )
            header.setSectionResizeMode(
                TABLE_COL_RESULT, QHeaderView.ResizeMode.Interactive
            )
            header.setSectionResizeMode(
                TABLE_COL_ACTIONS, QHeaderView.ResizeMode.Interactive
            )
            header.setMinimumSectionSize(TABLE_MIN_SECTION_SIZE)
        self._table.setColumnWidth(TABLE_COL_TIMESTAMP, TIMESTAMP_COLUMN_WIDTH)
        self._apply_column_widths()
        self._table.cellClicked.connect(self._on_table_cell_clicked)
        return self._table

    def _min_header_width(self, title: str) -> int:
        """Return minimum width to fit header title text."""
        header = self._table.horizontalHeader()
        if header is None:
            return len(title) * TITLE_WIDTH_RATIO + HEADER_TEXT_PADDING
        metrics = QFontMetrics(header.font())
        return metrics.horizontalAdvance(title) + HEADER_TEXT_PADDING

    def _apply_column_widths(self) -> None:
        """Apply adaptive widths for result/actions columns."""
        result_min = self._min_header_width(
            self._header_labels[TABLE_COL_RESULT]
        )
        actions_min_by_text = self._min_header_width(
            self._header_labels[TABLE_COL_ACTIONS]
        )
        actions_min_by_icons = (
            (ACTION_BUTTON_SIZE * ACTION_BUTTON_COUNT)
            + ACTIONS_LAYOUT_PADDING
            + (ACTIONS_LAYOUT_SPACING * (ACTION_BUTTON_COUNT - 1))
        )
        actions_width = max(actions_min_by_text, actions_min_by_icons)
        result_width = max(
            result_min,
            STATUS_COLUMN_WIDTH,
            actions_width + RESULT_COLUMN_EXTRA_WIDTH,
        )
        self._table.setColumnWidth(TABLE_COL_RESULT, result_width)
        self._table.setColumnWidth(
            TABLE_COL_ACTIONS,
            max(actions_width, ACTIONS_COLUMN_WIDTH),
        )

    def _normalize_timestamp(self, ts: str) -> str:
        """Render ISO timestamp into a concise local format."""
        try:
            parsed = datetime.fromisoformat(ts)
        except ValueError:
            return ts
        return parsed.strftime(NORMALIZED_TS_FORMAT)

    def _build_footer(self) -> QFrame:
        """Build footer with entries count label.

        Returns:
            Configured footer frame.
        """
        footer_wrap = QFrame()
        footer_wrap.setObjectName(OBJECT_NAME_FOOTER_DINAMIC_POSTFIX_P101)
        footer = QHBoxLayout(footer_wrap)
        footer.setContentsMargins(
            HEADER_LEFT_MARGIN, ROOT_MARGIN, HEADER_LEFT_MARGIN, ROOT_MARGIN
        )
        footer.setSpacing(FOOTER_SPACING)
        self._count_lbl.setObjectName(
            OBJECT_NAME_COUNT_LABEL_DINAMIC_POSTFIX_P101
        )
        footer.addStretch(LAYOUT_STRETCH)
        footer.addWidget(
            self._count_lbl,
            BUTTON_NO_STRETCH,
            Qt.AlignmentFlag.AlignVCenter,
        )
        return footer_wrap

    def showEvent(self, a0: QShowEvent | None) -> None:
        """Reload history every time dialog becomes visible.

        Args:
            a0: Qt show event instance.

        Returns:
            None.
        """
        super().showEvent(a0)
        self._reload()

    def _reload(self) -> None:
        """Load history rows and refresh table view.

        Returns:
            None.
        """
        self._rows = load_entries_newest_first()
        self._apply_filter()

    def _filtered_rows(self) -> list[HistoryRowView]:
        """Return history rows that match the active search text."""
        q = self._search.text().strip().lower()
        if not q:
            return self._rows
        return [
            row
            for row in self._rows
            if q in row.task_id.lower()
            or q in row.task_title.lower()
            or q in row.pack_name.lower()
            or q in row.status.lower()
            or q in row.error_text.lower()
            or q in row.result_text.lower()
        ]

    def _apply_filter(self) -> None:
        """Apply search filter and render visible table rows.

        Returns:
            None.
        """
        filtered = self._filtered_rows()
        self._visible_rows = filtered
        self._table.setRowCount(0)
        for r in filtered:
            self._append_row(r)
        self._count_lbl.setText(
            COUNT_LABEL_TEMPLATE_DINAMIC_POSTFIX_P101.format(
                count=len(filtered)
            )
        )

    def _append_row(self, row_data: HistoryRowView) -> None:
        """Append one row to history table.

        Args:
            row_data: History row data.

        Returns:
            None.
        """
        row = self._table.rowCount()
        self._table.insertRow(row)
        when_item = QTableWidgetItem(self._normalize_timestamp(row_data.ts))
        when_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._table.setItem(
            row,
            TABLE_COL_TIMESTAMP,
            when_item,
        )
        self._table.setItem(
            row, TABLE_COL_TASK, self._build_task_item(row_data)
        )
        self._table.setItem(
            row, TABLE_COL_RESULT, self._build_status_item(row_data)
        )
        self._table.setCellWidget(
            row, TABLE_COL_ACTIONS, self._build_actions_widget(row_data)
        )

    def _build_task_item(self, row_data: HistoryRowView) -> QTableWidgetItem:
        """Build table item for task column.

        Args:
            row_data: History row data.

        Returns:
            Configured task table item.
        """
        task_item = QTableWidgetItem(task_cell_text(row_data))
        task_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        task_item.setToolTip(
            TASK_TOOLTIP_TEMPLATE_DINAMIC_POSTFIX_P101.format(
                title=row_data.task_title,
                task_id=row_data.task_id,
                pack=pack_label(row_data.pack_name),
            )
        )
        return task_item

    def _build_status_item(self, row_data: HistoryRowView) -> QTableWidgetItem:
        """Build table item for status column.

        Args:
            row_data: History row data.

        Returns:
            Configured status table item.
        """
        mark = (
            SUCCESS_MARK_DINAMIC_POSTFIX_P101
            if row_data.passed
            else FAIL_MARK_DINAMIC_POSTFIX_P101
        )
        color = (
            SUCCESS_COLOR_DINAMIC_POSTFIX_P101
            if row_data.passed
            else FAIL_COLOR_DINAMIC_POSTFIX_P101
        )
        item = QTableWidgetItem(mark)
        item.setForeground(QColor(color))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _on_table_cell_clicked(self, row_index: int, column: int) -> None:
        """Open row-details modal when a non-actions cell is clicked."""
        if column == TABLE_COL_ACTIONS:
            return
        if row_index < 0 or row_index >= self._table.rowCount():
            return
        if row_index >= len(self._visible_rows):
            return
        matched = self._visible_rows[row_index]
        HistoryEntryDetailsDialog(
            self,
            row=matched,
            normalized_ts=self._normalize_timestamp(matched.ts),
        ).exec()

    def _build_actions_widget(self, row_data: HistoryRowView) -> QWidget:
        """Build actions cell widget with report/code buttons.

        Args:
            row_data: History row data.

        Returns:
            Widget containing row action buttons.
        """
        wrap = QWidget()
        layout = QHBoxLayout(wrap)
        layout.setContentsMargins(
            ACTIONS_LAYOUT_PADDING,
            SMALL_VERTICAL_MARGIN,
            ACTIONS_LAYOUT_PADDING,
            SMALL_VERTICAL_MARGIN,
        )
        layout.setSpacing(ACTIONS_LAYOUT_SPACING)
        report_button = self._create_icon_button(
            icon=icons.icon_file_text(),
            tooltip=REPORT_BUTTON_TOOLTIP_DINAMIC_POSTFIX_P101,
            callback=partial(self._show_report, row_data),
        )
        code_button = self._create_icon_button(
            icon=icons.icon_code(),
            tooltip=CODE_BUTTON_TOOLTIP_DINAMIC_POSTFIX_P101,
            callback=partial(self._show_code, row_data),
        )
        export_button = QPushButton(ROW_EXPORT_TEXT)
        export_button.setObjectName(
            OBJECT_NAME_TABLE_ICON_BUTTON_DINAMIC_POSTFIX_P101
        )
        export_button.setToolTip(HISTORY_EXPORT_TOOLTIP_DINAMIC_POSTFIX_P101)
        export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        export_button.clicked.connect(partial(self._export_row, row_data))
        layout.addWidget(report_button)
        layout.addWidget(code_button)
        layout.addWidget(export_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return wrap

    def _create_icon_button(
        self, *, icon: QIcon, tooltip: str, callback: Callable[[], None]
    ) -> QPushButton:
        """Create standardized icon action button.

        Args:
            icon: Qt icon object.
            tooltip: Tooltip text.
            callback: Click callback.

        Returns:
            Configured push button.
        """
        button = QPushButton()
        button.setObjectName(
            OBJECT_NAME_TABLE_ICON_BUTTON_DINAMIC_POSTFIX_P101
        )
        button.setFixedSize(ACTION_BUTTON_SIZE, ACTION_BUTTON_SIZE)
        button.setIcon(icon)
        button.setIconSize(QSize(ACTION_ICON_SIZE, ACTION_ICON_SIZE))
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(callback)
        return button

    def _show_report(self, row: HistoryRowView) -> None:
        """Open report detail dialog.

        Args:
            row: Selected history row.

        Returns:
            None.
        """
        text = row.result_text if row.passed else row.error_text
        if row.passed and not text.strip():
            text = SUCCESS_REPORT_TEXT_DINAMIC_POSTFIX_P101
        if (not row.passed) and row.result_text:
            text = REPORT_ACTUAL_TEMPLATE_DINAMIC_POSTFIX_P101.format(
                text=text or EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
                actual_preview=row.result_text,
            )
        DetailTextDialog(
            self,
            window_title=REPORT_WINDOW_TITLE_DINAMIC_POSTFIX_P101,
            body=text or EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
            is_code=False,
        ).exec()

    def _normalize_export_path(self, path_text: str) -> Path:
        """Return export path with ``.py`` suffix."""
        path = Path(path_text)
        if path.suffix.lower() == PY_FILE_SUFFIX:
            return path
        return path.with_suffix(PY_FILE_SUFFIX)

    def _export_row(self, row: HistoryRowView) -> None:
        """Export a single history row into a chosen Python file."""
        suggested = str(Path.cwd() / default_history_export_filename(row))
        path_text, _selected_filter = QFileDialog.getSaveFileName(
            self,
            HISTORY_EXPORT_DIALOG_TITLE_DINAMIC_POSTFIX_P101,
            suggested,
            HISTORY_EXPORT_FILE_FILTER_DINAMIC_POSTFIX_P101,
        )
        if not path_text:
            return
        target = self._normalize_export_path(path_text)
        try:
            export_history_entry_to_python(row, target)
        except OSError as exc:
            QMessageBox.critical(
                self,
                WINDOW_TITLE_DINAMIC_POSTFIX_P101,
                str(exc),
            )
            return
        QMessageBox.information(
            self,
            WINDOW_TITLE_DINAMIC_POSTFIX_P101,
            HISTORY_EXPORT_DONE_MESSAGE_DINAMIC_POSTFIX_P101.format(
                path=str(target)
            ),
        )

    def _export_all_rows(self) -> None:
        """Export all history rows into a selected directory."""
        if not self._rows:
            QMessageBox.information(
                self,
                WINDOW_TITLE_DINAMIC_POSTFIX_P101,
                HISTORY_EXPORT_EMPTY_MESSAGE_DINAMIC_POSTFIX_P101,
            )
            return
        folder = QFileDialog.getExistingDirectory(
            self,
            HISTORY_EXPORT_DIR_DIALOG_TITLE_DINAMIC_POSTFIX_P101,
            str(Path.cwd()),
        )
        if not folder:
            return
        target_dir = Path(folder)
        try:
            written = export_history_rows_to_python(self._rows, target_dir)
        except OSError as exc:
            QMessageBox.critical(
                self,
                WINDOW_TITLE_DINAMIC_POSTFIX_P101,
                str(exc),
            )
            return
        QMessageBox.information(
            self,
            WINDOW_TITLE_DINAMIC_POSTFIX_P101,
            HISTORY_EXPORT_ALL_DONE_MESSAGE_DINAMIC_POSTFIX_P101.format(
                count=len(written),
                path=str(target_dir),
            ),
        )

    def _show_code(self, row: HistoryRowView) -> None:
        """Open code detail dialog.

        Args:
            row: Selected history row.

        Returns:
            None.
        """
        body = row.code[:CODE_PREVIEW_LIMIT]
        if len(row.code) > CODE_PREVIEW_LIMIT:
            body += CODE_TRUNCATION_SUFFIX_DINAMIC_POSTFIX_P101
        DetailTextDialog(
            self,
            window_title=CODE_WINDOW_TITLE_DINAMIC_POSTFIX_P101,
            body=body or EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
            is_code=True,
        ).exec()

    def _on_clear(self) -> None:
        """Handle clear-history action with confirmation.

        Returns:
            None.
        """
        reply = QMessageBox.question(
            self,
            CLEAR_HISTORY_DIALOG_TITLE_DINAMIC_POSTFIX_P101,
            CLEAR_HISTORY_DIALOG_TEXT_DINAMIC_POSTFIX_P101,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            clear_history_file()
            self._reload()


class HistoryEntryDetailsDialog(QDialog):
    """Structured modal dialog for one history entry."""

    def __init__(
        self,
        parent: QWidget,
        *,
        row: HistoryRowView,
        normalized_ts: str,
    ) -> None:
        super().__init__(parent)
        self._highlighters: list[PythonHighlighter] = []
        self.setWindowTitle(HISTORY_ROW_DETAILS_TITLE_DINAMIC_POSTFIX_P101)
        self.setModal(True)
        self.resize(DETAIL_DIALOG_WIDTH, DETAIL_DIALOG_HEIGHT)
        self.setMinimumSize(DETAIL_MIN_DIALOG_WIDTH, DETAIL_MIN_DIALOG_HEIGHT)
        self.setObjectName(DETAIL_DIALOG_OBJECT_NAME)
        self.setStyleSheet(DETAIL_STYLE_SHEET)
        root = QVBoxLayout(self)
        root.setContentsMargins(
            DETAIL_ROOT_MARGIN_LEFT,
            DETAIL_ROOT_MARGIN_TOP,
            DETAIL_ROOT_MARGIN_RIGHT,
            DETAIL_ROOT_MARGIN_BOTTOM,
        )
        root.setSpacing(DETAIL_ROOT_SPACING)
        meta = self._build_meta_card(row=row, normalized_ts=normalized_ts)
        root.addWidget(meta)
        sections_grid = QGridLayout()
        sections_grid.setSpacing(12)
        sections_grid.addWidget(
            self._section(
                INPUT_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
                row.input_data or EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
                highlight_python=True,
            ),
            0,
            0,
        )
        sections_grid.addWidget(
            self._section(
                OUTPUT_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
                row.expected_result
                or EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
                highlight_python=True,
            ),
            0,
            1,
        )
        sections_grid.addWidget(
            self._section(
                HISTORY_TABLE_RESULT_DINAMIC_POSTFIX_P101,
                row.result_text or EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
                highlight_python=True,
            ),
            1,
            0,
        )
        sections_grid.addWidget(
            self._section(
                HISTORY_DETAILS_SECTION_ERROR_DINAMIC_POSTFIX_P101,
                row.error_text or EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
            ),
            1,
            1,
        )
        root.addLayout(sections_grid, 1)
        root.addWidget(
            self._section(
                HISTORY_DETAILS_SECTION_CODE_DINAMIC_POSTFIX_P101,
                row.code or EMPTY_CONTENT_FALLBACK_DINAMIC_POSTFIX_P101,
                is_code=True,
                highlight_python=True,
            )
        )

    def _build_meta_card(
        self, *, row: HistoryRowView, normalized_ts: str
    ) -> QFrame:
        """Build compact key/value metadata card."""
        card = QFrame()
        card.setObjectName(DETAIL_META_CARD_OBJECT_NAME)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(
            DETAIL_CARD_MARGIN_LEFT,
            DETAIL_CARD_MARGIN_TOP,
            DETAIL_CARD_MARGIN_RIGHT,
            DETAIL_CARD_MARGIN_BOTTOM,
        )
        layout.setSpacing(DETAIL_CARD_SPACING)
        title = QLabel(row.task_title or row.task_id)
        title.setObjectName(DETAIL_META_TITLE_OBJECT_NAME)
        title.setWordWrap(True)
        title.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        title.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        chips_row = QWidget()
        grid = QHBoxLayout(chips_row)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        status_text = self._localized_status(row)
        for key, value in (
            (HISTORY_DETAILS_LABEL_ID_DINAMIC_POSTFIX_P101, row.task_id),
            (HISTORY_DETAILS_LABEL_WHEN_DINAMIC_POSTFIX_P101, normalized_ts),
            (
                HISTORY_DETAILS_LABEL_PACK_DINAMIC_POSTFIX_P101,
                pack_label(row.pack_name),
            ),
            (HISTORY_DETAILS_LABEL_STATUS_DINAMIC_POSTFIX_P101, status_text),
            (
                HISTORY_DETAILS_LABEL_DURATION_DINAMIC_POSTFIX_P101,
                f"{row.duration_sec:.2f}s",
            ),
        ):
            chip = QFrame()
            chip.setObjectName(DETAIL_META_BLOCK_OBJECT_NAME)
            block = QVBoxLayout(chip)
            block.setContentsMargins(
                DETAIL_META_BLOCK_MARGIN_LEFT,
                DETAIL_META_BLOCK_MARGIN_TOP,
                DETAIL_META_BLOCK_MARGIN_RIGHT,
                DETAIL_META_BLOCK_MARGIN_BOTTOM,
            )
            block.setSpacing(DETAIL_META_BLOCK_SPACING)
            k = QLabel(key)
            k.setObjectName(DETAIL_META_KEY_OBJECT_NAME)
            k.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            v = QLabel(value)
            v.setObjectName(DETAIL_META_VALUE_OBJECT_NAME)
            v.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            v.setWordWrap(True)
            block.addWidget(k)
            block.addWidget(v)
            grid.addWidget(chip, 0)
        layout.addWidget(title, stretch=1)
        layout.addWidget(
            chips_row,
            stretch=0,
            alignment=Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter,
        )
        return card

    def _localized_status(self, row: HistoryRowView) -> str:
        """Return translated status text for details header."""
        if row.passed:
            return (
                f"{SUCCESS_MARK_DINAMIC_POSTFIX_P101} "
                f"{HISTORY_DETAILS_STATUS_PASSED_DINAMIC_POSTFIX_P101}"
            )
        return (
            f"{FAIL_MARK_DINAMIC_POSTFIX_P101} "
            f"{HISTORY_DETAILS_STATUS_FAILED_DINAMIC_POSTFIX_P101}"
        )

    def _section(
        self,
        title: str,
        body: str,
        *,
        is_code: bool = False,
        highlight_python: bool = False,
    ) -> QWidget:
        """Build one titled readonly text section."""
        wrap = QFrame()
        wrap.setObjectName(DETAIL_SECTION_OBJECT_NAME)
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(
            DETAIL_META_BLOCK_MARGIN_LEFT,
            DETAIL_META_BLOCK_MARGIN_TOP,
            DETAIL_META_BLOCK_MARGIN_RIGHT,
            DETAIL_META_BLOCK_MARGIN_BOTTOM,
        )
        layout.setSpacing(DETAIL_FIELD_GAP)
        title_label = QLabel(title)
        title_label.setObjectName(DETAIL_SECTION_TITLE_OBJECT_NAME)
        layout.addWidget(title_label)
        viewer = QPlainTextEdit()
        viewer.setObjectName(DETAIL_BODY_OBJECT_NAME)
        viewer.setReadOnly(True)
        viewer.setPlainText(body)
        if highlight_python:
            font = QFont()
            font.setFamilies(list(DETAIL_MONO_FONT_FAMILIES))
            font.setStyleHint(QFont.StyleHint.Monospace)
            font.setPointSize(DETAIL_MONO_FONT_SIZE)
            viewer.setFont(font)
            self._highlighters.append(
                PythonHighlighter(viewer.document(), dark=False)
            )
        if is_code:
            viewer.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
            viewer.setMinimumHeight(DETAIL_CODE_MIN_HEIGHT)
        else:
            viewer.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            viewer.setMinimumHeight(DETAIL_BODY_MIN_HEIGHT)
        layout.addWidget(viewer)
        return wrap
