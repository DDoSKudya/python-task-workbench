"""
This module implements a custom Python code editor widget (CodeEditor)
with line numbers, syntax highlighting, on-the-fly syntax error
marking, bracket/quote pairing, and context-aware autocompletion.

It works by subclassing QPlainTextEdit, wiring timers and event filters,
and integrating a QCompleter, a gutter widget, a Python syntax
highlighter, and lightweight type inference to provide an IDE-like
editing experience inside the Qt application.

It defines numerous constants controlling font families and sizes, tab
width, completion timing and popup geometry, line-number gutter
padding, bracket/quote pairing rules, and syntax-error colors.

The constructor configures the editors appearance (monospace font, no
frame, placeholder text), installs a PythonHighlighter, sets up tab
stops, constructs a QCompleter backed by a QStringListModel, and
initializes timers for debounced syntax parsing and word completion.

Line-number support is handled via a separate LineNumberArea widget;
methods like line_number_area_width, resizeEvent,
line_number_area_paint_event, _update_line_number_area_width, and
_update_line_number_area_rect keep the gutter aligned and repaint line
numbers as the document or viewport changes.

Theme switching and font resizing are supported by set_light_theme and
set_font_size, which update gutter colors, reinstantiate the
highlighter in dark/light mode, and recompute margins.

Syntax error feedback comes from _refresh_syntax_error_highlight, which
parses the buffer with ast.parse after a delay, then either clears the
error state or selects the offending line with a colored background and
wave underline via _syntax_error_format and
_apply_syntax_error_selection, also setting a tooltip with error
details.

Autocomplete is managed through a combination of _install_completer,
_install_deferred_timers, _run_word_completion_if_applicable,
_update_global_completion, _update_member_completion, and
_show_completion_popup, which together compute identifier prefixes,
build candidate word lists (build_word_list or inferred member methods),
and position a popup under the cursor.

Member completion leverages infer_symbol_types and
python_type_method_map to suggest methods after a dot based on inferred
variable types, while global completion suggests words from the current
buffer when typing or on Ctrl+Space.

Bracket and quote pairing behavior is implemented by
_handle_pair_insertion and _handle_closer_skip, which wrap selections
or insert/open-closer pairs and skip over existing closers to avoid
duplication.

Keyboard and mouse events are funneled through keyPressEvent,
_handle_pre_key_event, _handle_completion_navigation,
_update_completion_after_typing, and eventFilter, which coordinate
escape handling, popup navigation, completion acceptance, prefix
updates, and hiding the popup when the user clicks elsewhere.

Higher-level helpers like set_solution_stub populate the editor with a
default solution template, and _popup abstracts access to the
completers popup view, tying all these features into a cohesive,
reusable code-editing component for the application.
"""

from __future__ import annotations

import ast
import re

from PyQt6.QtCore import QEvent, QObject, QRect, QStringListModel, Qt, QTimer
from PyQt6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QTextCharFormat,
    QTextCursor,
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCompleter,
    QPlainTextEdit,
    QTextEdit,
)

