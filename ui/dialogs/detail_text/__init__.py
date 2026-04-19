"""Public exports for detail text dialog package.

Exports:
    DetailTextDialog: Dialog that displays detailed text content.
    normalize_code_for_view: Formatter for code preview rendering.
"""

from __future__ import annotations

from .dialog import DetailTextDialog as DetailTextDialog
from .formatting import normalize_code_for_view as normalize_code_for_view

__all__: tuple[str, ...] = (
    "DetailTextDialog",
    "normalize_code_for_view",
)
