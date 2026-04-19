"""Expose public dialog-layer widgets and helpers."""

from __future__ import annotations

from .detail_text import DetailTextDialog, normalize_code_for_view
from .history import HistoryDialog
from .session_start import SessionStartDialog
from .session_summary import SessionSummaryDialog, SessionSummaryTaskRow

__all__: tuple[str, ...] = (
    "DetailTextDialog",
    "HistoryDialog",
    "SessionStartDialog",
    "SessionSummaryDialog",
    "SessionSummaryTaskRow",
    "normalize_code_for_view",
)
