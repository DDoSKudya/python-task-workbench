"""
This module implements the main-window “session” behavior for a
task-based checking app, handling session lifecycle, timers, navigation
between tasks, and display of check results and summaries.

It works as a mixin (MainWindowSessionMixin) that expects a host window
to provide various widgets and state attributes, then wires them to
core session logic, including starting and stopping sessions, updating
the countdown timer, enabling or disabling controls, and orchestrating
asynchronous code checks.

It contains helper protocols (SupportsHighlighter, SupportsCodeEditor,
MainWindowSessionHost), numerous UI and timing constants, and a small
locale-restart helper _restart_process_for_locale_reload plus
_initial_solution_code for determining starter code text.

Within the mixin, methods such as _start_clicked, _stop_clicked,
_apply_clicked, _load_current_task, _update_locks, and
_sync_task_section_visibility manage configuration, session creation via
build_session, per-task UI population, and lock state for buttons and
panels.

Timer-related methods (_reset_session_timer, _update_timer_label,
_on_timer_tick) compute total session time from tasks and per-task
minutes, update a timer label with a warning style near expiration, and
stop the session with a timeout dialog when time runs out.

Verification methods (_verify_clicked, _on_check_finished,
_on_worker_result_not_check_result) launch CheckWorker instances, track
in-flight checks and durations, update task state and styles based on
CheckResult, append history records, and optionally auto-advance to the
next task.

Summary-generation methods (_summary_status, _summary_task_row_model,
_show_session_end_summary, _finalize_session_cleanup,
_maybe_show_summary_after_last_task) map internal task statuses to
summary enums, build per-task summary rows, present a
SessionSummaryDialog, reset session state, and decide when to show the
summary after the last relevant check completes.

UI feedback helpers (_set_empty_check_label, _set_check_label,
_set_checking_label, _update_task_banner,
_show_check_status_for_current, _constraints_text) generate constraint
text, control visibility of sections, and drive a banner and label that
reflect pass/fail/checking states with appropriate styles and tooltips.

Navigation and persistence helpers (_persist_editor, _go_prev_task,
_go_next_task, _clear_session_task_ui, _clear_left_task_column,
_clear_task_views) ensure code edits are stored in session state, move
between tasks when allowed, and clear or hide task-related widgets when
the session stops or no session is active.

Finally, _open_history manages a non-modal HistoryDialog, while
_populate_from_defaults, _collect_config, and _apply_clicked integrate
with the configuration system to load, update, and save app and UI
defaults, including handling a language change by restarting the
process.
"""

from __future__ import annotations

import os
import sys
import time

from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QWidget,
)
from typing import TYPE_CHECKING, Final, Protocol, cast

from core.check_history import append_check_record
from core.config import (
    AppDefaults,
    UiDefaults,
    load_defaults,
    save_defaults_config,
)
from core.formatting import pretty, structure_signature
from core.models import CheckResult, SessionConfig, Task, TaskSession
from core.session import build_session
from messages import (
    BANNER_OK_TEXT_DINAMIC_POSTFIX_QLLY,
    BANNER_VARIANT_OK_DINAMIC_POSTFIX_QLLY,
    BULLET_PREFIX_DINAMIC_POSTFIX_QLLY,
    CHECK_FAILED_TEXT_DINAMIC_POSTFIX_QLLY,
    CHECK_OK_TEXT_DINAMIC_POSTFIX_QLLY,
    CHECK_WITH_DURATION_TEMPLATE_DINAMIC_POSTFIX_QLLY,
    CHECKING_LABEL_DINAMIC_POSTFIX_QLLY,
    CONSTRAINT_COLLECTIONS_DINAMIC_POSTFIX_QLLY,
    CONSTRAINT_PACK_DINAMIC_POSTFIX_QLLY,
    DOUBLE_NEWLINE_DINAMIC_POSTFIX_QLLY,
    ELLIPSIS_DINAMIC_POSTFIX_QLLY,
    EMPTY_FALLBACK_VALUE_DINAMIC_POSTFIX_QLLY,
    EMPTY_STYLE_DINAMIC_POSTFIX_QLLY,
    EMPTY_TOOLTIP_DINAMIC_POSTFIX_QLLY,
    LABEL_TIMER_NORMAL_DINAMIC_POSTFIX_QLLY,
    LABEL_TIMER_WARN_DINAMIC_POSTFIX_QLLY,
    MSGBOX_TEXT_SESSION_TIMEOUT_DINAMIC_POSTFIX_QLLY,
    MSGBOX_TEXT_SETTINGS_SAVED_DINAMIC_POSTFIX_QLLY,
    MSGBOX_TITLE_SESSION_DINAMIC_POSTFIX_QLLY,
    MSGBOX_TITLE_SETTINGS_DINAMIC_POSTFIX_QLLY,
    MSGBOX_TITLE_TIME_DINAMIC_POSTFIX_QLLY,
    NEWLINE_DINAMIC_POSTFIX_QLLY,
    PLACEHOLDER_ACTIVE_DINAMIC_POSTFIX_QLLY,
    PLACEHOLDER_INACTIVE_DINAMIC_POSTFIX_QLLY,
    STATUS_CHECKING_DINAMIC_POSTFIX_QLLY,
    STATUS_FAILED_DINAMIC_POSTFIX_QLLY,
    STATUS_PASSED_DINAMIC_POSTFIX_QLLY,
    STATUS_PENDING_DINAMIC_POSTFIX_QLLY,
    STYLE_CHECK_FAILED_DINAMIC_POSTFIX_QLLY,
    STYLE_CHECK_OK_DINAMIC_POSTFIX_QLLY,
    STYLE_CHECKING_DINAMIC_POSTFIX_QLLY,
    SUMMARY_HEADING_DINAMIC_POSTFIX_QLLY,
    TASK_TITLE_TEMPLATE_DINAMIC_POSTFIX_QLLY,
)
from messages.translate import set_locale
from ui.check_worker import CheckWorker
from ui.dialogs import (
    HistoryDialog,
    SessionStartDialog,
    SessionSummaryDialog,
    SessionSummaryTaskRow,
)
from ui.dialogs.session_summary.models import TaskStatus as SummaryTaskStatus