from messages import (
    CODE_EDITOR_FONT_FAMILY_FALLBACK_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_FONT_FAMILY_PRIMARY_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_FONT_FAMILY_SECONDARY_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_FONT_FAMILY_TERTIARY_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_PAIR_BRACE_CLOSE_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_PAIR_BRACE_OPEN_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_PAIR_BRACKET_CLOSE_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_PAIR_BRACKET_OPEN_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_PAIR_DOUBLE_QUOTE_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_PAIR_PAREN_CLOSE_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_PAIR_PAREN_OPEN_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_PAIR_SINGLE_QUOTE_DINAMIC_POSTFIX_EMAU,
    COLOR_SYNTAX_UNDERLINE_DINAMIC_POSTFIX_EMAU,
    COMPLETER_POPUP_STYLESHEET_DINAMIC_POSTFIX_EMAU,
    DIGIT_SAMPLE_DINAMIC_POSTFIX_EMAU,
    EMPTY_STRING_DINAMIC_POSTFIX_TGHG,
    LINE_NUMBER_BG_DARK_DINAMIC_POSTFIX_EMAU,
    LINE_NUMBER_BG_LIGHT_DINAMIC_POSTFIX_EMAU,
    LINE_NUMBER_FG_DARK_DINAMIC_POSTFIX_EMAU,
    LINE_NUMBER_FG_LIGHT_DINAMIC_POSTFIX_EMAU,
    MEMBER_TRIGGER_CHAR_DINAMIC_POSTFIX_EMAU,
    NEWLINE_CHAR_DINAMIC_POSTFIX_EMAU,
    OBJECT_NAME_COMPLETER_POPUP_DINAMIC_POSTFIX_EMAU,
    OBJECT_NAME_EDITOR_DINAMIC_POSTFIX_EMAU,
    PARAGRAPH_SEPARATOR_DINAMIC_POSTFIX_EMAU,
    PLACEHOLDER_TEXT_DINAMIC_POSTFIX_EMAU,
    RE_MEMBER_DOT_DINAMIC_POSTFIX_EMAU,
    RE_MEMBER_PARTIAL_DINAMIC_POSTFIX_EMAU,
    RE_WORD_PREFIX_DINAMIC_POSTFIX_EMAU,
    SOLUTION_STUB_TEXT_DINAMIC_POSTFIX_EMAU,
    SPACE_CHAR_DINAMIC_POSTFIX_EMAU,
    TIP_SYNTAX_ERROR_DINAMIC_POSTFIX_EMAU,
)

from .completion_words import build_word_list
from .line_number_area import LineNumberArea
from .python_highlighter import PythonHighlighter
from .type_inference import (
    KnownTypeName,
    infer_symbol_types,
    python_type_method_map,
)

MONO_FONT_STYLE_HINT: QFont.StyleHint = QFont.StyleHint.Monospace

FONT_FAMILIES: tuple[str, ...] = (
    CODE_EDITOR_FONT_FAMILY_PRIMARY_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_FONT_FAMILY_SECONDARY_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_FONT_FAMILY_TERTIARY_DINAMIC_POSTFIX_EMAU,
    CODE_EDITOR_FONT_FAMILY_FALLBACK_DINAMIC_POSTFIX_EMAU,
)

FONT_SIZE_MIN: int = 8
FONT_SIZE_MAX: int = 22
TAB_SIZE_SPACES: int = 4
COMPLETER_MAX_VISIBLE_ITEMS: int = 14
WORD_COMPLETION_DELAY_MS: int = 40
SYNTAX_HIGHLIGHT_DELAY_MS: int = 380
LINE_NUMBER_WIDTH_PADDING: int = 8
LINE_NUMBER_WIDTH_MIN: int = 36
LINE_NUMBER_RIGHT_PADDING: int = 4
COMPLETION_RECT_TOP_OFFSET: int = 2
COMPLETION_RECT_MIN_WIDTH: int = 280
COMPLETION_RECT_EXTRA_WIDTH: int = 20
COLOR_SYNTAX_BG_R: int = 254
COLOR_SYNTAX_BG_G: int = 226
COLOR_SYNTAX_BG_B: int = 226
COLOR_SYNTAX_BG_A: int = 90

PAIR_MAP: dict[str, str] = {
    CODE_EDITOR_PAIR_PAREN_OPEN_DINAMIC_POSTFIX_EMAU: (
        CODE_EDITOR_PAIR_PAREN_CLOSE_DINAMIC_POSTFIX_EMAU
    ),
    CODE_EDITOR_PAIR_BRACKET_OPEN_DINAMIC_POSTFIX_EMAU: (
        CODE_EDITOR_PAIR_BRACKET_CLOSE_DINAMIC_POSTFIX_EMAU
    ),
    CODE_EDITOR_PAIR_BRACE_OPEN_DINAMIC_POSTFIX_EMAU: (
        CODE_EDITOR_PAIR_BRACE_CLOSE_DINAMIC_POSTFIX_EMAU
    ),
    CODE_EDITOR_PAIR_DOUBLE_QUOTE_DINAMIC_POSTFIX_EMAU: (
        CODE_EDITOR_PAIR_DOUBLE_QUOTE_DINAMIC_POSTFIX_EMAU
    ),
    CODE_EDITOR_PAIR_SINGLE_QUOTE_DINAMIC_POSTFIX_EMAU: (
        CODE_EDITOR_PAIR_SINGLE_QUOTE_DINAMIC_POSTFIX_EMAU
    ),
}
CLOSER_CHARS: frozenset[str] = frozenset(PAIR_MAP.values())


