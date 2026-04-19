"""Data models for the session summary task list.

Task status literals match ``STATUS_*_DINAMIC_POSTFIX_UWJS`` in
``messages``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

type TaskStatus = Literal["ok", "bad", "checking", "pending"]


@dataclass(frozen=True, slots=True)
class SessionSummaryTaskRow:
    """Immutable row model for one task line in the session summary.

    Attributes:
        num: One-based index of the task in the session.
        status: Checker outcome or progress tag for this task.
        title: Title string shown in the summary list.
        report_text: Optional checker report body for detail view.
        code_text: Optional submitted solution source for detail view.
    """

    num: int
    status: TaskStatus
    title: str
    report_text: str | None = None
    code_text: str | None = None