from .helpers import is_empty_mono_block, pack_label
from .summary import summary_report_for_state


def _restart_process_for_locale_reload() -> None:
    """Re-exec this process with the same argv so locale changes apply.

    Uses :func:`os.execv` to replace the running interpreter image.
    """
    os.execv(
        sys.executable,
        [sys.executable, sys.argv[0], *sys.argv[1:]],
    )


def _initial_solution_code(task: Task) -> str:
    """
    Return starter code or an empty placeholder for the editor buffer.

    Args:
        task: Current task; ``starter_code`` may be ``None``.

    Returns:
        ``task.starter_code`` when set; otherwise the catalog
        empty-style token used elsewhere for blank editor state.
    """
    return (
        task.starter_code
        if task.starter_code is not None
        else EMPTY_STYLE_DINAMIC_POSTFIX_QLLY
    )


class SupportsHighlighter(Protocol):
    """Protocol for text highlighter objects."""

    def rehighlight(self) -> None:
        """Re-highlight current document."""
        ...


class SupportsCodeEditor(Protocol):
    """Protocol for code editor widget used by session mixin."""

    def setReadOnly(self, value: bool) -> None:
        """Set read-only mode (Qt ``QPlainTextEdit`` API)."""
        ...

    def setPlaceholderText(self, text: str) -> None:
        """Set placeholder text (Qt API)."""
        ...

    def toPlainText(self) -> str:
        """Return plain document text (Qt API)."""
        ...

    def setPlainText(self, text: str) -> None:
        """Replace document text (Qt API)."""
        ...

    def clear(self) -> None:
        """Clear editor text."""
        ...

    def set_font_size(self, size: int) -> None:
        """Set editor font size."""
        ...

    def set_light_theme(self, enabled: bool) -> None:
        """Toggle light theme."""
        ...

    def set_solution_stub(self) -> None:
        """Insert default solution stub (no per-task starter)."""
        ...


class MainWindowSessionHost(Protocol):
    """Protocol that describes required main-window attributes."""

    _defaults: AppDefaults
    _session: TaskSession | None
    _session_active: bool
    _checks_running: int
    _check_started_at: dict[int, float]
    _finalize_summary_for_task_index: int | None
    _current_index: int
    _remaining_sec: int
    _alive: bool
    _history_dialog: HistoryDialog | None
    _slider_duration: QSlider
    _chk_autocheck: QCheckBox
    _chk_strict_types: QCheckBox
    _spin_check_timeout: QSpinBox
    _spin_font_size: QSpinBox
    _combo_ui_language: QComboBox
    _btn_start: QPushButton
    _btn_header_stop: QPushButton
    _btn_apply: QPushButton
    _btn_header_check: QPushButton
    _settings_inner: QWidget | None
    _history_scroll_inner: QWidget | None
    _editor: SupportsCodeEditor
    _lbl_timer: QLabel
    _timer: QTimer
    _task_aside_scroll: QScrollArea
    _task_banner: QFrame
    _task_banner_text: QLabel
    _lbl_task_title: QLabel
    _lbl_task_desc: QLabel
    _mono_input: QPlainTextEdit
    _mono_input_high: SupportsHighlighter
    _mono_output: QPlainTextEdit
    _mono_output_high: SupportsHighlighter
    _lbl_constraints: QLabel
    _fr_task_section: QFrame
    _fr_input_section: QFrame
    _fr_output_section: QFrame
    _fr_constraints_section: QFrame
    _lbl_check: QLabel

    def _update_header_session_controls(self) -> None:
        """Update header controls for session state."""
        ...

    def _on_duration_slider(self, value: int) -> None:
        """Handle duration slider change."""
        ...

    def _reload_history_tab(self) -> None:
        """Refresh sidebar history list."""
        ...