class CodeEditor(QPlainTextEdit):
    """
    Code editor with highlighting, optional gutter, and completion.
    """

    def __init__(
        self,
        font_size: int = 12,
        *,
        line_numbers: bool = True,
        light_theme: bool = False,
    ) -> None:
        """Create the editor with font, completer, and gutter options.

        Args:
            font_size: Initial font size in typographic points.
            line_numbers: When True, show and maintain a line-number
                strip.
            light_theme: When True, use light-theme gutter colors.
        """
        super().__init__()
        self.setObjectName(OBJECT_NAME_EDITOR_DINAMIC_POSTFIX_EMAU)
        self.setFrameShape(QPlainTextEdit.Shape.NoFrame)
        self._line_numbers: bool = line_numbers
        self._light_theme: bool = light_theme
        self._apply_line_number_theme(light_theme=light_theme)
        self.setPlaceholderText(PLACEHOLDER_TEXT_DINAMIC_POSTFIX_EMAU)
        self._apply_font(font_size=font_size)
        self.highlighter = PythonHighlighter(
            self.document(), dark=(not light_theme)
        )
        self._configure_tab_stops()
        self._completion_start_pos: int = -1
        self._in_member_completion: bool = False
        self._member_choice_list: list[str] = []
        self._install_completer()
        self._type_methods: dict[KnownTypeName, list[str]] = (
            python_type_method_map()
        )
        self._install_deferred_timers()
        self.textChanged.connect(self._on_text_changed)
        self._line_number_area = LineNumberArea(self)
        self._setup_line_number_gutter(show_line_numbers=line_numbers)

    def _apply_line_number_theme(self, *, light_theme: bool) -> None:
        """Store gutter colors for the current theme.

        Args:
            light_theme: Whether the light palette is active.
        """
        self._ln_bg: str = (
            LINE_NUMBER_BG_LIGHT_DINAMIC_POSTFIX_EMAU
            if light_theme
            else LINE_NUMBER_BG_DARK_DINAMIC_POSTFIX_EMAU
        )
        self._ln_fg: str = (
            LINE_NUMBER_FG_LIGHT_DINAMIC_POSTFIX_EMAU
            if light_theme
            else LINE_NUMBER_FG_DARK_DINAMIC_POSTFIX_EMAU
        )

    def _apply_font(self, *, font_size: int) -> None:
        """Apply monospace stack and clamped size to this widget.

        Args:
            font_size: Requested font size in points.
        """
        font = QFont()
        font.setFamilies(list(FONT_FAMILIES))
        font.setStyleHint(MONO_FONT_STYLE_HINT)
        clamped = max(FONT_SIZE_MIN, min(FONT_SIZE_MAX, font_size))
        font.setPointSize(clamped)
        self.setFont(font)

    def _configure_tab_stops(self) -> None:
        """Set tab-stop distance from space advance and tab width."""
        advance = self.fontMetrics().horizontalAdvance(
            SPACE_CHAR_DINAMIC_POSTFIX_EMAU
        )
        self.setTabStopDistance(advance * TAB_SIZE_SPACES)

    def _install_completer(self) -> None:
        """Create completer, popup styling, and event wiring."""
        completer = QCompleter(self)
        completer.setWidget(self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        completer.setModel(QStringListModel([], completer))
        completer.setMaxVisibleItems(COMPLETER_MAX_VISIBLE_ITEMS)
        completer.activated.connect(self._insert_completion)
        self._completer: QCompleter = completer
        popup = self._popup()
        if popup is not None:
            popup.setMouseTracking(True)
            popup.setObjectName(
                OBJECT_NAME_COMPLETER_POPUP_DINAMIC_POSTFIX_EMAU
            )
            popup.setStyleSheet(
                COMPLETER_POPUP_STYLESHEET_DINAMIC_POSTFIX_EMAU
            )
            popup.installEventFilter(self)
        self.installEventFilter(self)

    def _install_deferred_timers(self) -> None:
        """
        Attach single-shot timers for syntax check and word complete.
        """
        syn_timer = QTimer(self)
        syn_timer.setSingleShot(True)
        syn_timer.timeout.connect(self._refresh_syntax_error_highlight)
        self._syntax_error_timer: QTimer = syn_timer
        word_timer = QTimer(self)
        word_timer.setSingleShot(True)
        word_timer.timeout.connect(self._run_word_completion_if_applicable)
        self._word_complete_timer: QTimer = word_timer

    def _setup_line_number_gutter(self, *, show_line_numbers: bool) -> None:
        """Show gutter and connect geometry updates when enabled.

        Args:
            show_line_numbers: When True, pin the line strip beside
            text.
        """
        if not show_line_numbers:
            self._line_number_area.hide()
            return
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area_rect)
        self._update_line_number_area_width()
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def line_number_area_width(self) -> int:
        """Compute gutter width from digit count and font metrics.

        Returns:
            Pixel width reserved for line numbers.
        """
        digits = max(1, len(str(max(1, self.blockCount()))))
        sample_advance = self.fontMetrics().horizontalAdvance(
            DIGIT_SAMPLE_DINAMIC_POSTFIX_EMAU
        )
        calculated = LINE_NUMBER_WIDTH_PADDING + sample_advance * digits
        return max(LINE_NUMBER_WIDTH_MIN, calculated)

    def resizeEvent(self, e: QResizeEvent | None) -> None:
        """Keep the gutter aligned when the viewport size changes.

        Args:
            e: Resize event from Qt, or None in degenerate cases.
        """
        super().resizeEvent(e)
        if not self._line_numbers:
            return
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(
                cr.left(),
                cr.top(),
                self.line_number_area_width(),
                cr.height(),
            )
        )

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        """Paint line indices in the gutter widget.

        Args:
            event: Paint region for the gutter.
        """
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor(self._ln_bg))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())
        width = self._line_number_area.width()
        bottom_limit = event.rect().bottom()
        while block.isValid() and top <= bottom_limit:
            if block.isVisible() and bottom >= event.rect().top():
                line_text = str(block_number + 1)
                painter.setPen(QColor(self._ln_fg))
                painter.drawText(
                    0,
                    top,
                    width - LINE_NUMBER_RIGHT_PADDING,
                    self.fontMetrics().height(),
                    int(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter
                    ),
                    line_text,
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def _update_line_number_area_width(self, _new_count: int = 0) -> None:
        """
        Resize viewport margins and the gutter when digit count shifts.
        """
        if not self._line_numbers:
            return
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(
                cr.left(),
                cr.top(),
                self.line_number_area_width(),
                cr.height(),
            )
        )
        self._line_number_area.update()

    def _update_line_number_area_rect(self, rect: QRect, dy: int) -> None:
        """Scroll or repaint the gutter after document updates.

        Args:
            rect: Updated viewport rectangle from Qt.
            dy: Vertical delta for scrolling content.
        """
        if not self._line_numbers:
            return
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0,
                rect.y(),
                self._line_number_area.width(),
                rect.height(),
            )
        vp = self.viewport()
        if vp is not None and rect.contains(vp.rect()):
            self._update_line_number_area_width()

    def set_font_size(self, size: int) -> None:
        """Clamp and apply a new body font size in points.

        Args:
            size: Requested size in typographic points.
        """
        font = self.font()
        clamped = max(FONT_SIZE_MIN, min(FONT_SIZE_MAX, size))
        font.setPointSize(clamped)
        self.setFont(font)
        self._update_line_number_area_width()

    def set_light_theme(self, light: bool) -> None:
        """Switch gutter colors and Python highlighter theme.

        Args:
            light: When True, use light-theme palette.
        """
        self._light_theme = light
        self._apply_line_number_theme(light_theme=light)
        self.highlighter = PythonHighlighter(self.document(), dark=(not light))
        self.highlighter.rehighlight()
        self._line_number_area.update()

    def set_solution_stub(self) -> None:
        """Populate the buffer with the catalog solution stub text."""
        self.setPlainText(SOLUTION_STUB_TEXT_DINAMIC_POSTFIX_EMAU)

    def _on_text_changed(self) -> None:
        """Debounce syntax marking and word completion."""
        self._schedule_syntax_error_check()
        self._word_complete_timer.stop()
        self._word_complete_timer.start(WORD_COMPLETION_DELAY_MS)

    def _schedule_syntax_error_check(self) -> None:
        """Restart the delayed syntax-parse timer."""
        self._syntax_error_timer.start(SYNTAX_HIGHLIGHT_DELAY_MS)

    def _refresh_syntax_error_highlight(self) -> None:
        """
        Parse the buffer and refresh syntax error decoration state.
        """
        text = self.toPlainText()
        if not text.strip():
            self._clear_syntax_error_state()
            return
        try:
            ast.parse(text)
        except SyntaxError as exc:
            self._apply_syntax_error_selection(exc=exc)
        except (MemoryError, RecursionError):
            self._clear_syntax_error_state()
        else:
            self._clear_syntax_error_state()

    def _clear_syntax_error_state(self) -> None:
        """Drop extra selections and clear tooltip text."""
        self.setExtraSelections([])
        self.setToolTip(EMPTY_STRING_DINAMIC_POSTFIX_TGHG)

    def _syntax_error_format(self) -> QTextCharFormat:
        """Build underline and background for a bad syntax range."""
        fmt = QTextCharFormat()
        fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
        fmt.setUnderlineColor(
            QColor(COLOR_SYNTAX_UNDERLINE_DINAMIC_POSTFIX_EMAU)
        )
        fmt.setBackground(
            QColor(
                COLOR_SYNTAX_BG_R,
                COLOR_SYNTAX_BG_G,
                COLOR_SYNTAX_BG_B,
                COLOR_SYNTAX_BG_A,
            )
        )
        return fmt

    def _syntax_error_tooltip_text(self, exc: SyntaxError) -> str:
        """Compose tooltip lines from a ``SyntaxError`` instance.

        Args:
            exc: Exception raised by ``ast.parse``.
        """
        tip = (exc.msg or str(exc)).strip()
        if exc.text:
            cleaned = exc.text.strip()
            tip = f"{tip}\n{cleaned}" if tip else cleaned
        return tip or TIP_SYNTAX_ERROR_DINAMIC_POSTFIX_EMAU

    def _apply_syntax_error_selection(self, *, exc: SyntaxError) -> None:
        """Select the error line and surface a tooltip.

        Args:
            exc: Syntax error describing the failure location.
        """
        doc = self.document()
        if doc is None or exc.lineno is None or exc.lineno < 1:
            self._clear_syntax_error_state()
            return
        block = doc.findBlockByNumber(exc.lineno - 1)
        if not block.isValid():
            self._clear_syntax_error_state()
            return
        cur = QTextCursor(block)
        cur.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cur.movePosition(
            QTextCursor.MoveOperation.EndOfBlock,
            QTextCursor.MoveMode.KeepAnchor,
        )
        sel = QTextEdit.ExtraSelection()
        sel.cursor = cur
        sel.format = self._syntax_error_format()
        self.setExtraSelections([sel])
        self.setToolTip(self._syntax_error_tooltip_text(exc=exc))

    def _completion_rect(self) -> QRect:
        """Rectangle placed beneath the cursor for the popup."""
        rect = self.cursorRect()
        line_height = self.fontMetrics().height()
        rect.moveTop(rect.top() + line_height + COMPLETION_RECT_TOP_OFFSET)
        popup = self._popup()
        if popup is None:
            return rect
        scrollbar = popup.verticalScrollBar()
        sw = scrollbar.sizeHint().width() if scrollbar else 0
        width = max(
            COMPLETION_RECT_MIN_WIDTH,
            popup.sizeHintForColumn(0) + sw + COMPLETION_RECT_EXTRA_WIDTH,
        )
        rect.setWidth(width)
        return rect

    def _close_completion(self) -> None:
        """Hide popup and clear stored completion context."""
        popup = self._popup()
        if popup is not None:
            popup.hide()
        self._completion_start_pos = -1
        self._in_member_completion = False
        self._member_choice_list = []

    def _member_prefix_at_cursor(self) -> tuple[int, str] | None:
        """Return prefix span and text for member completion, if any."""
        cur = self.textCursor()
        pos = cur.position()
        block = cur.block()
        rel = pos - block.position()
        left = block.text()[:rel]
        known = infer_symbol_types(self.toPlainText())
        dot = re.search(RE_MEMBER_DOT_DINAMIC_POSTFIX_EMAU, left)
        if dot and known.get(dot.group(1)):
            return (pos, "")
        partial = re.search(RE_MEMBER_PARTIAL_DINAMIC_POSTFIX_EMAU, left)
        if partial and known.get(partial.group(1)):
            ptxt = partial.group(2)
            return (pos - len(ptxt), ptxt)
        return None

    def _run_word_completion_if_applicable(self) -> None:
        """Run deferred completion when focus and selection allow it."""
        if not self.hasFocus():
            return
        cur = self.textCursor()
        if cur.hasSelection():
            self._close_completion()
            return
        if self._update_member_completion():
            return
        self._update_global_completion(cur=cur)

    def _update_member_completion(self) -> bool:
        """Refresh member-mode completion when still active.

        Returns:
            True when member completion consumed the update.
        """
        if not self._in_member_completion:
            return False
        mem = self._member_prefix_at_cursor()
        if mem is None or not self._member_choice_list:
            self._close_completion()
            return False
        self._completion_start_pos, pref = mem
        self._set_completion_candidates(words=self._member_choice_list)
        self._completer.setCompletionPrefix(pref)
        self._show_completion_if_any()
        return True

    def _set_completion_candidates(self, *, words: list[str]) -> None:
        """Push a new candidate list into the string model.

        Args:
            words: Completion strings shown in the popup.
        """
        model = self._completer.model()
        if isinstance(model, QStringListModel):
            model.setStringList(words)

    def _show_completion_if_any(self) -> None:
        """Open the completer when matches exist, else hide it."""
        if self._completer.completionCount() > 0:
            self._completer.complete(self._completion_rect())
            return
        self._close_completion()

    def _set_completion_context(
        self,
        *,
        start_pos: int,
        member: bool,
        member_words: list[str] | None = None,
    ) -> None:
        """Persist state used while navigating completions.

        Args:
            start_pos: Document offset where the prefix begins.
            member: True when completing after an attribute access.
            member_words: Member candidates when ``member`` is True.
        """
        self._completion_start_pos = start_pos
        self._in_member_completion = member
        self._member_choice_list = (
            member_words if member and member_words is not None else []
        )

    def _update_global_completion(self, *, cur: QTextCursor) -> None:
        # sourcery skip: class-extract-method
        """Match identifier prefix and show global word completions."""
        block = cur.block()
        rel = cur.position() - block.position()
        left = block.text()[:rel]
        wm = re.search(RE_WORD_PREFIX_DINAMIC_POSTFIX_EMAU, left)
        popup = self._popup()
        if wm is None:
            if (
                popup is not None
                and popup.isVisible()
                and (not self._in_member_completion)
            ):
                self._close_completion()
            return
        prefix = wm.group(1)
        if not prefix:
            return
        start = cur.position() - len(prefix)
        words = build_word_list(self.toPlainText())
        self._set_completion_candidates(words=words)
        self._set_completion_context(start_pos=start, member=False)
        self._completer.setCompletionPrefix(prefix)
        if self._completer.completionCount() == 0:
            self._close_completion()
            return
        if self._is_single_exact_completion(prefix=prefix):
            self._close_completion()
            return
        self._show_completion_if_any()

    def _is_single_exact_completion(self, *, prefix: str) -> bool:
        """Return whether the model has one row equal to the prefix.

        Args:
            prefix: Current typed prefix text.
        """
        model = self._completer.completionModel()
        if model is None or model.rowCount() != 1:
            return False
        index = model.index(0, 0)
        first = str(model.data(index) or "")
        return first == prefix

    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        """Route keys through pairing, completion, and default editing.

        Args:
            e: Qt key event forwarded from the text edit.
        """
        if e is None:
            return
        handled = self._handle_pre_key_event(e=e)
        text = e.text()
        if not handled:
            mods = e.modifiers()
            if mods & (
                Qt.KeyboardModifier.ControlModifier
                | Qt.KeyboardModifier.AltModifier
                | Qt.KeyboardModifier.MetaModifier
            ):
                super().keyPressEvent(e)
                return
            if self._handle_pair_insertion(text=text):
                handled = True
            elif self._handle_closer_skip(text=text):
                handled = True
        if handled:
            return
        super().keyPressEvent(e)
        if text == MEMBER_TRIGGER_CHAR_DINAMIC_POSTFIX_EMAU:
            self._trigger_member_completion()
        else:
            self._update_completion_after_typing(e=e, text=text)

    def _handle_completion_navigation(self, *, e: QKeyEvent) -> bool:
        """Forward navigation keys to the popup or accept a choice.

        Args:
            e: Key event while completion may be visible.

        Returns:
            True if this handler consumed the event.
        """
        popup = self._popup()
        if popup is None or not popup.isVisible():
            return False
        key = e.key()
        if key in (
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_PageUp,
            Qt.Key.Key_PageDown,
        ):
            popup.event(e)
            return True
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
            idx = popup.currentIndex()
            if idx.isValid():
                completion = idx.data()
                if isinstance(completion, str):
                    self._insert_completion(completion)
            self._close_completion()
            return True
        return False

    def _handle_pair_insertion(self, *, text: str) -> bool:
        """Wrap selection or insert paired opener and closer tokens.

        Args:
            text: Single character typed by the user.
        """
        if text not in PAIR_MAP:
            return False
        cur = self.textCursor()
        closer = PAIR_MAP[text]
        if cur.hasSelection():
            selected = cur.selectedText().replace(
                PARAGRAPH_SEPARATOR_DINAMIC_POSTFIX_EMAU,
                NEWLINE_CHAR_DINAMIC_POSTFIX_EMAU,
            )
            cur.insertText(f"{text}{selected}{closer}")
            return True
        cur.insertText(f"{text}{closer}")
        cur.movePosition(cur.MoveOperation.Left)
        self.setTextCursor(cur)
        return True

    def _handle_closer_skip(self, *, text: str) -> bool:
        """Skip typing when the next char already matches the closer.

        Args:
            text: Single character from the key event.
        """
        if text not in CLOSER_CHARS:
            return False
        cur = self.textCursor()
        if cur.hasSelection():
            return False
        doc = self.document()
        pos = cur.position()
        next_char = EMPTY_STRING_DINAMIC_POSTFIX_TGHG
        if doc is not None and pos < doc.characterCount() - 1:
            next_char = doc.characterAt(pos)
        if next_char != text:
            return False
        cur.movePosition(cur.MoveOperation.Right)
        self.setTextCursor(cur)
        return True

    def _update_completion_after_typing(
        self, *, e: QKeyEvent, text: str
    ) -> None:
        """Update or close completion after edits inside the prefix.

        Args:
            e: Key event after default handling ran.
            text: Text payload from ``e``.
        """
        popup = self._popup()
        if (
            popup is None
            or not popup.isVisible()
            or self._completion_start_pos < 0
        ):
            return
        if e.key() == Qt.Key.Key_Backspace:
            cur = self.textCursor()
            if cur.position() < self._completion_start_pos:
                self._close_completion()
                return
            self._update_completion_prefix()
            if self._completer.completionCount() == 0:
                self._close_completion()
            return
        if text and (text.isalnum() or text == "_"):
            self._update_completion_prefix()
            if self._completer.completionCount() == 0:
                self._close_completion()

    def eventFilter(
        self,
        a0: QObject | None,
        a1: QEvent | None,
    ) -> bool:
        """Hide completion when clicking outside the popup."""
        popup = self._popup()
        if (
            popup is not None
            and popup.isVisible()
            and (a1 is not None)
            and (a1.type() == QEvent.Type.MouseButtonPress)
        ):
            if a0 is self and isinstance(a1, QMouseEvent):
                global_point = a1.globalPosition().toPoint()
                if not popup.geometry().contains(global_point):
                    popup.hide()
            elif a0 is popup:
                return False
        return super().eventFilter(a0, a1)

    def _handle_pre_key_event(self, *, e: QKeyEvent) -> bool:
        """Handle escape, completion navigation, or manual trigger.

        Args:
            e: Key event before default text processing.
        """
        popup = self._popup()
        if (
            popup is not None
            and e.key() == Qt.Key.Key_Escape
            and popup.isVisible()
        ):
            self._close_completion()
            return True
        if self._handle_completion_navigation(e=e):
            return True
        if self._is_manual_completion_shortcut(e=e):
            self._trigger_global_completion()
            return True
        return False

    def _is_manual_completion_shortcut(self, *, e: QKeyEvent) -> bool:
        """Detect Ctrl+Space manual completion requests."""
        return e.key() == Qt.Key.Key_Space and bool(
            e.modifiers() & Qt.KeyboardModifier.ControlModifier
        )

    def _trigger_member_completion(self) -> None:
        """Populate method completions after a dotted name if known."""
        cur = self.textCursor()
        block = cur.block()
        rel_pos = cur.position() - block.position()
        left = block.text()[:rel_pos]
        match = re.search(RE_MEMBER_DOT_DINAMIC_POSTFIX_EMAU, left)
        if match is None:
            return
        var_name = match.group(1)
        types = infer_symbol_types(self.toPlainText())
        resolved = types.get(var_name)
        if resolved is None:
            return
        methods = list(self._type_methods.get(resolved, ()))
        self._member_choice_list = methods
        self._show_completion_popup(
            words=methods,
            start_pos=cur.position(),
            member=True,
        )

    def _trigger_global_completion(self) -> None:
        """Show completions for the identifier prefix at the cursor."""
        cur = self.textCursor()
        block = cur.block()
        rel_pos = cur.position() - block.position()
        left = block.text()[:rel_pos]
        match = re.search(RE_WORD_PREFIX_DINAMIC_POSTFIX_EMAU, left)
        prefix = match.group(1) if match else EMPTY_STRING_DINAMIC_POSTFIX_TGHG
        start_pos = cur.position() - len(prefix)
        self._show_completion_popup(
            words=build_word_list(self.toPlainText()),
            start_pos=start_pos,
            member=False,
        )

    def _show_completion_popup(
        self,
        words: list[str] | tuple[str, ...],
        *,
        start_pos: int,
        member: bool = False,
    ) -> None:
        """
        Show ``words`` as completion candidates from ``start_pos``.
        """
        if not words:
            return
        words_list = list(words)
        self._set_completion_candidates(words=words_list)
        self._set_completion_context(
            start_pos=start_pos,
            member=member,
            member_words=words_list,
        )
        self._update_completion_prefix()
        self._completer.complete(self._completion_rect())

    def _update_completion_prefix(self) -> None:
        """Sync the completer prefix with text after ``start_pos``."""
        if self._completion_start_pos < 0:
            return
        cur = self.textCursor()
        end = cur.position()
        if end < self._completion_start_pos:
            popup = self._popup()
            if popup is not None:
                popup.hide()
            return
        chunk = self.toPlainText()[self._completion_start_pos : end]
        self._completer.setCompletionPrefix(chunk)
        popup = self._popup()
        model = self._completer.completionModel()
        if popup is not None and model is not None:
            popup.setCurrentIndex(model.index(0, 0))

    def _insert_completion(self, completion: str) -> None:
        """Replace the active prefix span with the chosen completion.

        Args:
            completion: String chosen from the popup.
        """
        if self._completion_start_pos < 0:
            return
        cur = self.textCursor()
        end = cur.position()
        cur.setPosition(self._completion_start_pos)
        cur.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cur.insertText(completion)
        self.setTextCursor(cur)
        self._close_completion()

    def _popup(self) -> QAbstractItemView | None:
        """
        Return the completer popup view when the backend exposes it.
        """
        return self._completer.popup()
