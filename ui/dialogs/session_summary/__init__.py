"""Public exports for session summary dialog package.

Exports:
    SessionSummaryDialog: Dialog widget with session summary details.
    SessionSummaryTaskRow: Structured row model for summary table.
"""

from __future__ import annotations

from .dialog import SessionSummaryDialog as SessionSummaryDialog
from .models import SessionSummaryTaskRow as SessionSummaryTaskRow

__all__: tuple[str, ...] = (
    "SessionSummaryDialog",
    "SessionSummaryTaskRow",
)
