"""
This module builds the main windows Qt user interface for a
task-checking application, including the header, task sidebar, central
code editor, and right-hand history/settings panels.

It works as a mixin (MainWindowUiMixin) that assumes a host object
implementing MainWindowUiHost, then programmatically constructs
layouts, widgets, and signal connections that wire UI controls to
session and configuration callbacks.

It defines many layout and sizing constants (margins, spacings, fixed
widths, ranges) plus type aliases for margins and click handlers, which
are reused across helpers like _make_vbox_layout, _make_hbox_layout,
_configure_vertical_scroll_area, and _set_size_policy_ignored_preferred.

Header-related methods (_build_light_header, _build_header_title_block,
_build_timer_pill, _append_header_session_toolbar,
_make_header_action_button, _update_header_session_controls) assemble
the logo/title area, a timer pill, and start/stop/check buttons with
icons and connect them to host callbacks.

Left-side task UI methods (_build_status_banner,
_build_task_text_section, _make_mono_preview, _build_mono_section,
_build_constraints_section, _build_task_aside) construct the task
sidebar showing title, description, input/output previews with syntax
highlighting, constraints text, and a status banner.

The central column builder (_build_center_column) creates the code
editor shell using a CodeEditor instance configured with font size and
theme, adds a placeholder, enforces minimum height, and includes a
check-result label below the editor.

Right-side methods (_build_right_tab_strip, _build_right_aside,
_set_right_tab)  create a tab strip with icons for history and settings,
manage a QStackedWidget for switching between pages, and trigger history
reload when the history tab is activated.

Settings-page builders (_build_settings_page,
_build_time_settings_block, _build_check_settings_block,
_build_ui_settings_block, _make_collapsible, _make_default_form_layout)
construct collapsible blocks for time, check, and UI options, populate
sliders and spin boxes with appropriate ranges, and connect controls
like the duration slider and “save settings” button to host callbacks.

History-page helpers (_build_history_page, _clear_history_list,
_build_open_history_button, _build_empty_history_label,
_history_mark_style, _build_history_card, _reload_history_tab) manage a
lightweight sidebar history view by loading recent entries, rendering
compact cards with pass/fail marks and meta information, and providing a
button to open the full history dialog.

Utility methods like _section_header, _collapsible_title,
_make_no_wrap_label, and _on_duration_slider encapsulate small pieces
of UI behavior such as building labeled section headers with accent
bars, toggling collapsible titles, disabling word wrap, and formatting
the current per-task duration text.
"""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QObject, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from typing import TYPE_CHECKING, Final, Protocol, cast

from core.check_history import HistoryRowView, load_entries_newest_first
from core.config import AppDefaults
from messages import (
    ACCENT_BAR_MUTED_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    ACCENT_BAR_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    APP_SUBTITLE_DINAMIC_POSTFIX_ME8C,
    APP_SUBTITLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    APP_TITLE_DINAMIC_POSTFIX_ME8C,
    APP_TITLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    APPLY_BUTTON_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    AUTOCHECK_TEXT_DINAMIC_POSTFIX_ME8C,
    AUTOCHECK_TOOLTIP_DINAMIC_POSTFIX_ME8C,
    CENTER_COLUMN_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    CHECK_BOX_TITLE_DINAMIC_POSTFIX_ME8C,
    CHECK_LIGHT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    CHECK_STATUS_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    CHECK_TIMEOUT_LABEL_DINAMIC_POSTFIX_ME8C,
    CHECK_TIMEOUT_TOOLTIP_DINAMIC_POSTFIX_ME8C,
    COLLAPSED_PREFIX_DINAMIC_POSTFIX_ME8C,
    COLLAPSIBLE_BODY_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    COLLAPSIBLE_HEAD_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    COLLAPSIBLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    CONSTRAINTS_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    CONSTRAINTS_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
    DURATION_DEFAULT_TEXT_DINAMIC_POSTFIX_ME8C,
    DURATION_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    DURATION_SLIDER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    DURATION_VALUE_TEMPLATE_DINAMIC_POSTFIX_ME8C,
    EDITOR_PAD_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    EDITOR_PLACEHOLDER_DINAMIC_POSTFIX_ME8C,
    EDITOR_SHELL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    EMPTY_LABEL_TEXT_DINAMIC_POSTFIX_ME8C,
    EXPANDED_PREFIX_DINAMIC_POSTFIX_ME8C,
    FONT_SIZE_LABEL_DINAMIC_POSTFIX_ME8C,
    HEADER_CHECK_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HEADER_CHECK_TEXT_DINAMIC_POSTFIX_ME8C,
    HEADER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HEADER_START_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HEADER_START_TEXT_DINAMIC_POSTFIX_ME8C,
    HEADER_STOP_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HEADER_STOP_TEXT_DINAMIC_POSTFIX_ME8C,
    HISTORY_BAD_MARK_DINAMIC_POSTFIX_ME8C,
    HISTORY_CARD_META_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HISTORY_CARD_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HISTORY_CARD_TITLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HISTORY_EMPTY_HINT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HISTORY_EMPTY_TEXT_DINAMIC_POSTFIX_ME8C,
    HISTORY_INNER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HISTORY_LINK_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    HISTORY_MARK_STYLE_BAD_DINAMIC_POSTFIX_ME8C,
    HISTORY_MARK_STYLE_OK_DINAMIC_POSTFIX_ME8C,
    HISTORY_META_TEMPLATE_DINAMIC_POSTFIX_ME8C,
    HISTORY_OK_MARK_DINAMIC_POSTFIX_ME8C,
    HISTORY_SCROLL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    ICON_WHITE_DINAMIC_POSTFIX_ME8C,
    INPUT_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
    LABEL_UI_LANGUAGE_DINAMIC_POSTFIX_K7WQ,
    LOGO_BADGE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    LOGO_TEXT_DINAMIC_POSTFIX_ME8C,
    MONO_BLOCK_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    OPEN_FULL_HISTORY_TEXT_DINAMIC_POSTFIX_ME8C,
    OPTION_UI_LANGUAGE_EN_DINAMIC_POSTFIX_K7WQ,
    OPTION_UI_LANGUAGE_RU_DINAMIC_POSTFIX_K7WQ,
    OUTPUT_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
    PARAM_SPIN_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    RIGHT_ASIDE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    RIGHT_DIVIDER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    RIGHT_SETTINGS_SCROLL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    RIGHT_TAB_HISTORY_TEXT_DINAMIC_POSTFIX_ME8C,
    RIGHT_TAB_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    RIGHT_TAB_SETTINGS_TEXT_DINAMIC_POSTFIX_ME8C,
    RIGHT_TAB_STRIP_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    SAVE_SETTINGS_TEXT_DINAMIC_POSTFIX_ME8C,
    SECTION_TITLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    SETTINGS_FIELD_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    SETTINGS_INNER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    SETTINGS_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    STATUS_BANNER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    STATUS_BANNER_TEXT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    STRICT_TYPES_TEXT_DINAMIC_POSTFIX_ME8C,
    TAB_ICON_STROKE_DINAMIC_POSTFIX_ME8C,
    TASK_ASIDE_INNER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    TASK_ASIDE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    TASK_BODY_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    TASK_DURATION_LABEL_DINAMIC_POSTFIX_ME8C,
    TASK_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
    TASK_TITLE_STYLE_DINAMIC_POSTFIX_ME8C,
    TIME_BOX_TITLE_DINAMIC_POSTFIX_ME8C,
    TIMER_ICON_STROKE_DINAMIC_POSTFIX_ME8C,
    TIMER_INITIAL_TEXT_DINAMIC_POSTFIX_ME8C,
    TIMER_PILL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    TIMER_PILL_TEXT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
    UI_BOX_TITLE_DINAMIC_POSTFIX_ME8C,
)
from ui import icons
from ui.editor import CodeEditor, PythonHighlighter

