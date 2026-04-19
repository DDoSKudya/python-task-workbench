"""
This module generates concise, user-facing summary text for the result
of running a task check, including optional previews of actual outputs.

It works by examining a TaskStates status and attached result, then
building either a success message with an optional actual-result
fragment or a failure message composed from error text and actual
output, returning nothing for pending or in-progress tasks.

It defines constants controlling preview length (PREVIEW_CHAR_LIMIT,
_TRUNCATION_SUFFIX_CHAR_LEN, PREVIEW_TRUNCATE_HEAD_CHARS) and a set of
“pending” statuses (PENDING_STATE_STATUSES) derived from message-catalog
tokens.

The helper summary_preview_repr returns a possibly truncated repr(value)
with a catalog-defined truncation suffix, while _report_text_for_passed
and _report_text_for_failed assemble success or failure report bodies
using catalog message templates and optional previews.

The main function summary_report_for_state routes on TaskState.status to
either call the passed/failed helpers or return None for
pending/checking, and is used elsewhere in the system to populate
per-task rows in session summary views.
"""

from __future__ import annotations

from typing import Final

from core.models import TaskState
from messages import (
    NEWLINE_DINAMIC_POSTFIX_QLLY,
    STATUS_CHECKING_DINAMIC_POSTFIX_TGHG,
    STATUS_FAILED_DINAMIC_POSTFIX_TGHG,
    STATUS_PASSED_DINAMIC_POSTFIX_TGHG,
    STATUS_PENDING_DINAMIC_POSTFIX_TGHG,
    SUMMARY_REPORT_ACTUAL_FRAGMENT_HEADER_DINAMIC_POSTFIX_QLLY,
    SUMMARY_REPORT_CHECK_FAILED_FALLBACK_DINAMIC_POSTFIX_QLLY,
    SUMMARY_REPORT_CHECK_SUCCESS_DINAMIC_POSTFIX_QLLY,
    TRUNCATION_SUFFIX_DINAMIC_POSTFIX_IU5M,
)

PREVIEW_CHAR_LIMIT: Final[int] = 800
_TRUNCATION_SUFFIX_CHAR_LEN: Final[int] = len(
    TRUNCATION_SUFFIX_DINAMIC_POSTFIX_IU5M,
)
PREVIEW_TRUNCATE_HEAD_CHARS: Final[int] = (
    PREVIEW_CHAR_LIMIT - _TRUNCATION_SUFFIX_CHAR_LEN
)

PENDING_STATE_STATUSES: Final[frozenset[str]] = frozenset(
    {
        STATUS_PENDING_DINAMIC_POSTFIX_TGHG,
        STATUS_CHECKING_DINAMIC_POSTFIX_TGHG,
    },
)


def summary_preview_repr(value: object) -> str:
    """Return ``repr(value)``, truncated for long values.

    Args:
        value: Any object to preview.

    Returns:
        Full ``repr`` or a prefix plus the catalog truncation suffix.
    """
    text = repr(value)
    if len(text) <= PREVIEW_CHAR_LIMIT:
        return text
    prefix = text[:PREVIEW_TRUNCATE_HEAD_CHARS]
    return f"{prefix}{TRUNCATION_SUFFIX_DINAMIC_POSTFIX_IU5M}"


def _report_text_for_passed(state: TaskState) -> str:
    """Compose report body for a passed task state.

    Args:
        state: State with optional
        :attr:`~core.models.TaskState.result`.

    Returns:
        Success line plus optional actual-result fragment.
    """
    parts: list[str] = [SUMMARY_REPORT_CHECK_SUCCESS_DINAMIC_POSTFIX_QLLY]
    result = state.result
    if result is not None and result.actual_result is not None:
        fragment = summary_preview_repr(result.actual_result)
        parts.append(
            f"{SUMMARY_REPORT_ACTUAL_FRAGMENT_HEADER_DINAMIC_POSTFIX_QLLY}"
            f"{fragment}",
        )
    return "".join(parts)


def _report_text_for_failed(state: TaskState) -> str:
    """Compose report body for a failed task state.

    Args:
        state: State that may carry error text and actual output.

    Returns:
        Joined error lines, a fallback message, or structured fragments.
    """
    result = state.result
    segments: list[str] = []
    if result is not None:
        if result.error_text:
            segments.append(result.error_text.strip())
        if result.actual_result is not None:
            fragment = summary_preview_repr(result.actual_result)
            segments.append(
                f"{SUMMARY_REPORT_ACTUAL_FRAGMENT_HEADER_DINAMIC_POSTFIX_QLLY}"
                f"{fragment}",
            )
    if segments:
        return NEWLINE_DINAMIC_POSTFIX_QLLY.join(segments).strip()
    return SUMMARY_REPORT_CHECK_FAILED_FALLBACK_DINAMIC_POSTFIX_QLLY


def summary_report_for_state(state: TaskState) -> str | None:
    """Build user-visible report text for one task's check state.

    Args:
        state: Per-task state including status and optional checker
        result.

    Returns:
        Report string, or ``None`` while status is still
        pending/checking.
    """
    if state.status in PENDING_STATE_STATUSES:
        return None

    if state.status == STATUS_PASSED_DINAMIC_POSTFIX_TGHG:
        return _report_text_for_passed(state)

    if state.status == STATUS_FAILED_DINAMIC_POSTFIX_TGHG:
        return _report_text_for_failed(state)

    return None
