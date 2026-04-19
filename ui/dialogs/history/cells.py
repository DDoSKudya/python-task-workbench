"""
This module formats the display text for task cells in a history table,
combining a normalized title and pack label into a compact two-line
string.

It works by sanitizing and truncating task titles from HistoryRowView
objects and then interpolating them, along with a human-readable pack
label, into a template from the message catalog.

It defines constants for maximum title length and truncated length, plus
an ellipsis token and fallback “untitled” label via the messages
module.

The helper _normalized_title strips whitespace, replaces missing or
empty titles with a default label, and _truncate_title enforces the
length limit by appending an ellipsis when necessary.

The main task_cell_text function applies these helpers to a
HistoryRowView instance, resolves the pack label via pack_label, and
returns the final formatted cell text for use by the UI layer.
"""

from __future__ import annotations

from core.check_history import HistoryRowView
from messages import (
    TASK_CELL_TEMPLATE_DINAMIC_POSTFIX_10HF,
    TITLE_ELLIPSIS_DINAMIC_POSTFIX_10HF,
    UNTITLED_TASK_LABEL_DINAMIC_POSTFIX_10HF,
)

from ..common import pack_label

TITLE_MAX_LENGTH: int = 110
TITLE_TRUNCATED_LENGTH: int = 107


def _normalized_title(raw_title: str | None) -> str:
    """Normalize title with fallback for empty or missing values.

    Args:
        raw_title: Raw title from history row view.

    Returns:
        Non-empty normalized title.
    """
    title: str = (
        raw_title.strip()
        if isinstance(raw_title, str)
        else UNTITLED_TASK_LABEL_DINAMIC_POSTFIX_10HF
    )
    return title or UNTITLED_TASK_LABEL_DINAMIC_POSTFIX_10HF


def _truncate_title(title: str) -> str:
    """Truncate task title for compact history cell rendering.

    Args:
        title: Candidate title text.

    Returns:
        Original title when short enough, otherwise truncated text
        with ellipsis suffix.
    """
    if len(title) <= TITLE_MAX_LENGTH:
        return title
    return (
        f"{title[:TITLE_TRUNCATED_LENGTH]}"
        f"{TITLE_ELLIPSIS_DINAMIC_POSTFIX_10HF}"
    )


def task_cell_text(r: HistoryRowView) -> str:
    """Build display text for task cell in history table.

    Args:
        r: History row view model.

    Returns:
        Two-line text with task title and pack metadata.
    """
    title: str = _truncate_title(_normalized_title(r.task_title))
    return TASK_CELL_TEMPLATE_DINAMIC_POSTFIX_10HF.format(
        title=title,
        pack=pack_label(r.pack_name),
    )
