"""
This module maps high-level task status strings to display glyphs and Qt
object names used for styling status marks in the UI.

It works by maintaining lookup dictionaries keyed by TaskStatus and
exposing helper functions that validate a raw status string and then
return the corresponding symbol or style object name, falling back to
defaults when the status is unknown.

It defines two dictionaries, MARK_BY_STATUS and OBJECT_NAME_BY_STATUS,
which associate statuses like "ok", "bad", "checking", and "pending"
with message-based mark characters and Qt object-name tokens.

The internal _is_task_status function acts as a TypeGuard to recognize
supported statuses, while mark_for_status and mark_object_name use it
to either retrieve the correct glyph/object name or return a default
mark and the pending-style object name, integrating status semantics
into the visual layer.
"""

from __future__ import annotations

from typing import TypeGuard

from messages import (
    DEFAULT_MARK_DINAMIC_POSTFIX_MUF0,
    MARK_BAD_DINAMIC_POSTFIX_MUF0,
    MARK_CHECKING_DINAMIC_POSTFIX_MUF0,
    MARK_OK_DINAMIC_POSTFIX_MUF0,
    MARK_PENDING_DINAMIC_POSTFIX_MUF0,
    OBJECT_MARK_BAD_DINAMIC_POSTFIX_MUF0,
    OBJECT_MARK_CHECKING_DINAMIC_POSTFIX_MUF0,
    OBJECT_MARK_OK_DINAMIC_POSTFIX_MUF0,
    OBJECT_MARK_PENDING_DINAMIC_POSTFIX_MUF0,
)

from .models import TaskStatus

MARK_BY_STATUS: dict[TaskStatus, str] = {
    "ok": MARK_OK_DINAMIC_POSTFIX_MUF0,
    "bad": MARK_BAD_DINAMIC_POSTFIX_MUF0,
    "checking": MARK_CHECKING_DINAMIC_POSTFIX_MUF0,
    "pending": MARK_PENDING_DINAMIC_POSTFIX_MUF0,
}
OBJECT_NAME_BY_STATUS: dict[TaskStatus, str] = {
    "ok": OBJECT_MARK_OK_DINAMIC_POSTFIX_MUF0,
    "bad": OBJECT_MARK_BAD_DINAMIC_POSTFIX_MUF0,
    "checking": OBJECT_MARK_CHECKING_DINAMIC_POSTFIX_MUF0,
    "pending": OBJECT_MARK_PENDING_DINAMIC_POSTFIX_MUF0,
}


def _is_task_status(value: str) -> TypeGuard[TaskStatus]:
    """Return whether a string is a known session summary status.

    Args:
        value: Raw status value from application data.

    Returns:
        True when ``value`` is a supported task status.
    """
    return value in MARK_BY_STATUS


def mark_for_status(status: str) -> str:
    """Return the mark glyph for a summary status string.

    Args:
        status: Summary row status label.

    Returns:
        Display symbol for the status, or the default mark when unknown.
    """
    return (
        MARK_BY_STATUS[status]
        if _is_task_status(status)
        else DEFAULT_MARK_DINAMIC_POSTFIX_MUF0
    )


def mark_object_name(status: str) -> str:
    """Return the Qt object name used to style the status mark.

    Args:
        status: Summary row status label.

    Returns:
        Object name token for mark styling, or the idle token if
        unknown.
    """
    return (
        OBJECT_NAME_BY_STATUS[status]
        if _is_task_status(status)
        else OBJECT_MARK_PENDING_DINAMIC_POSTFIX_MUF0
    )
