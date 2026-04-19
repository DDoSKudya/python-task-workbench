"""UI translation: JSON maps and locale switching."""

from __future__ import annotations

from .translate import (
    add_locale_listener,
    get_locale,
    load_translation_files,
    remove_locale_listener,
    set_locale,
    translate,
)

translate_text = translate

__all__ = [
    "add_locale_listener",
    "get_locale",
    "load_translation_files",
    "remove_locale_listener",
    "set_locale",
    "translate",
    "translate_text",
]
