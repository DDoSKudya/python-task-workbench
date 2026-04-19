"""
This module serves as an index or façade for a group of commonly used
icon objects or factories, making them easy to import from a single
place.

It works by importing selected icon symbols from several sibling modules
and then explicitly re-exporting them through the __all__ tuple.

It contains only imports for icon_clipboard_list, icon_clock,
icon_settings, icon_code, icon_file_text, icon_trash, icon_check,
icon_play_filled, and icon_square_filled, plus a Final __all__ tuple
listing those names.

Within the broader system, this module provides a stable, centralized
import path for UI components that need access to shared icons,
improving consistency and reducing coupling to the internal icon module
structure.
"""

from __future__ import annotations

from typing import Final

from .chrome import icon_clipboard_list, icon_clock, icon_settings
from .content import icon_code, icon_file_text
from .destructive import icon_trash
from .marks import icon_check
from .playback import icon_play_filled, icon_square_filled

__all__: Final[tuple[str, ...]] = (
    "icon_check",
    "icon_clipboard_list",
    "icon_clock",
    "icon_code",
    "icon_file_text",
    "icon_play_filled",
    "icon_settings",
    "icon_square_filled",
    "icon_trash",
)
