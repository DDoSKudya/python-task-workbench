"""Localized application strings.

Each public attribute name maps to an English source string in
:data:`CATALOG`. Accessing ``messages.NAME`` resolves through the
translation layer so the active UI language is applied.

Values imported with ``from messages import X`` are resolved once at
import time; use ``import messages`` and ``messages.X`` for language
changes without restarting the process.
"""

from __future__ import annotations

from typing import Final

from ._catalog import CATALOG
from .translate import (
    add_locale_listener,
    get_locale,
    load_translation_files,
    remove_locale_listener,
    set_locale,
    translate_text,
)

_ERR_UNKNOWN_ATTRIBUTE_TEMPLATE: Final[str] = (
    "module {module_name!r} has no attribute {attribute_name!r}"
)


def translate(text: str) -> str:
    """Translate a raw English UI string using loaded JSON tables.

    Args:
        text: English source phrase from the message catalog.

    Returns:
        Localized phrase for the currently active locale.
    """
    return translate_text(text)


def __getattr__(name: str) -> str:
    """Resolve message names lazily from the translation catalog.

    Args:
        name: Public attribute name looked up on this module.

    Returns:
        Localized message string for the requested catalog key.

    Raises:
        AttributeError: If the key does not exist in ``CATALOG``.
    """
    try:
        source = CATALOG[name]
    except KeyError as exc:
        raise AttributeError(
            _ERR_UNKNOWN_ATTRIBUTE_TEMPLATE.format(
                module_name=__name__,
                attribute_name=name,
            )
        ) from exc
    return translate_text(source)


def __dir__() -> list[str]:
    """Return static and dynamic public attributes for introspection.

    Returns:
        Sorted union of module globals and catalog-backed keys.
    """
    return sorted(set(globals()) | set(CATALOG))


__all__ = [
    "CATALOG",
    "translate",
    "translate_text",
    "get_locale",
    "set_locale",
    "load_translation_files",
    "add_locale_listener",
    "remove_locale_listener",
]
