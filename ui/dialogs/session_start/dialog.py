"""
This module implements a modal Qt dialog (SessionStartDialog) for
configuring which task packs to use and how many tasks to include
before starting a session.

It works by presenting a scrollable UI with a multi-select list of
available packs, form fields for session count and optional seed, and a
“Start” button that becomes enabled only when at least one pack is
selected.

It defines a set of layout and sizing constants (dialog dimensions,
margins, spacing, list heights, spin-box range, etc.) and uses
message-driven labels and object names for styling and localization.

The constructor wires up core widgets (pack list, count spin-box, seed
edit, labels, start button), builds the UI via _build_ui, applies an
initial SessionConfig template, and connects pack-selection signals to
_update_start_enabled to control the button state.

The _build_pack_section method populates the pack list by calling
list_available_pack_labels, displaying localized labels and storing
pack IDs in UserRole for later retrieval.

The _build_form_section method sets up a QFormLayout with a count
QSpinBox and a seed QLineEdit, using _mk_plbl to create styled labels
and applying sensible ranges and size policies.

_apply_template clears the current selection, re-selects packs from the
provided template, sets the count, and initializes the seed field based
on SessionConfig.seed.

_selected_pack_ids walks over selected items, extracting their stored
pack IDs into a tuple suitable for passing to the core configuration
model.

The key method build_full_config reads the selected pack IDs, count, and
seed from the UI, validates that at least one pack is selected, and
constructs a full SessionConfig including external parameters like
per_task_minutes, strict_types, and check_timeout_sec.

Within the broader application, this dialog is the entry point for the
user to define a new practice session, bridging between UI choices and
the generators session configuration model.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.models import CheckerEntryMode, SessionConfig
from messages import (
    ERROR_PACK_REQUIRED_DINAMIC_POSTFIX_I30N,
    HEADER_TITLE_DINAMIC_POSTFIX_I30N,
    LABEL_COUNT_DINAMIC_POSTFIX_I30N,
    LABEL_PACKS_DINAMIC_POSTFIX_I30N,
    LABEL_SEED_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_BODY_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_DIALOG_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_DIVIDER_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_FIELD_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_FIELD_LABEL_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_FOOTER_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_HEADER_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_HINT_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_LABEL_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_PACK_SELECT_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_SCROLL_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_SCROLL_VIEWPORT_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_SPIN_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_START_BUTTON_DINAMIC_POSTFIX_I30N,
    OBJECT_NAME_TITLE_DINAMIC_POSTFIX_I30N,
    PACKS_HINT_DINAMIC_POSTFIX_I30N,
    PLACEHOLDER_SEED_DINAMIC_POSTFIX_I30N,
    START_BUTTON_TEXT_DINAMIC_POSTFIX_I30N,
    WINDOW_TITLE_DINAMIC_POSTFIX_I30N,
)
from task_packs import list_available_pack_labels

from ..common import pack_label

DEFAULT_DIALOG_WIDTH: int = 560
DEFAULT_DIALOG_HEIGHT: int = 520
MIN_DIALOG_WIDTH: int = 440
ROOT_MARGIN: int = 0
ROOT_SPACING: int = 0
HEADER_LEFT_MARGIN: int = 24
HEADER_RIGHT_MARGIN: int = 20
BODY_LEFT_MARGIN: int = 20
BODY_RIGHT_MARGIN: int = 20
BODY_TOP_MARGIN: int = 14
BODY_BOTTOM_MARGIN: int = 12
BODY_SPACING: int = 10
FORM_SPACING: int = 8
FORM_TOP_MARGIN: int = 2
FORM_HORIZONTAL_SPACING: int = 10
FORM_VERTICAL_SPACING: int = 6
PACK_LIST_MIN_HEIGHT: int = 160
PACK_LIST_MAX_HEIGHT: int = 260
FIELD_MIN_WIDTH: int = 160
FOOTER_TOP_BOTTOM_MARGIN: int = 14
FOOTER_SPACING: int = 10
START_BUTTON_MIN_HEIGHT: int = 44
START_BUTTON_MIN_WIDTH: int = 240
DEFAULT_SPIN_COUNT_MIN: int = 1
DEFAULT_SPIN_COUNT_MAX: int = 80
UNSELECTED_ROW_INDEX: int = -1
LAYOUT_STRETCH: int = 1


class SessionStartDialog(QDialog):
    """Configure packs and session size before starting."""

    def __init__(
        self, parent: QWidget | None, template: SessionConfig
    ) -> None:
        """Initialize session-start dialog and apply template.

        Args:
            parent: Optional parent widget.
            template: Initial configuration template.

        """
        super().__init__(parent)
        self._configure_window()
        self._checker_entry_mode: CheckerEntryMode = (
            template.checker_entry_mode
        )
        self._pack_list: QListWidget = QListWidget()
        self._spin_count: QSpinBox = QSpinBox()
        self._edit_seed: QLineEdit = QLineEdit()
        self._lbl_count: QLabel = QLabel()
        self._lbl_seed: QLabel = QLabel()
        self._start_button: QPushButton = QPushButton(
            START_BUTTON_TEXT_DINAMIC_POSTFIX_I30N
        )
        self._configure_start_button()
        self._build_ui()
        self._apply_template(template)
        self._pack_list.itemSelectionChanged.connect(
            self._update_start_enabled
        )
        sm = self._pack_list.selectionModel()
        if sm is not None:
            sm.selectionChanged.connect(self._update_start_enabled)
        self._update_start_enabled()

    def _configure_window(self) -> None:
        """Configure dialog-level visual and modal properties."""
        self.setObjectName(OBJECT_NAME_DIALOG_DINAMIC_POSTFIX_I30N)
        self.setWindowTitle(WINDOW_TITLE_DINAMIC_POSTFIX_I30N)
        self.setModal(True)
        self.resize(DEFAULT_DIALOG_WIDTH, DEFAULT_DIALOG_HEIGHT)
        self.setMinimumWidth(MIN_DIALOG_WIDTH)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def _configure_start_button(self) -> None:
        """Configure the primary start button state and style."""
        self._start_button.setEnabled(False)
        self._start_button.setObjectName(
            OBJECT_NAME_START_BUTTON_DINAMIC_POSTFIX_I30N
        )
        self._start_button.setMinimumHeight(START_BUTTON_MIN_HEIGHT)
        self._start_button.setMinimumWidth(START_BUTTON_MIN_WIDTH)
        self._start_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_button.clicked.connect(self.accept)

    def _build_ui(self) -> None:
        """Build full dialog widget tree."""
        root: QVBoxLayout = QVBoxLayout(self)
        root.setContentsMargins(
            ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN
        )
        root.setSpacing(ROOT_SPACING)
        root.addWidget(self._build_header())
        root.addWidget(self._build_divider())
        root.addWidget(self._build_scroll_body(), LAYOUT_STRETCH)
        root.addWidget(self._build_footer())

    def _build_header(self) -> QFrame:
        """Build header bar frame.

        Returns:
            Configured header frame.
        """
        header: QFrame = QFrame()
        header.setObjectName(OBJECT_NAME_HEADER_DINAMIC_POSTFIX_I30N)
        layout: QHBoxLayout = QHBoxLayout(header)
        layout.setContentsMargins(
            HEADER_LEFT_MARGIN, ROOT_MARGIN, HEADER_RIGHT_MARGIN, ROOT_MARGIN
        )
        title_label: QLabel = QLabel(HEADER_TITLE_DINAMIC_POSTFIX_I30N)
        title_label.setObjectName(OBJECT_NAME_TITLE_DINAMIC_POSTFIX_I30N)
        layout.addWidget(
            title_label,
            LAYOUT_STRETCH,
            Qt.AlignmentFlag.AlignVCenter,
        )
        return header

    def _build_divider(self) -> QFrame:
        """Build divider frame below header.

        Returns:
            Divider frame.
        """
        divider: QFrame = QFrame()
        divider.setObjectName(OBJECT_NAME_DIVIDER_DINAMIC_POSTFIX_I30N)
        return divider

    def _build_scroll_body(self) -> QScrollArea:
        """Build scrollable body area with controls.

        Returns:
            Configured scroll area.
        """
        inner: QWidget = QWidget()
        inner.setObjectName(OBJECT_NAME_BODY_DINAMIC_POSTFIX_I30N)
        body: QVBoxLayout = QVBoxLayout(inner)
        body.setContentsMargins(
            BODY_LEFT_MARGIN,
            BODY_TOP_MARGIN,
            BODY_RIGHT_MARGIN,
            BODY_BOTTOM_MARGIN,
        )
        body.setSpacing(BODY_SPACING)
        body.addLayout(self._build_pack_section())
        body.addLayout(self._build_form_section())
        scroll: QScrollArea = QScrollArea()
        scroll.setObjectName(OBJECT_NAME_SCROLL_DINAMIC_POSTFIX_I30N)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        viewport = scroll.viewport()
        if viewport is not None:
            viewport.setObjectName(
                OBJECT_NAME_SCROLL_VIEWPORT_DINAMIC_POSTFIX_I30N
            )
            viewport.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        scroll.setWidget(inner)
        return scroll

    def _build_pack_section(self) -> QVBoxLayout:
        """Build packs selection controls.

        Returns:
            Layout containing packs controls.
        """
        layout: QVBoxLayout = QVBoxLayout()
        layout.setContentsMargins(
            ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN, ROOT_MARGIN
        )
        layout.setSpacing(BODY_SPACING)
        packs_label: QLabel = QLabel(LABEL_PACKS_DINAMIC_POSTFIX_I30N)
        packs_label.setObjectName(OBJECT_NAME_LABEL_DINAMIC_POSTFIX_I30N)
        packs_hint: QLabel = QLabel(PACKS_HINT_DINAMIC_POSTFIX_I30N)
        packs_hint.setObjectName(OBJECT_NAME_HINT_DINAMIC_POSTFIX_I30N)
        self._pack_list.setObjectName(
            OBJECT_NAME_PACK_SELECT_DINAMIC_POSTFIX_I30N
        )
        self._pack_list.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self._pack_list.setUniformItemSizes(True)
        self._pack_list.setAlternatingRowColors(False)
        self._pack_list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._pack_list.setMinimumHeight(PACK_LIST_MIN_HEIGHT)
        self._pack_list.setMaximumHeight(PACK_LIST_MAX_HEIGHT)
        for pack in list_available_pack_labels():
            item: QListWidgetItem = QListWidgetItem(pack_label(pack.pack_id))
            item.setData(Qt.ItemDataRole.UserRole, pack.pack_id)
            self._pack_list.addItem(item)
        layout.addWidget(packs_label)
        layout.addWidget(packs_hint)
        layout.addWidget(self._pack_list)
        return layout

    def _build_form_section(self) -> QFormLayout:
        """Build parameters form controls.

        Returns:
            Configured form layout.
        """
        frm: QFormLayout = QFormLayout()
        frm.setSpacing(FORM_SPACING)
        frm.setContentsMargins(
            ROOT_MARGIN, FORM_TOP_MARGIN, ROOT_MARGIN, ROOT_MARGIN
        )
        frm.setHorizontalSpacing(FORM_HORIZONTAL_SPACING)
        frm.setVerticalSpacing(FORM_VERTICAL_SPACING)
        frm.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        frm.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        frm.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self._spin_count.setObjectName(OBJECT_NAME_SPIN_DINAMIC_POSTFIX_I30N)
        self._spin_count.setRange(
            DEFAULT_SPIN_COUNT_MIN, DEFAULT_SPIN_COUNT_MAX
        )
        self._spin_count.setMinimumWidth(FIELD_MIN_WIDTH)
        self._spin_count.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._edit_seed.setObjectName(OBJECT_NAME_FIELD_DINAMIC_POSTFIX_I30N)
        self._edit_seed.setPlaceholderText(
            PLACEHOLDER_SEED_DINAMIC_POSTFIX_I30N
        )
        self._edit_seed.setMinimumWidth(FIELD_MIN_WIDTH)
        self._edit_seed.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._lbl_count = self._mk_plbl(LABEL_COUNT_DINAMIC_POSTFIX_I30N)
        self._lbl_seed = self._mk_plbl(LABEL_SEED_DINAMIC_POSTFIX_I30N)
        frm.addRow(self._lbl_count, self._spin_count)
        frm.addRow(self._lbl_seed, self._edit_seed)
        return frm

    def _build_footer(self) -> QFrame:
        """Build dialog footer with start button.

        Returns:
            Footer frame.
        """
        foot: QFrame = QFrame()
        foot.setObjectName(OBJECT_NAME_FOOTER_DINAMIC_POSTFIX_I30N)
        layout: QHBoxLayout = QHBoxLayout(foot)
        layout.setContentsMargins(
            BODY_LEFT_MARGIN,
            FOOTER_TOP_BOTTOM_MARGIN,
            BODY_RIGHT_MARGIN,
            FOOTER_TOP_BOTTOM_MARGIN,
        )
        layout.setSpacing(FOOTER_SPACING)
        layout.addWidget(self._start_button, LAYOUT_STRETCH)
        return foot

    def _mk_plbl(self, text: str) -> QLabel:
        """Create styled form field label.

        Args:
            text: Label text.

        Returns:
            Configured label widget.
        """
        label: QLabel = QLabel(text)
        label.setObjectName(OBJECT_NAME_FIELD_LABEL_DINAMIC_POSTFIX_I30N)
        label.setWordWrap(True)
        return label

    def _apply_template(self, s: SessionConfig) -> None:
        """Apply template values to dialog controls.

        Args:
            s: Session configuration template.

        """
        self._pack_list.clearSelection()
        self._pack_list.setCurrentRow(UNSELECTED_ROW_INDEX)
        selected: set[str] = set(s.selected_packs)
        for i in range(self._pack_list.count()):
            item: QListWidgetItem | None = self._pack_list.item(i)
            if item is None:
                continue
            pack_name: object = item.data(Qt.ItemDataRole.UserRole)
            item.setSelected(pack_name in selected)
        self._spin_count.setValue(s.count)
        if s.seed is not None:
            self._edit_seed.setText(str(s.seed))
        else:
            self._edit_seed.clear()

    def _update_start_enabled(self) -> None:
        """Enable Start when a content pack is selected."""
        has_catalog: bool = self._pack_list.count() > 0
        sm = self._pack_list.selectionModel()
        has_selection: bool = sm.hasSelection() if sm is not None else False
        self._start_button.setEnabled(has_catalog and has_selection)

    def build_full_config(
        self,
        *,
        per_task_minutes: int,
        strict_types: bool,
        check_timeout_sec: int,
    ) -> SessionConfig:
        """Build full session configuration from UI values.

        Args:
            per_task_minutes: Time limit per task.
            strict_types: Whether strict typing checks are enabled.
            check_timeout_sec: Solution check timeout in seconds.

        Returns:
            Fully built session configuration.

        Raises:
            ValueError: If required fields are invalid.
        """
        packs: tuple[str, ...] = self._selected_pack_ids()
        if not packs:
            raise ValueError(ERROR_PACK_REQUIRED_DINAMIC_POSTFIX_I30N)
        seed_text: str = self._edit_seed.text().strip()
        seed: int | None = int(seed_text) if seed_text else None
        return SessionConfig(
            selected_packs=packs,
            count=self._spin_count.value(),
            seed=seed,
            strict_types=strict_types,
            checker_entry_mode=self._checker_entry_mode,
            check_timeout_sec=check_timeout_sec,
            per_task_minutes=per_task_minutes,
        )

    def _selected_pack_ids(self) -> tuple[str, ...]:
        """Return selected pack identifiers from the list widget.

        Returns:
            Tuple of selected pack identifiers.
        """
        pack_ids: list[str] = []
        for item in self._pack_list.selectedItems():
            raw_pack_id: object = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(raw_pack_id, str):
                pack_ids.append(raw_pack_id)
        return tuple(pack_ids)
