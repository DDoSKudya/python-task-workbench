"""
This module defines the main application window for a PyQt-based
task-checking app, wiring together the UI layout and the session logic
mixins.

It works by subclassing QMainWindow and mixing in MainWindowUiMixin and
MainWindowSessionMixin, then in __init__ setting up defaults, timers,
the three-column UI, initial state, and global keyboard shortcuts.

It defines window geometry and timing constants, plus small protocol
types (SupportsSignal, SupportsEditorSignal) that describe minimal
signal interfaces for connecting handlers.

The _configure_window, _setup_timer, and _build_ui methods set the
window title and size, create a 1-second QTimer for session countdown,
and assemble the header, task sidebar, editor, and right aside using the
UI mixin helpers.

The _initialize_state method loads persisted defaults into controls,
syncs header and timer labels, clears task views, applies lock states,
and hooks the editors textChanged signal to re-evaluate whether
verification is enabled.

Editor focus styling is handled by _apply_editor_shell_focus_style,
_handle_editor_focus_event, and an overridden eventFilter, which toggle
a dynamic property on the editor shell frame and re-polish its style on
focus in/out events.

Keyboard accelerators are registered via _bind_shortcut and
_bind_shortcuts, mapping configurable key sequences to verify and
next/previous task handlers provided by the session mixin.

The overridden closeEvent marks the window as no longer alive, stops the
session timer, and then delegates to the base class, ensuring
background work and timing logic are shut down cleanly when the window
closes.
"""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QEvent, QObject, QTimer
from PyQt6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFrame,
    QMainWindow,
    QWidget,
)
from typing import Final, Protocol, cast

from core.config import AppDefaults
from core.models import TaskSession
from messages import (
    EDITOR_SHELL_FOCUSED_PROPERTY_DINAMIC_POSTFIX_EBOU,
    ROOT_OBJECT_NAME_DINAMIC_POSTFIX_EBOU,
    SHORTCUT_NEXT_TASK_DINAMIC_POSTFIX_EBOU,
    SHORTCUT_PREV_TASK_DINAMIC_POSTFIX_EBOU,
    SHORTCUT_VERIFY_ALTERNATIVE_DINAMIC_POSTFIX_EBOU,
    SHORTCUT_VERIFY_PRIMARY_DINAMIC_POSTFIX_EBOU,
    WINDOW_TITLE_DINAMIC_POSTFIX_EBOU,
)

from .session_logic import MainWindowSessionMixin
from .ui_build import MainWindowUiMixin

type NoArgHandler = Callable[[], None]

WINDOW_WIDTH: Final[int] = 1480
WINDOW_HEIGHT: Final[int] = 920
WINDOW_MIN_WIDTH: Final[int] = 1024
WINDOW_MIN_HEIGHT: Final[int] = 700
ZERO_MARGINS: Final[tuple[int, int, int, int]] = (0, 0, 0, 0)
LAYOUT_SPACING_NONE: Final[int] = 0
TIMER_INTERVAL_MS: Final[int] = 1000
_FOCUS_IN_TYPE: Final[QEvent.Type] = QEvent.Type.FocusIn
_FOCUS_OUT_TYPE: Final[QEvent.Type] = QEvent.Type.FocusOut


class SupportsSignal(Protocol):
    """Qt-like emitter exposing ``connect`` for zero-arg handlers."""

    def connect(self, handler: NoArgHandler) -> object:
        """Register ``handler`` to run when the signal fires."""
        ...


class SupportsEditorSignal(Protocol):
    """Minimal editor surface for ``textChanged`` subscription."""

    textChanged: SupportsSignal


