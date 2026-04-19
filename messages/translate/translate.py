"""
This module implements a simple localization layer that loads
translation strings from JSON files and resolves UI text according to
the currently active locale.

It works by maintaining a global runtime state with an active Locale (en
or ru) and a merged translation table, protected by a lock and backed
by on-disk JSON files.

It defines a Locale enum, constants for file patterns, encoding,
defaults, and an internal _TranslationRuntime dataclass holding the
active locale and translation map.

Helper functions _normalize_locale_tag, _string_entries_from_mapping,
_load_translation_file, and _merge_translation_tables normalize user
language tags, filter JSON payloads to string-to-string pairs, and merge
all *.json files in a directory with later files overriding earlier
ones.

The public function load_translation_files repopulates the in-memory
table from disk, while translate uses the active locale to return
either the original text or its Russian translation if available.

get_locale and set_locale expose and modify the active locale;
set_locale also reloads translations and notifies registered listeners
via a simple observer mechanism stored in _LISTENERS.

The functions add_locale_listener and remove_locale_listener manage
callbacks to be run after locale changes, and current_translation_table
returns a copy of the current translation map for introspection or
tests.

At import time, load_translation_files() is called once so that the
localization system is ready for use by the rest of the application
without explicit initialization.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from threading import RLock

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final

JSON_FILE_GLOB: Final[str] = "*.json"
TEXT_ENCODING: Final[str] = "utf-8"
_EMPTY_TEXT: Final[str] = ""

_PACKAGE_DIR: Final[Path] = Path(__file__).resolve().parent
_DEFAULT_TRANSLATIONS_ROOT: Final[Path] = _PACKAGE_DIR


class Locale(str, Enum):
    """BCP-style language tags supported by the translation layer."""

    EN = "en"
    RU = "ru"


type LocaleListener = Callable[[], None]
type TranslationTable = dict[str, str]

_DEFAULT_LOCALE: Final[Locale] = Locale.EN
_SUPPORTED_LOCALES: Final[frozenset[Locale]] = frozenset(Locale)


@dataclass(slots=True)
class _TranslationRuntime:
    """Active locale and merged phrase table (shared runtime state)."""

    active_locale: Locale
    table: TranslationTable = field(default_factory=dict)


_runtime: Final[_TranslationRuntime] = _TranslationRuntime(
    active_locale=_DEFAULT_LOCALE,
)
_LISTENERS: list[LocaleListener] = []
_LOCK: Final[RLock] = RLock()


def _normalize_locale_tag(raw: str) -> Locale:
    """Map arbitrary user input to a supported :class:`Locale`.

    Args:
        raw: Language tag from configuration or UI, possibly padded or
            differently cased.

    Returns:
        ``Locale.EN`` when the tag is missing or unsupported; otherwise
        the matching :class:`Locale` member.
    """
    candidate = raw.strip().lower() if raw else _EMPTY_TEXT
    return next(
        (loc for loc in _SUPPORTED_LOCALES if loc.value == candidate),
        _DEFAULT_LOCALE,
    )


def _string_entries_from_mapping(
    payload: Mapping[object, object],
) -> TranslationTable:
    """Keep only string-to-string pairs from an arbitrary JSON value.

    Args:
        payload: Parsed JSON mapping-like root value.

    Returns:
        A new table with only ``str`` keys mapped to ``str`` values.
    """
    return {
        key: value
        for key, value in payload.items()
        if isinstance(key, str) and isinstance(value, str)
    }


def _load_translation_file(path: Path) -> TranslationTable:
    """Parse one ``.json`` file into a translation table.

    Args:
        path: File to read.

    Returns:
        Pairs from the file, or empty if blank or unusable.

    Raises:
        json.JSONDecodeError: If non-empty content is not valid JSON.
    """
    raw = path.read_text(encoding=TEXT_ENCODING)
    if not raw.strip():
        return {}
    payload: object = json.loads(raw)
    if not isinstance(payload, Mapping):
        return {}
    return _string_entries_from_mapping(payload)


def _merge_translation_tables(root: Path) -> TranslationTable:
    """Merge every ``*.json`` file under ``root`` in sorted name order.

    Later files override keys from earlier files.

    Args:
        root: Directory that should contain translation JSON files.

    Returns:
        Combined translation table, or empty when ``root`` is not a
        directory.
    """
    merged: TranslationTable = {}
    if not root.is_dir():
        return merged
    for path in sorted(root.glob(JSON_FILE_GLOB)):
        merged.update(_load_translation_file(path))
    return merged


def load_translation_files(directory: Path | None = None) -> None:
    """Reload in-memory tables from JSON files on disk.

    Args:
        directory: Folder to scan; defaults to this package directory.
    """
    root = _DEFAULT_TRANSLATIONS_ROOT if directory is None else directory
    merged = _merge_translation_tables(root)
    with _LOCK:
        _runtime.table = merged


def translate(text: str) -> str:
    """Return ``text`` translated for :func:`get_locale`.

    Args:
        text: Source phrase, usually English from the string catalog.

    Returns:
        Russian text when active locale is ``ru`` and a key exists;
        otherwise ``text`` unchanged.
    """
    if not text:
        return text
    with _LOCK:
        active = _runtime.active_locale
        table = _runtime.table
    return text if active is not Locale.RU else table.get(text, text)


def get_locale() -> str:
    """Return the active UI language tag.

    Returns:
        ``Locale.EN.value`` or ``Locale.RU.value``.
    """
    with _LOCK:
        return _runtime.active_locale.value


def set_locale(lang: str) -> None:
    """Set the active locale and notify listeners when it changes.

    Args:
        lang: Requested language tag; unknown tags map to English.
    """
    chosen = _normalize_locale_tag(lang)
    with _LOCK:
        if _runtime.active_locale is chosen:
            return
        _runtime.active_locale = chosen
        callbacks = list(_LISTENERS)
    load_translation_files()
    for callback in callbacks:
        callback()


def add_locale_listener(callback: LocaleListener) -> None:
    """Register a callback invoked after each successful locale change.

    Args:
        callback: Callable with no parameters (safe during UI refresh).
    """
    with _LOCK:
        _LISTENERS.append(callback)


def remove_locale_listener(callback: LocaleListener) -> None:
    """Unregister a listener added via :func:`add_locale_listener`.

    Args:
        callback: The exact object that was registered.
    """
    with _LOCK:
        try:
            _LISTENERS.remove(callback)
        except ValueError:
            return


def current_translation_table() -> Mapping[str, str]:
    """Return a copy of the merged translation map (for tests).

    Returns:
        A shallow copy of the in-memory table.
    """
    with _LOCK:
        return dict(_runtime.table)


load_translation_files()
