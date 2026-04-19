"""Public exports for history dialog package.

Exports:
    HistoryDialog: Dialog widget for viewing check history.
"""

from __future__ import annotations

from .dialog import HistoryDialog as HistoryDialog

__all__: tuple[str, ...] = ("HistoryDialog",)