class MainWindow(QMainWindow, MainWindowUiMixin, MainWindowSessionMixin):
    """
    Application window wiring mixins for UI shell and session behavior.
    """

    def __init__(
        self, defaults: AppDefaults, parent: QWidget | None = None
    ) -> None:
        """Build chrome, session state, and keyboard bindings.

        Args:
            defaults: Persisted defaults (fonts, packs, timing, and UI).
            parent: Optional Qt parent, usually ``None`` for top-level.
        """
        super().__init__(parent)
        self._defaults = defaults
        self._session: TaskSession | None = None
        self._session_active = False
        self._current_index = 0
        self._alive = True
        self._checks_running = 0
        self._check_started_at: dict[int, float] = {}
        self._finalize_summary_for_task_index: int | None = None
        self._remaining_sec = 0
        self._history_dialog: QWidget | None = None
        self._settings_inner: QWidget | None = None
        self._editor_shell: QFrame | None = None
        self._configure_window()
        self._setup_timer()
        self._build_ui()
        self._initialize_state()
        self._bind_shortcuts()

    def _configure_window(self) -> None:
        """Set title, initial geometry, and minimum usable size."""
        self.setWindowTitle(WINDOW_TITLE_DINAMIC_POSTFIX_EBOU)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

    def _setup_timer(self) -> None:
        """
        Attach a single-shot interval timer for the session countdown.
        """
        self._timer = QTimer(self)
        self._timer.setInterval(TIMER_INTERVAL_MS)
        self._timer.timeout.connect(self._on_timer_tick)

    def _build_ui(self) -> None:
        """
        Compose header strip and three-column body from the UI mixin.
        """
        root = QWidget()
        root.setObjectName(ROOT_OBJECT_NAME_DINAMIC_POSTFIX_EBOU)
        self.setCentralWidget(root)
        main_layout = self._make_vbox_layout(
            root, margins=ZERO_MARGINS, spacing=LAYOUT_SPACING_NONE
        )
        main_layout.addWidget(self._build_light_header())
        body_widget = QWidget()
        body = self._make_hbox_layout(
            body_widget,
            margins=ZERO_MARGINS,
            spacing=LAYOUT_SPACING_NONE,
        )
        body.addWidget(self._build_task_aside(), 0)
        body.addWidget(self._build_center_column(), 1)
        body.addWidget(self._build_right_aside(), 0)
        main_layout.addWidget(body_widget, 1)

    def _initialize_state(self) -> None:
        """
        Load defaults, sync header/timer, and wire editor callbacks.
        """
        self._populate_from_defaults()
        self._update_header_session_controls()
        self._update_timer_label()
        self._clear_task_views()
        self._update_locks()
        editor = cast(SupportsEditorSignal, self._editor)
        editor.textChanged.connect(self._update_verify_enabled)

    def _apply_editor_shell_focus_style(self, *, focused: bool) -> None:
        """Toggle dynamic property driving editor chrome QSS state.

        Args:
            focused: ``True`` when the code editor receives focus.
        """
        shell = self._editor_shell
        if shell is None:
            return
        style = shell.style()
        if style is None:
            return
        shell.setProperty(
            EDITOR_SHELL_FOCUSED_PROPERTY_DINAMIC_POSTFIX_EBOU,
            focused,
        )
        style.unpolish(shell)
        style.polish(shell)

    def _bind_shortcut(self, sequence: str, handler: NoArgHandler) -> None:
        """
        Bind one global shortcut using a human-readable sequence string.

        Args:
            sequence: Value accepted by
            :class:`~PyQt6.QtGui.QKeySequence`.
            handler: Zero-argument slot on ``self``.
        """
        QShortcut(QKeySequence(sequence), self).activated.connect(handler)

    def _bind_shortcuts(self) -> None:
        """Register verify and task navigation accelerators."""
        self._bind_shortcut(
            SHORTCUT_VERIFY_PRIMARY_DINAMIC_POSTFIX_EBOU,
            self._verify_clicked,
        )
        self._bind_shortcut(
            SHORTCUT_VERIFY_ALTERNATIVE_DINAMIC_POSTFIX_EBOU,
            self._verify_clicked,
        )
        self._bind_shortcut(
            SHORTCUT_PREV_TASK_DINAMIC_POSTFIX_EBOU,
            self._go_prev_task,
        )
        self._bind_shortcut(
            SHORTCUT_NEXT_TASK_DINAMIC_POSTFIX_EBOU,
            self._go_next_task,
        )

    def _handle_editor_focus_event(self, event: QEvent) -> None:
        """Apply shell styling for focus enter/leave on the editor.

        Args:
            event: Focus event issued for the code editor widget.
        """
        ev_type = event.type()
        if ev_type == _FOCUS_IN_TYPE:
            self._apply_editor_shell_focus_style(focused=True)
        elif ev_type == _FOCUS_OUT_TYPE:
            self._apply_editor_shell_focus_style(focused=False)

    def eventFilter(
        self,
        a0: QObject | None,
        a1: QEvent | None,
    ) -> bool:
        """Forward editor focus events to shell styling refresh logic.

        Args:
            a0: Object Qt dispatches the event to (Qt parameter name).
            a1: Concrete event instance, or ``None`` if absent.

        Returns:
            Value from :meth:`QObject.eventFilter` (whether filtered
            out).
        """
        editor_object = cast(QObject, self._editor)
        if a1 is not None and a0 is editor_object:
            self._handle_editor_focus_event(a1)
        return super().eventFilter(a0, a1)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        """Mark the window dead and stop timers before the widget is
        gone.

        Args:
            a0: Native Qt close request (Qt parameter name).
        """
        self._alive = False
        self._timer.stop()
        super().closeEvent(a0)