from .helpers import mono_font, pack_label

type Margins = tuple[int, int, int, int]
type ClickHandler = Callable[[], None]
HEADER_MARGINS: Final[Margins] = (24, 16, 24, 16)
HEADER_LEFT_SPACING: Final[int] = 12
HEADER_TITLE_SPACING: Final[int] = 4
HEADER_SPACING: Final[int] = 0
TIMER_PILL_MARGINS: Final[Margins] = (10, 4, 12, 4)
TIMER_PILL_SPACING: Final[int] = 8
TIMER_ICON_SIZE: Final[int] = 16
SPACING_AFTER_TIMER: Final[int] = 12
BUTTON_GROUP_SPACING: Final[int] = 8
CHECK_ICON_SIZE: Final[int] = 16
STOP_ICON_SIZE: Final[int] = 14
START_ICON_SIZE: Final[int] = 16
SECTION_HEADER_SPACING: Final[int] = 8
DEFAULT_SECTION_SPACING: Final[int] = 10
TASK_ASIDE_WIDTH: Final[int] = 410
TASK_ASIDE_MARGINS: Final[Margins] = (24, 24, 24, 24)
TASK_ASIDE_SPACING: Final[int] = 20
STATUS_BANNER_MARGINS: Final[Margins] = (12, 10, 12, 10)
MONO_BLOCK_MAX_HEIGHT: Final[int] = 160
MONO_BLOCK_FONT_SIZE: Final[int] = 11
EDITOR_PAD_MARGINS: Final[Margins] = (24, 24, 24, 12)
EDITOR_MIN_HEIGHT: Final[int] = 240
RIGHT_ASIDE_WIDTH: Final[int] = 300
RIGHT_DIVIDER_HEIGHT: Final[int] = 1
RIGHT_STACK_HISTORY_INDEX: Final[int] = 0
RIGHT_STACK_SETTINGS_INDEX: Final[int] = 1
HISTORY_ICON_SIZE: Final[int] = 16
SETTINGS_ICON_SIZE: Final[int] = 16
SETTINGS_MARGINS: Final[Margins] = (16, 22, 16, 16)
SETTINGS_SPACING: Final[int] = 14
DURATION_MIN: Final[int] = 1
DURATION_MAX: Final[int] = 30
FORM_SPACING_H: Final[int] = 12
FORM_SPACING_V: Final[int] = 10
FORM_MARGINS: Final[Margins] = (0, 0, 0, 0)
CHECK_TIMEOUT_MIN: Final[int] = 1
CHECK_TIMEOUT_MAX: Final[int] = 10
PARAM_SPIN_WIDTH: Final[int] = 88
FONT_SIZE_MIN: Final[int] = 10
FONT_SIZE_MAX: Final[int] = 18
COLLAPSIBLE_SPACING: Final[int] = 8
COLLAPSIBLE_BODY_MARGINS: Final[Margins] = (10, 12, 10, 10)
COLLAPSIBLE_BODY_SPACING: Final[int] = 12
HISTORY_LAYOUT_MARGINS: Final[Margins] = (16, 16, 16, 16)
HISTORY_LAYOUT_SPACING: Final[int] = 10
HISTORY_CARD_MARGINS: Final[Margins] = (12, 10, 12, 10)
HISTORY_MAX_ENTRIES: Final[int] = 25
HISTORY_TASK_TITLE_MAX: Final[int] = 48
LAYOUT_SPACING_NONE: Final[int] = 0
UI_LANGUAGE_TAG_EN: Final[str] = "en"
UI_LANGUAGE_TAG_RU: Final[str] = "ru"