SECONDS_PER_MINUTE: Final[int] = 60
MIN_TOTAL_SESSION_SECONDS: Final[int] = 1
ONE: Final[int] = 1
ZERO_SECONDS: Final[int] = 0
DEFAULT_RUN_ID: Final[int] = 0
SUMMARY_TITLE_MAX_LENGTH: Final[int] = 120
SUMMARY_TITLE_TRIM_LENGTH: Final[int] = 117
SUMMARY_TITLE_NEWLINE_REPLACE: Final[str] = " "
DEFAULT_UI_FALLBACK_LANGUAGE: Final[str] = "en"
DEFAULT_CHECK_DURATION: Final[float] = 0.0
TIMER_WARN_THRESHOLD_SEC: Final[int] = 60
SUMMARY_STATUS_OK: Final[SummaryTaskStatus] = "ok"
SUMMARY_STATUS_BAD: Final[SummaryTaskStatus] = "bad"
SUMMARY_STATUS_CHECKING: Final[SummaryTaskStatus] = "checking"
SUMMARY_STATUS_PENDING: Final[SummaryTaskStatus] = "pending"


class MainWindowSessionMixin(
    MainWindowSessionHost if TYPE_CHECKING else object
):
    """Mix in session lifecycle: timer, tasks, checks, and end summary.

    Expects the host object to expose widgets and state described by
    :class:`MainWindowSessionHost`.
    """

    def _summary_status(self, status: str) -> SummaryTaskStatus:
        """Convert internal task status to summary row status.

        Args:
            status: Internal task state status.

        Returns:
            Status value expected by summary dialog row model.
        """
        if status == STATUS_PASSED_DINAMIC_POSTFIX_QLLY:
            return SUMMARY_STATUS_OK
        if status == STATUS_FAILED_DINAMIC_POSTFIX_QLLY:
            return SUMMARY_STATUS_BAD
        if status == STATUS_CHECKING_DINAMIC_POSTFIX_QLLY:
            return SUMMARY_STATUS_CHECKING
        return SUMMARY_STATUS_PENDING

    def _set_empty_check_label(self) -> None:
        """Clear check label text, tooltip, and style."""
        self._lbl_check.clear()
        self._lbl_check.setToolTip(EMPTY_TOOLTIP_DINAMIC_POSTFIX_QLLY)
        self._lbl_check.setStyleSheet(EMPTY_STYLE_DINAMIC_POSTFIX_QLLY)

    def _set_check_label(self, text: str, style: str) -> None:
        """Set check label text with tooltip reset and style.

        Args:
            text: User-facing text.
            style: Qt stylesheet string for the label.
        """
        self._lbl_check.setText(text)
        self._lbl_check.setToolTip(EMPTY_TOOLTIP_DINAMIC_POSTFIX_QLLY)
        self._lbl_check.setStyleSheet(style)

    def _set_checking_label(self) -> None:
        """Display checking state in the header check label."""
        self._set_check_label(
            CHECKING_LABEL_DINAMIC_POSTFIX_QLLY,
            STYLE_CHECKING_DINAMIC_POSTFIX_QLLY,
        )

    def _decrement_checks_running(self) -> None:
        """Decrease active check counter without going below zero."""
        self._checks_running = max(ZERO_SECONDS, self._checks_running - ONE)

    def _status_count(self, status: str) -> int:
        """Count task states with the provided status.

        Args:
            status: Session state status name.

        Returns:
            Number of states matching the status.
        """
        if self._session is None:
            return ZERO_SECONDS
        return sum(
            ONE for state in self._session.states if state.status == status
        )

    def _check_label_with_duration(
        self, *, base_text: str, duration: float, has_duration: bool
    ) -> str:
        """Build check status text with optional duration suffix.

        Args:
            base_text: Base status text without duration.
            duration: Check duration in seconds.
            has_duration: Whether duration should be appended.

        Returns:
            Ready-to-show status label text.
        """
        return (
            CHECK_WITH_DURATION_TEMPLATE_DINAMIC_POSTFIX_QLLY.format(
                base=base_text, duration=duration
            )
            if has_duration
            else base_text
        )

    def _populate_from_defaults(self) -> None:
        """Apply defaults into the session controls."""
        session_defaults = self._defaults.session
        self._slider_duration.setValue(session_defaults.per_task_minutes)
        self._on_duration_slider(session_defaults.per_task_minutes)
        self._chk_autocheck.setChecked(self._defaults.ui.autocheck_on_next)
        self._chk_strict_types.setChecked(session_defaults.strict_types)
        self._spin_check_timeout.setValue(session_defaults.check_timeout_sec)
        self._spin_font_size.setValue(self._defaults.ui.font_size)
        lang = self._defaults.ui.ui_language
        idx = self._combo_ui_language.findData(lang)
        if idx >= 0:
            self._combo_ui_language.setCurrentIndex(idx)

    def _collect_config(self) -> SessionConfig:
        """Collect current settings into session config."""
        session_defaults = self._defaults.session
        minutes = self._slider_duration.value()
        return SessionConfig(
            selected_packs=session_defaults.selected_packs,
            count=session_defaults.count,
            seed=session_defaults.seed,
            strict_types=self._chk_strict_types.isChecked(),
            checker_entry_mode=session_defaults.checker_entry_mode,
            check_timeout_sec=self._spin_check_timeout.value(),
            per_task_minutes=minutes,
        )

    def _update_locks(self) -> None:
        """Enable and disable controls based on session state."""
        active = self._session_active
        self._btn_start.setEnabled(not active)
        self._btn_header_stop.setEnabled(active)
        self._btn_apply.setEnabled(not active)
        if self._settings_inner is not None:
            self._settings_inner.setEnabled(not active)
        if self._history_scroll_inner is not None:
            self._history_scroll_inner.setEnabled(not active)
        self._editor.setReadOnly(not active)
        if active:
            self._editor.setPlaceholderText(
                PLACEHOLDER_ACTIVE_DINAMIC_POSTFIX_QLLY
            )
        else:
            self._editor.setPlaceholderText(
                PLACEHOLDER_INACTIVE_DINAMIC_POSTFIX_QLLY
            )
        self._update_verify_enabled()
        self._update_header_session_controls()

    def _current_task_has_code_for_check(self) -> bool:
        """Return whether current task has code to run."""
        if not self._session:
            return False
        index = self._current_index
        return bool(
            self._editor.toPlainText().strip()
            or self._session.states[index].code.strip()
        )

    def _update_verify_enabled(self) -> None:
        """Update availability of verify button."""
        is_enabled = (
            bool(self._session and self._session_active)
            and self._current_task_has_code_for_check()
        )
        self._btn_header_check.setEnabled(is_enabled)

    def _update_timer_label(self) -> None:
        """Render timer value and warning visual state."""
        minutes = self._remaining_sec // SECONDS_PER_MINUTE
        seconds = self._remaining_sec % SECONDS_PER_MINUTE
        self._lbl_timer.setText(f"{minutes}:{seconds:02d}")
        is_low = (
            self._session_active
            and ZERO_SECONDS < self._remaining_sec <= TIMER_WARN_THRESHOLD_SEC
        )
        object_name = (
            LABEL_TIMER_WARN_DINAMIC_POSTFIX_QLLY
            if is_low
            else LABEL_TIMER_NORMAL_DINAMIC_POSTFIX_QLLY
        )
        self._lbl_timer.setObjectName(object_name)
        style = self._lbl_timer.style()
        if style is not None:
            style.unpolish(self._lbl_timer)
            style.polish(self._lbl_timer)

    def _reset_session_timer(self) -> None:
        """
        Set ``_remaining_sec`` from task count and per-task duration.
        """
        if self._session:
            task_count = len(self._session.tasks)
            per_task_minutes = self._session.config.per_task_minutes
            total_seconds = task_count * per_task_minutes * SECONDS_PER_MINUTE
            self._remaining_sec = max(MIN_TOTAL_SESSION_SECONDS, total_seconds)
        else:
            self._remaining_sec = ZERO_SECONDS
        self._update_timer_label()

    def _on_timer_tick(self) -> None:
        """Handle per-second timer tick for active session."""
        if not self._session_active:
            return
        self._remaining_sec = max(ZERO_SECONDS, self._remaining_sec - ONE)
        self._update_timer_label()
        if self._remaining_sec <= ZERO_SECONDS:
            self._timer.stop()
            self._persist_editor()
            self._session_active = False
            self._clear_session_task_ui()
            self._update_locks()
            QMessageBox.warning(
                cast(QWidget, self),
                MSGBOX_TITLE_TIME_DINAMIC_POSTFIX_QLLY,
                MSGBOX_TEXT_SESSION_TIMEOUT_DINAMIC_POSTFIX_QLLY,
            )

    def _start_clicked(self) -> None:
        """Start a new session from start dialog config."""
        dialog = SessionStartDialog(
            cast(QWidget, self), self._defaults.session
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            config = dialog.build_full_config(
                per_task_minutes=self._slider_duration.value(),
                strict_types=self._chk_strict_types.isChecked(),
                check_timeout_sec=self._spin_check_timeout.value(),
            )
        except ValueError as error:
            QMessageBox.warning(
                cast(QWidget, self),
                MSGBOX_TITLE_SESSION_DINAMIC_POSTFIX_QLLY,
                str(error),
            )
            return
        try:
            session = build_session(config)
        except Exception as exc:
            QMessageBox.critical(
                cast(QWidget, self),
                MSGBOX_TITLE_SESSION_DINAMIC_POSTFIX_QLLY,
                str(exc),
            )
            return
        self._defaults = AppDefaults(session=config, ui=self._defaults.ui)
        self._session = session
        self._checks_running = ZERO_SECONDS
        self._check_started_at.clear()
        self._finalize_summary_for_task_index = None
        self._current_index = ZERO_SECONDS
        self._session_active = True
        self._task_aside_scroll.show()
        self._reset_session_timer()
        self._timer.start()
        self._load_current_task()
        self._refresh_stats()
        self._update_locks()
        self._set_empty_check_label()
        self._task_banner.hide()

    def _stop_clicked(self) -> None:
        """Stop active session and clear task UI."""
        self._timer.stop()
        self._session_active = False
        self._persist_editor()
        self._clear_session_task_ui()
        self._update_locks()

    def _apply_clicked(self) -> None:
        """Persist settings to defaults configuration."""
        try:
            config = self._collect_config()
        except ValueError as error:
            QMessageBox.warning(
                cast(QWidget, self),
                MSGBOX_TITLE_SETTINGS_DINAMIC_POSTFIX_QLLY,
                str(error),
            )
            return
        old_lang = self._defaults.ui.ui_language
        raw_lang = self._combo_ui_language.currentData()
        new_lang = (
            raw_lang
            if isinstance(raw_lang, str)
            else DEFAULT_UI_FALLBACK_LANGUAGE
        )

        ui_defaults = UiDefaults(
            default_packs=config.selected_packs,
            window_compact=self._defaults.ui.window_compact,
            font_size=self._spin_font_size.value(),
            autocheck_on_next=self._chk_autocheck.isChecked(),
            splitter_sizes=self._defaults.ui.splitter_sizes,
            ui_language=new_lang,
        )
        save_defaults_config(config, ui_defaults)
        self._defaults = load_defaults()
        if old_lang != new_lang:
            set_locale(new_lang)
            _restart_process_for_locale_reload()
        self._editor.set_font_size(self._defaults.ui.font_size)
        self._editor.set_light_theme(True)
        self._populate_from_defaults()
        QMessageBox.information(
            cast(QWidget, self),
            MSGBOX_TITLE_SETTINGS_DINAMIC_POSTFIX_QLLY,
            MSGBOX_TEXT_SETTINGS_SAVED_DINAMIC_POSTFIX_QLLY,
        )

    def _persist_editor(self) -> None:
        """Persist current editor code into session state."""
        if self._session is None:
            return
        self._session.states[self._current_index].code = (
            self._editor.toPlainText()
        )

    def _constraints_text(self, task: Task) -> str:
        """Build constraints block text for the task card.

        Args:
            task: Task model from current session.

        Returns:
            Multi-line constraints text for UI label.
        """
        collections = (
            ", ".join(task.collections)
            if task.collections
            else EMPTY_FALLBACK_VALUE_DINAMIC_POSTFIX_QLLY
        )
        pack_line = (
            f"{BULLET_PREFIX_DINAMIC_POSTFIX_QLLY} "
            f"{CONSTRAINT_PACK_DINAMIC_POSTFIX_QLLY}: "
            f"{pack_label(task.pack_name)}"
        )
        return (
            f"{BULLET_PREFIX_DINAMIC_POSTFIX_QLLY} "
            f"{CONSTRAINT_COLLECTIONS_DINAMIC_POSTFIX_QLLY}: {collections}"
            f"{NEWLINE_DINAMIC_POSTFIX_QLLY}"
            f"{pack_line}"
        )

    def _sync_task_section_visibility(self) -> None:
        """Synchronize task section visibility with current content."""
        title = self._lbl_task_title.text().strip()
        description = self._lbl_task_desc.text().strip()
        self._fr_task_section.setVisible(bool(title or description))
        self._lbl_task_title.setVisible(bool(title))
        self._lbl_task_desc.setVisible(bool(description))
        self._fr_input_section.setVisible(
            not is_empty_mono_block(self._mono_input.toPlainText())
        )
        self._fr_output_section.setVisible(
            not is_empty_mono_block(self._mono_output.toPlainText())
        )
        self._fr_constraints_section.setVisible(
            bool(self._lbl_constraints.text().strip())
        )

    def _load_current_task(self, *, persist_before: bool = True) -> None:
        """Load task content and solution for current index.

        Args:
            persist_before: Whether to persist previous editor state
            first.
        """
        if self._session is None:
            self._clear_task_views()
            return
        if persist_before:
            self._persist_editor()
        task = self._session.tasks[self._current_index]
        state = self._session.states[self._current_index]
        self._lbl_task_title.setText(task.title)
        self._lbl_task_desc.setText(task.description or "")
        self._mono_input.setPlainText(pretty(task.input_data))
        self._mono_input_high.rehighlight()
        sig = structure_signature(task.expected_result)
        body = pretty(task.expected_result)
        output_text = f"{sig}{DOUBLE_NEWLINE_DINAMIC_POSTFIX_QLLY}{body}"
        self._mono_output.setPlainText(output_text.strip())
        self._mono_output_high.rehighlight()
        self._lbl_constraints.setText(self._constraints_text(task))
        if state.code.strip():
            self._editor.setPlainText(state.code)
        else:
            self._editor.setPlainText(_initial_solution_code(task))
        self._update_task_banner()
        self._show_check_status_for_current()
        self._update_locks()
        self._sync_task_section_visibility()

    def _clear_left_task_column(self, *, hide_aside: bool) -> None:
        """Clear left task panel content.

        Args:
            hide_aside: Whether to hide aside scroll area as well.
        """
        self._lbl_task_title.clear()
        self._lbl_task_desc.clear()
        self._mono_input.clear()
        self._mono_output.clear()
        self._lbl_constraints.clear()
        self._task_banner_text.setToolTip(EMPTY_TOOLTIP_DINAMIC_POSTFIX_QLLY)
        self._task_banner.hide()
        self._mono_input_high.rehighlight()
        self._mono_output_high.rehighlight()
        self._sync_task_section_visibility()
        if hide_aside:
            self._task_aside_scroll.hide()

    def _clear_session_task_ui(self) -> None:
        """Clear task-related UI and check metadata for session stop."""
        self._check_started_at.clear()
        self._finalize_summary_for_task_index = None
        self._clear_left_task_column(hide_aside=True)
        self._editor.clear()
        self._set_empty_check_label()

    def _clear_task_views(self) -> None:
        """Clear task views when no session is available."""
        self._clear_session_task_ui()

    def _update_task_banner(self) -> None:
        """Update top task banner according to current task state."""
        if self._session is None:
            self._task_banner.hide()
            return
        state = self._session.states[self._current_index]
        if state.status == STATUS_PASSED_DINAMIC_POSTFIX_QLLY:
            self._task_banner.setProperty(
                "variant", BANNER_VARIANT_OK_DINAMIC_POSTFIX_QLLY
            )
            self._task_banner_text.setText(BANNER_OK_TEXT_DINAMIC_POSTFIX_QLLY)
            self._task_banner_text.setToolTip(
                EMPTY_TOOLTIP_DINAMIC_POSTFIX_QLLY
            )
            self._task_banner.show()
        else:
            self._task_banner_text.setToolTip(
                EMPTY_TOOLTIP_DINAMIC_POSTFIX_QLLY
            )
            self._task_banner.hide()
        style = self._task_banner.style()
        if style is not None:
            style.unpolish(self._task_banner)
            style.polish(self._task_banner)

    def _show_check_status_for_current(self) -> None:
        """Show check status label for the current task."""
        if self._session is None:
            return
        state = self._session.states[self._current_index]
        if state.status == STATUS_PASSED_DINAMIC_POSTFIX_QLLY:
            self._set_check_label(
                CHECK_OK_TEXT_DINAMIC_POSTFIX_QLLY,
                STYLE_CHECK_OK_DINAMIC_POSTFIX_QLLY,
            )
        elif state.status == STATUS_FAILED_DINAMIC_POSTFIX_QLLY:
            self._set_check_label(
                CHECK_FAILED_TEXT_DINAMIC_POSTFIX_QLLY,
                STYLE_CHECK_FAILED_DINAMIC_POSTFIX_QLLY,
            )
        else:
            self._set_empty_check_label()

    def _go_prev_task(self) -> None:
        """Navigate to previous task when available."""
        if (
            not self._session
            or not self._session_active
            or self._current_index <= ZERO_SECONDS
        ):
            return
        self._persist_editor()
        self._current_index -= ONE
        self._load_current_task(persist_before=False)

    def _go_next_task(self) -> None:
        """Navigate to next task when available."""
        if not self._session or not self._session_active:
            return
        if self._current_index >= len(self._session.tasks) - ONE:
            return
        self._persist_editor()
        self._current_index += ONE
        self._load_current_task(persist_before=False)

    def _refresh_stats(self) -> None:
        """Hook for statistics widgets; base implementation does
        nothing.

        Subclasses or future work may override or extend this to update
        counters when session or check state changes.

        Returns:
            None
        """
        return

    def _summary_task_row_model(
        self, session: TaskSession, index: int
    ) -> SessionSummaryTaskRow:
        """Build summary row model for one task.

        Args:
            session: Session with tasks and states.
            index: Task index in session.

        Returns:
            Summary row model for summary dialog.
        """
        task = session.tasks[index]
        state = session.states[index]
        title = (
            task.title
            or TASK_TITLE_TEMPLATE_DINAMIC_POSTFIX_QLLY.format(
                number=index + ONE
            )
        ).replace(
            NEWLINE_DINAMIC_POSTFIX_QLLY,
            SUMMARY_TITLE_NEWLINE_REPLACE,
        )
        if len(title) > SUMMARY_TITLE_MAX_LENGTH:
            title = f"{title[:SUMMARY_TITLE_TRIM_LENGTH]}{ELLIPSIS_DINAMIC_POSTFIX_QLLY}"
        report = summary_report_for_state(state)
        code_text = state.code.strip() or None
        return SessionSummaryTaskRow(
            num=index + ONE,
            status=self._summary_status(state.status),
            title=title,
            report_text=report,
            code_text=code_text,
        )

    def _show_session_end_summary(self, session: TaskSession) -> None:
        """Show final session summary dialog.

        Args:
            session: Completed or stopped task session.
        """
        self._persist_editor()
        task_count = len(session.tasks)
        ok_n = self._status_count(STATUS_PASSED_DINAMIC_POSTFIX_QLLY)
        bad_n = self._status_count(STATUS_FAILED_DINAMIC_POSTFIX_QLLY)
        pend_n = self._status_count(STATUS_PENDING_DINAMIC_POSTFIX_QLLY)
        chk_n = self._status_count(STATUS_CHECKING_DINAMIC_POSTFIX_QLLY)
        task_rows = [
            self._summary_task_row_model(session, index)
            for index in range(task_count)
        ]
        all_ok = all(
            state.status == STATUS_PASSED_DINAMIC_POSTFIX_QLLY
            for state in session.states
        )
        self._finalize_session_cleanup()
        SessionSummaryDialog(
            cast(QWidget, self),
            heading=SUMMARY_HEADING_DINAMIC_POSTFIX_QLLY,
            ok_n=ok_n,
            bad_n=bad_n,
            pend_n=pend_n,
            chk_n=chk_n,
            task_rows=task_rows,
            all_passed=all_ok,
        ).exec()
        self._reload_history_tab()

    def _finalize_session_cleanup(self) -> None:
        """Stop timer and reset session data before summary window."""
        self._timer.stop()
        self._session_active = False
        self._checks_running = ZERO_SECONDS
        self._check_started_at.clear()
        self._finalize_summary_for_task_index = None
        self._session = None
        self._current_index = ZERO_SECONDS
        self._clear_session_task_ui()
        self._remaining_sec = ZERO_SECONDS
        self._update_timer_label()
        self._refresh_stats()
        self._update_locks()

    def _maybe_show_summary_after_last_task(self, task_index: int) -> None:
        """Open summary when finished check matches final marker.

        Args:
            task_index: Index of completed check.
        """
        final_index = self._finalize_summary_for_task_index
        if final_index is None or task_index != final_index:
            return
        self._finalize_summary_for_task_index = None
        if self._session is not None:
            self._show_session_end_summary(self._session)

    def _verify_clicked(self) -> None:
        """Run asynchronous verification for current task."""
        if not self._btn_header_check.isEnabled() or self._session is None:
            return
        self._persist_editor()
        session = self._session
        check_ix = self._current_index
        code = session.states[check_ix].code.strip()
        if not code:
            return
        self._checks_running += ONE
        self._check_started_at[check_ix] = time.perf_counter()
        session.states[check_ix].status = (
            STATUS_CHECKING_DINAMIC_POSTFIX_QLLY  # pyright: ignore[reportAttributeAccessIssue]
        )
        self._refresh_stats()
        task = session.tasks[check_ix]
        worker = CheckWorker(
            task_index=check_ix,
            task=task,
            code=code,
            strict_types=session.config.strict_types,
            checker_entry_mode=session.config.checker_entry_mode,
            timeout_sec=session.config.check_timeout_sec,
            run_id=DEFAULT_RUN_ID,
            parent=cast(QObject, self),
        )
        worker.finished_for.connect(self._on_check_finished)
        worker.finished.connect(worker.deleteLater)
        worker.start()
        n_tasks = len(session.tasks)
        self._finalize_summary_for_task_index = (
            check_ix if n_tasks == ONE or check_ix == n_tasks - ONE else None
        )
        if n_tasks > ONE and check_ix < n_tasks - ONE:
            self._current_index = (check_ix + ONE) % n_tasks
            self._load_current_task(persist_before=False)
        else:
            self._set_checking_label()
        self._update_verify_enabled()

    def _on_worker_result_not_check_result(self, task_index: int) -> None:
        """Handle a worker payload that is not a ``CheckResult``.

        Clears a stuck ``checking`` state, refreshes controls, and may
        show the session summary when appropriate.

        Args:
            task_index: Index of the task tied to this worker run.

        Returns:
            None
        """
        session = self._session
        if session is None:
            return
        state = session.states[task_index]
        if state.status == STATUS_CHECKING_DINAMIC_POSTFIX_QLLY:
            state.status = STATUS_PENDING_DINAMIC_POSTFIX_QLLY  # pyright: ignore[reportAttributeAccessIssue]
        self._refresh_stats()
        self._decrement_checks_running()
        self._check_started_at.pop(task_index, None)
        self._update_verify_enabled()
        if self._checks_running == ZERO_SECONDS:
            self._show_check_status_for_current()
        self._update_task_banner()
        self._maybe_show_summary_after_last_task(task_index)

    def _on_check_finished(
        self, _run_id: int, task_index: int, result: object
    ) -> None:
        """Handle check worker completion and update UI/state.

        Args:
            _run_id: Reserved worker run identifier.
            task_index: Checked task index.
            result: Worker payload expected to be ``CheckResult``.
        """
        if not self._alive:
            return
        if self._session is None:
            self._decrement_checks_running()
            return
        if not isinstance(result, CheckResult):
            self._on_worker_result_not_check_result(task_index)
            return
        session = self._session
        state = session.states[task_index]
        state.result = result
        state.status = (  # pyright: ignore[reportAttributeAccessIssue]
            STATUS_PASSED_DINAMIC_POSTFIX_QLLY
            if result.passed
            else STATUS_FAILED_DINAMIC_POSTFIX_QLLY
        )
        check_started_at = self._check_started_at.pop(task_index, None)
        duration = (
            time.perf_counter() - check_started_at
            if check_started_at is not None
            else DEFAULT_CHECK_DURATION
        )
        task = session.tasks[task_index]
        append_check_record(
            task=task,
            result=result,
            code=state.code,
            config=session.config,
            duration_sec=duration,
        )
        self._refresh_stats()
        self._decrement_checks_running()
        self._update_verify_enabled()
        if task_index == self._current_index:
            is_passed = result.passed
            base_text = (
                CHECK_OK_TEXT_DINAMIC_POSTFIX_QLLY
                if is_passed
                else CHECK_FAILED_TEXT_DINAMIC_POSTFIX_QLLY
            )
            style = (
                STYLE_CHECK_OK_DINAMIC_POSTFIX_QLLY
                if is_passed
                else STYLE_CHECK_FAILED_DINAMIC_POSTFIX_QLLY
            )
            label_text = self._check_label_with_duration(
                base_text=base_text,
                duration=duration,
                has_duration=check_started_at is not None,
            )
            self._set_check_label(label_text, style)
        else:
            self._show_check_status_for_current()
        self._update_task_banner()
        self._maybe_show_summary_after_last_task(task_index)

    def _open_history(self) -> None:
        """Open or focus non-modal history dialog."""
        dialog = getattr(self, "_history_dialog", None)
        if dialog is None:
            dialog = HistoryDialog(cast(QWidget, self))
            self._history_dialog = dialog
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