class MainWindowUiHost(Protocol):
    """
    Required attributes and callbacks for :class:`MainWindowUiMixin`.
    """

    _session_active: bool
    _defaults: AppDefaults
    _history_list_layout: QVBoxLayout
    _right_stack: QStackedWidget
    _tab_history: QPushButton
    _tab_settings: QPushButton
    _lbl_duration_val: QLabel

    def _verify_clicked(self) -> None:
        """Run verification for the active task."""
        ...

    def _stop_clicked(self) -> None:
        """End the current session."""
        ...

    def _start_clicked(self) -> None:
        """Begin a new session."""
        ...

    def _apply_clicked(self) -> None:
        """Persist settings from the right pane."""
        ...

    def _open_history(self) -> None:
        """Show the full check history dialog."""
        ...

    def _update_verify_enabled(self) -> None:
        """Refresh whether the verify control may be used."""
        ...


class MainWindowUiMixin(MainWindowUiHost if TYPE_CHECKING else object):
    """Build main window header, sidebars, and editor area."""

    def _make_vbox_layout(
        self, widget: QWidget, *, margins: Margins, spacing: int
    ) -> QVBoxLayout:
        """Create a configured vertical layout for a widget.

        Args:
            widget: Parent widget for the layout.
            margins: Contents margins in Qt order.
            spacing: Spacing between child items.

        Returns:
            Configured vertical layout.
        """
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        return layout

    def _make_hbox_layout(
        self, widget: QWidget, *, margins: Margins, spacing: int
    ) -> QHBoxLayout:
        """Create a configured horizontal layout for a widget.

        Args:
            widget: Parent widget for the layout.
            margins: Contents margins in Qt order.
            spacing: Spacing between child items.

        Returns:
            Configured horizontal layout.
        """
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        return layout

    def _set_size_policy_ignored_preferred(self, widget: QWidget) -> None:
        """Set horizontal Ignored and vertical Preferred size policy.

        Args:
            widget: Target widget (typical scroll inner content).
        """
        widget.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )

    def _configure_vertical_scroll_area(
        self, scroll: QScrollArea, *, object_name: str | None = None
    ) -> None:
        """Apply shared configuration for vertical-only scroll areas.

        Args:
            scroll: Scroll area to configure.
            object_name: Optional Qt object name.
        """
        if object_name is not None:
            scroll.setObjectName(object_name)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding
        )

    def _collapsible_title(self, title: str, *, is_open: bool) -> str:
        """Build collapsible section title with state prefix.

        Args:
            title: Section title text.
            is_open: Whether the body is currently visible.

        Returns:
            Button label with disclosure prefix.
        """
        prefix = (
            EXPANDED_PREFIX_DINAMIC_POSTFIX_ME8C
            if is_open
            else COLLAPSED_PREFIX_DINAMIC_POSTFIX_ME8C
        )
        return f"{prefix}{title}"

    def _make_header_action_button(
        self,
        *,
        text: str,
        object_name: str,
        icon_size: int,
        on_click: ClickHandler,
        icon: QIcon,
    ) -> QPushButton:
        """Create a header action button with icon and callback.

        Args:
            text: Button text.
            object_name: Qt object name.
            icon_size: Pixel size for icon.
            on_click: Bound click handler.
            icon: Prepared Qt icon.

        Returns:
            Configured push button.
        """
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setIcon(icon)
        button.setIconSize(QSize(icon_size, icon_size))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(on_click)
        return button

    def _append_header_session_toolbar(self, header: QHBoxLayout) -> None:
        """Add timer pill, verify/stop/start controls to the header row.

        Args:
            header: Main header horizontal layout.
        """
        self._timer_pill = self._build_timer_pill()
        header.addWidget(self._timer_pill, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addSpacing(SPACING_AFTER_TIMER)
        self._btn_header_check = self._make_header_action_button(
            text=HEADER_CHECK_TEXT_DINAMIC_POSTFIX_ME8C,
            object_name=HEADER_CHECK_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
            icon_size=CHECK_ICON_SIZE,
            on_click=self._verify_clicked,
            icon=icons.icon_check(
                stroke=ICON_WHITE_DINAMIC_POSTFIX_ME8C, size=CHECK_ICON_SIZE
            ),
        )
        self._btn_header_check.hide()
        header.addWidget(self._btn_header_check, 0)
        header.addSpacing(BUTTON_GROUP_SPACING)
        self._btn_header_stop = self._make_header_action_button(
            text=HEADER_STOP_TEXT_DINAMIC_POSTFIX_ME8C,
            object_name=HEADER_STOP_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
            icon_size=STOP_ICON_SIZE,
            on_click=self._stop_clicked,
            icon=icons.icon_square_filled(
                color=ICON_WHITE_DINAMIC_POSTFIX_ME8C, size=STOP_ICON_SIZE
            ),
        )
        self._btn_header_stop.hide()
        header.addWidget(self._btn_header_stop, 0)
        header.addSpacing(BUTTON_GROUP_SPACING)
        self._btn_start = self._make_header_action_button(
            text=HEADER_START_TEXT_DINAMIC_POSTFIX_ME8C,
            object_name=HEADER_START_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
            icon_size=START_ICON_SIZE,
            on_click=self._start_clicked,
            icon=icons.icon_play_filled(size=START_ICON_SIZE),
        )
        header.addWidget(self._btn_start, 0, Qt.AlignmentFlag.AlignVCenter)

    def _build_header_title_block(self) -> QWidget:
        """Build header left block with logo and title lines.

        Returns:
            Header title widget.
        """
        left = QHBoxLayout()
        left.setSpacing(HEADER_LEFT_SPACING)
        logo = QLabel(LOGO_TEXT_DINAMIC_POSTFIX_ME8C)
        logo.setObjectName(LOGO_BADGE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        titles = QVBoxLayout()
        titles.setSpacing(HEADER_TITLE_SPACING)
        titles.setContentsMargins(*FORM_MARGINS)
        title_label = self._make_no_wrap_label(
            APP_TITLE_DINAMIC_POSTFIX_ME8C,
            APP_TITLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
        )
        subtitle_label = self._make_no_wrap_label(
            APP_SUBTITLE_DINAMIC_POSTFIX_ME8C,
            APP_SUBTITLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
        )
        titles.addWidget(title_label, 0)
        titles.addWidget(subtitle_label, 0)
        left.addWidget(logo, 0, Qt.AlignmentFlag.AlignTop)
        left.addLayout(titles)
        container = QWidget()
        container.setLayout(left)
        return container

    def _make_no_wrap_label(self, text: str, object_name: str) -> QLabel:
        """Create a label configured with disabled word wrapping.

        Args:
            text: Label text.
            object_name: Qt object name.

        Returns:
            Configured label instance.
        """
        label = QLabel(text)
        label.setObjectName(object_name)
        label.setWordWrap(False)
        return label

    def _build_timer_pill(self) -> QFrame:
        """Build timer pill shown during active session.

        Returns:
            Configured timer pill frame.
        """
        timer_pill = QFrame()
        timer_pill.setObjectName(TIMER_PILL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        layout = self._make_hbox_layout(
            timer_pill, margins=TIMER_PILL_MARGINS, spacing=TIMER_PILL_SPACING
        )
        icon_label = QLabel()
        icon_label.setPixmap(
            icons.icon_clock(
                stroke=TIMER_ICON_STROKE_DINAMIC_POSTFIX_ME8C,
                size=TIMER_ICON_SIZE,
            ).pixmap(TIMER_ICON_SIZE, TIMER_ICON_SIZE)
        )
        self._lbl_timer = QLabel(TIMER_INITIAL_TEXT_DINAMIC_POSTFIX_ME8C)
        self._lbl_timer.setObjectName(
            TIMER_PILL_TEXT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        layout.addWidget(icon_label)
        layout.addWidget(self._lbl_timer)
        timer_pill.hide()
        return timer_pill

    def _make_mono_preview(self) -> tuple[QPlainTextEdit, PythonHighlighter]:
        """Create read-only mono text edit with highlighter.

        Returns:
            Pair of text edit and corresponding highlighter.
        """
        mono = QPlainTextEdit()
        mono.setObjectName(MONO_BLOCK_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        mono.setReadOnly(True)
        mono.setMaximumHeight(MONO_BLOCK_MAX_HEIGHT)
        mono.setFont(mono_font(MONO_BLOCK_FONT_SIZE))
        highlighter = PythonHighlighter(mono.document(), dark=False)
        return (mono, highlighter)

    def _make_default_form_layout(self) -> QFormLayout:
        """Build standard form layout used in settings blocks.

        Returns:
            Configured form layout.
        """
        form = QFormLayout()
        form.setHorizontalSpacing(FORM_SPACING_H)
        form.setVerticalSpacing(FORM_SPACING_V)
        form.setContentsMargins(*FORM_MARGINS)
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        return form

    def _build_light_header(self) -> QFrame:
        """Build top header with title, timer, and controls.

        Returns:
            Top header frame.
        """
        bar = QFrame()
        bar.setObjectName(HEADER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        h = self._make_hbox_layout(
            bar, margins=HEADER_MARGINS, spacing=HEADER_SPACING
        )
        h.addWidget(self._build_header_title_block(), 0)
        h.addStretch(1)
        self._append_header_session_toolbar(h)
        return bar

    def _update_header_session_controls(self) -> None:
        """Toggle header controls according to session state."""
        active = self._session_active
        self._btn_start.setVisible(not active)
        self._timer_pill.setVisible(active)
        self._btn_header_check.setVisible(active)
        self._btn_header_stop.setVisible(active)
        self._update_verify_enabled()

    def _section_header(
        self, title: str, *, muted_accent: bool = False
    ) -> QWidget:
        """Build section header widget with accent bar.

        Args:
            title: Header title text.
            muted_accent: Whether to use muted accent bar style.

        Returns:
            Header widget.
        """
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(*FORM_MARGINS)
        row.setSpacing(SECTION_HEADER_SPACING)
        bar = QLabel()
        bar.setObjectName(
            ACCENT_BAR_MUTED_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
            if muted_accent
            else ACCENT_BAR_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        lab = QLabel(title)
        lab.setObjectName(SECTION_TITLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        row.addWidget(bar, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(lab, 1, Qt.AlignmentFlag.AlignVCenter)
        return w

    def _build_status_banner(self) -> QFrame:
        """Build status banner widget for task sidebar.

        Returns:
            Status banner frame.
        """
        self._task_banner = QFrame()
        self._task_banner.setObjectName(
            STATUS_BANNER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._task_banner.hide()
        banner_layout = self._make_hbox_layout(
            self._task_banner,
            margins=STATUS_BANNER_MARGINS,
            spacing=LAYOUT_SPACING_NONE,
        )
        self._task_banner_text = QLabel()
        self._task_banner_text.setObjectName(
            STATUS_BANNER_TEXT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._task_banner_text.setWordWrap(True)
        self._task_banner_text.setMinimumWidth(0)
        self._task_banner_text.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        banner_layout.addWidget(self._task_banner_text, 1)
        return self._task_banner

    def _build_task_text_section(self) -> QFrame:
        """Build task text section with title and description.

        Returns:
            Task section frame.
        """
        self._fr_task_section = QFrame()
        self._fr_task_section.setFrameShape(QFrame.Shape.NoFrame)
        layout = self._make_vbox_layout(
            self._fr_task_section,
            margins=FORM_MARGINS,
            spacing=DEFAULT_SECTION_SPACING,
        )
        layout.addWidget(
            self._section_header(TASK_SECTION_TITLE_DINAMIC_POSTFIX_ME8C)
        )
        self._lbl_task_title = QLabel()
        self._lbl_task_title.setObjectName(
            TASK_BODY_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._lbl_task_title.setWordWrap(True)
        self._lbl_task_title.setStyleSheet(
            TASK_TITLE_STYLE_DINAMIC_POSTFIX_ME8C
        )
        layout.addWidget(self._lbl_task_title)
        self._lbl_task_desc = QLabel()
        self._lbl_task_desc.setObjectName(
            TASK_BODY_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._lbl_task_desc.setWordWrap(True)
        layout.addWidget(self._lbl_task_desc)
        return self._fr_task_section

    def _build_mono_section(
        self, *, title: str
    ) -> tuple[QFrame, QPlainTextEdit, PythonHighlighter]:
        """Build section with a monospaced preview block.

        Args:
            title: Section title text.

        Returns:
            Section frame, mono block, and highlighter.
        """
        section = QFrame()
        section.setFrameShape(QFrame.Shape.NoFrame)
        layout = self._make_vbox_layout(
            section, margins=FORM_MARGINS, spacing=DEFAULT_SECTION_SPACING
        )
        layout.addWidget(self._section_header(title))
        mono, highlighter = self._make_mono_preview()
        layout.addWidget(mono)
        return (section, mono, highlighter)

    def _build_constraints_section(self) -> QFrame:
        """Build constraints section for task sidebar.

        Returns:
            Constraints section frame.
        """
        self._fr_constraints_section = QFrame()
        self._fr_constraints_section.setFrameShape(QFrame.Shape.NoFrame)
        layout = self._make_vbox_layout(
            self._fr_constraints_section,
            margins=FORM_MARGINS,
            spacing=DEFAULT_SECTION_SPACING,
        )
        layout.addWidget(
            self._section_header(
                CONSTRAINTS_SECTION_TITLE_DINAMIC_POSTFIX_ME8C,
                muted_accent=True,
            )
        )
        self._lbl_constraints = QLabel()
        self._lbl_constraints.setObjectName(
            CONSTRAINTS_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._lbl_constraints.setWordWrap(True)
        layout.addWidget(self._lbl_constraints)
        return self._fr_constraints_section

    def _build_task_aside(self) -> QScrollArea:
        """Build left task sidebar with task details and constraints.

        Returns:
            Configured left sidebar scroll area.
        """
        scroll = QScrollArea()
        self._configure_vertical_scroll_area(
            scroll, object_name=TASK_ASIDE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        scroll.setFixedWidth(TASK_ASIDE_WIDTH)
        scroll.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        inner = QWidget()
        inner.setObjectName(TASK_ASIDE_INNER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        v = self._make_vbox_layout(
            inner, margins=TASK_ASIDE_MARGINS, spacing=TASK_ASIDE_SPACING
        )
        v.addWidget(self._build_status_banner())
        v.addWidget(self._build_task_text_section())
        self._fr_input_section, self._mono_input, self._mono_input_high = (
            self._build_mono_section(
                title=INPUT_SECTION_TITLE_DINAMIC_POSTFIX_ME8C
            )
        )
        v.addWidget(self._fr_input_section)
        self._fr_output_section, self._mono_output, self._mono_output_high = (
            self._build_mono_section(
                title=OUTPUT_SECTION_TITLE_DINAMIC_POSTFIX_ME8C
            )
        )
        v.addWidget(self._fr_output_section)
        v.addWidget(self._build_constraints_section())
        v.addStretch(1)
        scroll.setWidget(inner)
        self._task_aside_scroll = scroll
        return scroll

    def _build_center_column(self) -> QWidget:
        """Build central column with editor and check result label.

        Returns:
            Configured center column widget.
        """
        col = QWidget()
        col.setObjectName(CENTER_COLUMN_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        lay = self._make_vbox_layout(
            col, margins=FORM_MARGINS, spacing=LAYOUT_SPACING_NONE
        )
        pad = QWidget()
        pad.setObjectName(EDITOR_PAD_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        pv = self._make_vbox_layout(
            pad, margins=EDITOR_PAD_MARGINS, spacing=LAYOUT_SPACING_NONE
        )
        self._editor = CodeEditor(
            font_size=self._defaults.ui.font_size,
            line_numbers=True,
            light_theme=True,
        )
        self._editor.setPlaceholderText(
            EDITOR_PLACEHOLDER_DINAMIC_POSTFIX_ME8C
        )
        self._editor.setMinimumHeight(EDITOR_MIN_HEIGHT)
        self._editor.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._editor_shell = QFrame()
        self._editor_shell.setObjectName(
            EDITOR_SHELL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        shl = self._make_vbox_layout(
            self._editor_shell,
            margins=FORM_MARGINS,
            spacing=LAYOUT_SPACING_NONE,
        )
        shl.addWidget(self._editor)
        self._editor.installEventFilter(cast(QObject, self))
        pv.addWidget(self._editor_shell, 1)
        self._lbl_check = QLabel(EMPTY_LABEL_TEXT_DINAMIC_POSTFIX_ME8C)
        self._lbl_check.setObjectName(
            CHECK_STATUS_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._lbl_check.setWordWrap(True)
        self._lbl_check.setMinimumWidth(0)
        self._lbl_check.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        pv.addWidget(self._lbl_check)
        lay.addWidget(pad, 1)
        return col

    def _build_right_tab_strip(self) -> QFrame:
        """Build the history/settings tab strip for the right sidebar.

        Populates ``_tab_history`` and ``_tab_settings``.

        Returns:
            Frame containing both tab buttons in one row.
        """
        tab_strip = QFrame()
        tab_strip.setObjectName(
            RIGHT_TAB_STRIP_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        row = self._make_hbox_layout(
            tab_strip,
            margins=FORM_MARGINS,
            spacing=LAYOUT_SPACING_NONE,
        )
        self._tab_history = QPushButton(
            RIGHT_TAB_HISTORY_TEXT_DINAMIC_POSTFIX_ME8C
        )
        self._tab_history.setObjectName(
            RIGHT_TAB_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._tab_history.setCheckable(True)
        self._tab_history.setIcon(
            icons.icon_clipboard_list(
                stroke=TAB_ICON_STROKE_DINAMIC_POSTFIX_ME8C,
                size=HISTORY_ICON_SIZE,
            )
        )
        self._tab_history.setIconSize(
            QSize(HISTORY_ICON_SIZE, HISTORY_ICON_SIZE)
        )
        self._tab_history.clicked.connect(
            lambda: self._set_right_tab(RIGHT_STACK_HISTORY_INDEX)
        )
        self._tab_settings = QPushButton(
            RIGHT_TAB_SETTINGS_TEXT_DINAMIC_POSTFIX_ME8C
        )
        self._tab_settings.setObjectName(
            RIGHT_TAB_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._tab_settings.setCheckable(True)
        self._tab_settings.setIcon(
            icons.icon_settings(
                stroke=TAB_ICON_STROKE_DINAMIC_POSTFIX_ME8C,
                size=SETTINGS_ICON_SIZE,
            )
        )
        self._tab_settings.setIconSize(
            QSize(SETTINGS_ICON_SIZE, SETTINGS_ICON_SIZE)
        )
        self._tab_settings.clicked.connect(
            lambda: self._set_right_tab(RIGHT_STACK_SETTINGS_INDEX)
        )
        row.addWidget(self._tab_history, 1)
        row.addWidget(self._tab_settings, 1)
        return tab_strip

    def _build_right_aside(self) -> QWidget:
        """Build right pane with history and settings tabs.

        Returns:
            Configured right sidebar widget.
        """
        wrap = QFrame()
        wrap.setObjectName(RIGHT_ASIDE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        wrap.setFixedWidth(RIGHT_ASIDE_WIDTH)
        outer = self._make_vbox_layout(
            wrap, margins=FORM_MARGINS, spacing=LAYOUT_SPACING_NONE
        )
        outer.addWidget(self._build_right_tab_strip())
        div = QFrame()
        div.setObjectName(RIGHT_DIVIDER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        div.setFixedHeight(RIGHT_DIVIDER_HEIGHT)
        outer.addWidget(div)
        self._right_stack = QStackedWidget()
        self._right_stack.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding
        )
        self._right_stack.addWidget(self._build_history_page())
        self._right_stack.addWidget(self._build_settings_page())
        outer.addWidget(self._right_stack, 1)
        self._set_right_tab(RIGHT_STACK_HISTORY_INDEX)
        return wrap

    def _set_right_tab(self, index: int) -> None:
        """Set active right pane tab by index.

        Args:
            index: Tab index for history/settings stack.
        """
        self._tab_history.setChecked(index == RIGHT_STACK_HISTORY_INDEX)
        self._tab_settings.setChecked(index == RIGHT_STACK_SETTINGS_INDEX)
        self._right_stack.setCurrentIndex(index)
        if index == RIGHT_STACK_HISTORY_INDEX:
            self._reload_history_tab()

    def _build_settings_page(self) -> QWidget:
        """Build settings page with collapsible groups.

        Returns:
            Settings page widget.
        """
        scroll = QScrollArea()
        self._configure_vertical_scroll_area(
            scroll,
            object_name=RIGHT_SETTINGS_SCROLL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C,
        )
        inner = QWidget()
        inner.setObjectName(SETTINGS_INNER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        inner.setMinimumWidth(0)
        self._set_size_policy_ignored_preferred(inner)
        self._settings_inner = inner
        v = self._make_vbox_layout(
            inner, margins=SETTINGS_MARGINS, spacing=SETTINGS_SPACING
        )
        self._build_time_settings_block(v)
        self._build_check_settings_block(v)
        self._build_ui_settings_block(v)
        v.addSpacing(COLLAPSIBLE_SPACING)
        self._btn_apply = QPushButton(SAVE_SETTINGS_TEXT_DINAMIC_POSTFIX_ME8C)
        self._btn_apply.setObjectName(
            APPLY_BUTTON_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_apply.clicked.connect(self._apply_clicked)
        v.addWidget(self._btn_apply)
        v.addStretch(1)
        scroll.setWidget(inner)
        return scroll

    def _build_time_settings_block(self, parent_layout: QVBoxLayout) -> None:
        """Append time settings group.

        Args:
            parent_layout: Target parent layout.
        """
        time_box, time_body = self._make_collapsible(
            TIME_BOX_TITLE_DINAMIC_POSTFIX_ME8C, collapsed=True
        )
        duration_label = QLabel(TASK_DURATION_LABEL_DINAMIC_POSTFIX_ME8C)
        duration_label.setObjectName(
            SETTINGS_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        time_body.addWidget(duration_label)
        row_layout = QHBoxLayout()
        self._slider_duration = QSlider(Qt.Orientation.Horizontal)
        self._slider_duration.setObjectName(
            DURATION_SLIDER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._slider_duration.setRange(DURATION_MIN, DURATION_MAX)
        self._slider_duration.valueChanged.connect(self._on_duration_slider)
        self._lbl_duration_val = QLabel(
            DURATION_DEFAULT_TEXT_DINAMIC_POSTFIX_ME8C
        )
        self._lbl_duration_val.setObjectName(
            DURATION_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        row_layout.addWidget(self._slider_duration, 1)
        row_layout.addWidget(self._lbl_duration_val, 0)
        time_body.addLayout(row_layout)
        parent_layout.addWidget(time_box)

    def _build_check_settings_block(self, parent_layout: QVBoxLayout) -> None:
        """Append check settings group.

        Args:
            parent_layout: Target parent layout.
        """
        chk_box, chk_body = self._make_collapsible(
            CHECK_BOX_TITLE_DINAMIC_POSTFIX_ME8C, collapsed=True
        )
        self._chk_autocheck = QCheckBox(AUTOCHECK_TEXT_DINAMIC_POSTFIX_ME8C)
        self._chk_autocheck.setObjectName(
            CHECK_LIGHT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._chk_autocheck.setToolTip(AUTOCHECK_TOOLTIP_DINAMIC_POSTFIX_ME8C)
        chk_body.addWidget(self._chk_autocheck)
        chk_form = self._make_default_form_layout()
        self._spin_check_timeout = QSpinBox()
        self._spin_check_timeout.setObjectName(
            PARAM_SPIN_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._spin_check_timeout.setRange(CHECK_TIMEOUT_MIN, CHECK_TIMEOUT_MAX)
        self._spin_check_timeout.setFixedWidth(PARAM_SPIN_WIDTH)
        timeout_label = QLabel(CHECK_TIMEOUT_LABEL_DINAMIC_POSTFIX_ME8C)
        timeout_label.setObjectName(
            SETTINGS_FIELD_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        timeout_label.setWordWrap(True)
        timeout_label.setToolTip(CHECK_TIMEOUT_TOOLTIP_DINAMIC_POSTFIX_ME8C)
        chk_form.addRow(timeout_label, self._spin_check_timeout)
        chk_body.addLayout(chk_form)
        self._chk_strict_types = QCheckBox(
            STRICT_TYPES_TEXT_DINAMIC_POSTFIX_ME8C
        )
        self._chk_strict_types.setObjectName(
            CHECK_LIGHT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        chk_body.addWidget(self._chk_strict_types)
        parent_layout.addWidget(chk_box)

    def _build_ui_settings_block(self, parent_layout: QVBoxLayout) -> None:
        """Append interface settings group.

        Args:
            parent_layout: Target parent layout.
        """
        ui_box, ui_body = self._make_collapsible(
            UI_BOX_TITLE_DINAMIC_POSTFIX_ME8C, collapsed=True
        )
        ui_form = self._make_default_form_layout()
        self._spin_font_size = QSpinBox()
        self._spin_font_size.setObjectName(
            PARAM_SPIN_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._spin_font_size.setRange(FONT_SIZE_MIN, FONT_SIZE_MAX)
        self._spin_font_size.setFixedWidth(PARAM_SPIN_WIDTH)
        font_size_label = QLabel(FONT_SIZE_LABEL_DINAMIC_POSTFIX_ME8C)
        font_size_label.setObjectName(
            SETTINGS_FIELD_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        font_size_label.setWordWrap(True)
        ui_form.addRow(font_size_label, self._spin_font_size)
        self._combo_ui_language = QComboBox()
        self._combo_ui_language.setObjectName(
            PARAM_SPIN_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        self._combo_ui_language.addItem(
            OPTION_UI_LANGUAGE_EN_DINAMIC_POSTFIX_K7WQ,
            UI_LANGUAGE_TAG_EN,
        )
        self._combo_ui_language.addItem(
            OPTION_UI_LANGUAGE_RU_DINAMIC_POSTFIX_K7WQ,
            UI_LANGUAGE_TAG_RU,
        )
        lang_label = QLabel(LABEL_UI_LANGUAGE_DINAMIC_POSTFIX_K7WQ)
        lang_label.setObjectName(
            SETTINGS_FIELD_LABEL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        lang_label.setWordWrap(True)
        ui_form.addRow(lang_label, self._combo_ui_language)
        ui_body.addLayout(ui_form)
        parent_layout.addWidget(ui_box)

    def _make_collapsible(
        self, title: str, *, collapsed: bool
    ) -> tuple[QFrame, QVBoxLayout]:
        """Build collapsible settings section.

        Args:
            title: Section title.
            collapsed: Initial collapsed state.

        Returns:
            Tuple of outer frame and inner body layout.
        """
        box = QFrame()
        box.setObjectName(COLLAPSIBLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        self._set_size_policy_ignored_preferred(box)
        outer = QVBoxLayout(box)
        outer.setContentsMargins(*FORM_MARGINS)
        outer.setSpacing(COLLAPSIBLE_SPACING)
        head = QPushButton()
        head.setObjectName(COLLAPSIBLE_HEAD_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        head.setFlat(True)
        head.setCursor(Qt.CursorShape.PointingHandCursor)
        head.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        head.setText(self._collapsible_title(title, is_open=not collapsed))
        body = QFrame()
        body.setObjectName(COLLAPSIBLE_BODY_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        self._set_size_policy_ignored_preferred(body)
        bl = QVBoxLayout(body)
        bl.setContentsMargins(*COLLAPSIBLE_BODY_MARGINS)
        bl.setSpacing(COLLAPSIBLE_BODY_SPACING)
        body.setVisible(not collapsed)

        def toggle() -> None:
            open_ = not body.isVisible()
            body.setVisible(open_)
            head.setText(self._collapsible_title(title, is_open=open_))

        head.clicked.connect(toggle)
        outer.addWidget(head)
        outer.addWidget(body)
        return (box, bl)

    def _build_history_page(self) -> QWidget:
        """Build history page widget for right tab stack.

        Returns:
            History page widget.
        """
        scroll = QScrollArea()
        self._configure_vertical_scroll_area(
            scroll, object_name=HISTORY_SCROLL_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        inner = QWidget()
        inner.setMinimumWidth(0)
        self._set_size_policy_ignored_preferred(inner)
        self._history_list_layout = self._make_vbox_layout(
            inner,
            margins=HISTORY_LAYOUT_MARGINS,
            spacing=HISTORY_LAYOUT_SPACING,
        )
        inner.setObjectName(HISTORY_INNER_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        scroll.setWidget(inner)
        self._history_scroll_inner = inner
        return scroll

    def _clear_history_list(self) -> None:
        """Remove all items from the lightweight history layout.

        Returns:
            None.
        """
        while self._history_list_layout.count():
            item = self._history_list_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_open_history_button(self) -> QPushButton:
        """Build shortcut button that opens the full history dialog.

        Returns:
            Configured history shortcut button.
        """
        button = QPushButton(OPEN_FULL_HISTORY_TEXT_DINAMIC_POSTFIX_ME8C)
        button.setObjectName(HISTORY_LINK_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self._open_history)
        return button

    def _build_empty_history_label(self) -> QLabel:
        """Build placeholder shown when no history entries exist.

        Returns:
            Configured empty-state label.
        """
        label = QLabel(HISTORY_EMPTY_TEXT_DINAMIC_POSTFIX_ME8C)
        label.setObjectName(
            HISTORY_EMPTY_HINT_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _history_mark_style(self, passed: bool) -> str:
        """Return stylesheet for a history result mark.

        Args:
            passed: Whether the history entry represents success.

        Returns:
            Stylesheet string for the mark label.
        """
        return (
            HISTORY_MARK_STYLE_OK_DINAMIC_POSTFIX_ME8C
            if passed
            else HISTORY_MARK_STYLE_BAD_DINAMIC_POSTFIX_ME8C
        )

    def _build_history_card(self, row: HistoryRowView) -> QFrame:
        """Build one compact history card for the sidebar.

        Args:
            row: Lightweight history row view.

        Returns:
            Configured history card frame.
        """
        card = QFrame()
        card.setObjectName(HISTORY_CARD_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        card_layout = self._make_vbox_layout(
            card,
            margins=HISTORY_CARD_MARGINS,
            spacing=LAYOUT_SPACING_NONE,
        )
        top_row = QHBoxLayout()
        title = QLabel(row.task_title[:HISTORY_TASK_TITLE_MAX])
        title.setObjectName(
            HISTORY_CARD_TITLE_OBJECT_NAME_DINAMIC_POSTFIX_ME8C
        )
        mark = QLabel(
            HISTORY_OK_MARK_DINAMIC_POSTFIX_ME8C
            if row.passed
            else HISTORY_BAD_MARK_DINAMIC_POSTFIX_ME8C
        )
        mark.setStyleSheet(self._history_mark_style(row.passed))
        top_row.addWidget(title, 1)
        top_row.addWidget(mark, 0)
        card_layout.addLayout(top_row)
        meta = QLabel(
            HISTORY_META_TEMPLATE_DINAMIC_POSTFIX_ME8C.format(
                ts=row.ts, pack=pack_label(row.pack_name)
            )
        )
        meta.setObjectName(HISTORY_CARD_META_OBJECT_NAME_DINAMIC_POSTFIX_ME8C)
        card_layout.addWidget(meta)
        return card

    def _reload_history_tab(self) -> None:
        """Reload lightweight history cards for sidebar tab."""
        self._clear_history_list()
        self._history_list_layout.addWidget(self._build_open_history_button())
        entries = load_entries_newest_first()[:HISTORY_MAX_ENTRIES]
        if not entries:
            self._history_list_layout.addWidget(
                self._build_empty_history_label()
            )
        else:
            for row in entries:
                self._history_list_layout.addWidget(
                    self._build_history_card(row)
                )
        self._history_list_layout.addStretch(1)

    def _on_duration_slider(self, value: int) -> None:
        """Update duration label text from slider value.

        Args:
            value: Slider value in minutes.
        """
        self._lbl_duration_val.setText(
            DURATION_VALUE_TEMPLATE_DINAMIC_POSTFIX_ME8C.format(
                minutes=value,
            )
        )
