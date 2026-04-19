"""
This module manages loading and saving application and UI default
settings from a JSON config file.

It works by reading config.json, validating that the root is a
string-keyed object, parsing individual fields into strongly-typed
values with sane fallbacks, and writing updated settings back with a
stable JSON format.

It defines numerous constants for JSON formatting, default values
(session size, strict types, timeouts, UI layout, language),
configuration key names, and allowed boolean and language values.

It introduces two frozen dataclasses, UiDefaults and AppDefaults, to
represent the persisted UI preferences and the combined session+UI
defaults used by the rest of the application.

Helper functions like _json_int, _json_bool, _optional_seed,
_selected_packs, _session_count, _splitter_sizes, and _ui_language
encapsulate the rules for interpreting raw JSON scalars and structures
into validated internal types.

The main functions load_defaults and save_defaults_config bridge between
on-disk JSON and in-memory models by constructing AppDefaults from the
parsed config and merging current SessionConfig and UiDefaults back into
the JSON object before saving.

Within the broader system, this module centralizes configuration
handling so that session creation and the UI can consistently use and
persist user preferences across runs.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from dataclasses import dataclass
from typing import Final, TypeGuard, cast

from messages import (
    ERR_BOOL_AS_INT_DINAMIC_POSTFIX_2IV9,
    ERR_NOT_OBJECT_DINAMIC_POSTFIX_2IV9,
    ERR_UNSUPPORTED_INT_TYPE_DINAMIC_POSTFIX_2IV9,
)
from task_packs import list_available_packs

from .models import CheckerEntryMode, SessionConfig
from .paths import CONFIG_PATH

_JSON_ENCODING: Final[str] = "utf-8"
_JSON_INDENT: Final[int] = 2
_JSON_ENSURE_ASCII: Final[bool] = False
_JSON_RECORD_SUFFIX: Final[str] = "\n"

_ERR_NOT_OBJECT: Final[str] = ERR_NOT_OBJECT_DINAMIC_POSTFIX_2IV9
_ERR_BOOL_AS_INT: Final[str] = ERR_BOOL_AS_INT_DINAMIC_POSTFIX_2IV9
_ERR_UNSUPPORTED_INT_TYPE: Final[str] = (
    ERR_UNSUPPORTED_INT_TYPE_DINAMIC_POSTFIX_2IV9
)

_DEFAULT_COUNT: Final[int] = 3
_MIN_SESSION_SIZE: Final[int] = 1
_DEFAULT_STRICT_TYPES: Final[bool] = True
_DEFAULT_CHECK_TIMEOUT_SEC: Final[int] = 3
_DEFAULT_PER_TASK_MINUTES: Final[int] = 5
_DEFAULT_WINDOW_COMPACT: Final[bool] = True
_DEFAULT_FONT_SIZE: Final[int] = 12
_DEFAULT_AUTOCHECK_ON_NEXT: Final[bool] = True

_SPLITTER_COUNT: Final[int] = 4
_DEFAULT_SPLITTER: tuple[int, int, int, int] = (1, 1, 1, 2)

_K_UI_DEFAULT_PACKS: Final[str] = "ui_default_packs"
_K_DEFAULT_COUNT: Final[str] = "default_count"
_K_DEFAULT_SESSION_SIZE: Final[str] = "default_session_size"
_K_DEFAULT_SEED: Final[str] = "default_seed"
_K_DEFAULT_STRICT_TYPES: Final[str] = "default_strict_types"
_K_CHECKER_ENTRY_MODE: Final[str] = "checker_entry_mode"
_K_UI_CHECK_TIMEOUT_SEC: Final[str] = "ui_check_timeout_sec"
_K_UI_PER_TASK_MINUTES: Final[str] = "ui_per_task_minutes"
_K_UI_SPLITTER_SIZES: Final[str] = "ui_splitter_sizes"
_K_UI_WINDOW_COMPACT: Final[str] = "ui_window_compact"
_K_UI_FONT_SIZE: Final[str] = "ui_font_size"
_K_UI_AUTOCHECK_ON_NEXT: Final[str] = "ui_autocheck_on_next"
_K_UI_LANGUAGE: Final[str] = "ui_language"
_DEFAULT_UI_LANGUAGE: Final[str] = "en"
_DEFAULT_CHECKER_ENTRY_MODE: Final[CheckerEntryMode] = "hybrid"
_CHECKER_ENTRY_MODE_VALUES: Final[frozenset[str]] = frozenset(
    {"strict", "hybrid"}
)
_SUPPORTED_UI_LANGUAGES: Final[frozenset[str]] = frozenset({"en", "ru"})

_BOOL_TRUE_STRINGS: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "on"}
)
_BOOL_FALSE_STRINGS: Final[frozenset[str]] = frozenset(
    {"0", "false", "no", "off"}
)

type JsonObject = dict[str, object]

AVAILABLE_PACKS: Final[tuple[str, ...]] = list_available_packs()


@dataclass(frozen=True)
class UiDefaults:
    """Persisted UI preferences (layout, fonts, splitter weights)."""

    default_packs: tuple[str, ...]
    window_compact: bool
    font_size: int
    autocheck_on_next: bool
    splitter_sizes: tuple[int, int, int, int]
    ui_language: str


@dataclass(frozen=True)
class AppDefaults:
    """Session and UI defaults loaded from ``config.json``."""

    session: SessionConfig
    ui: UiDefaults


def _is_str_key_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    """Return whether value is a dictionary with string keys.

    Args:
        value: Candidate JSON value.

    Returns:
        True when ``value`` is ``dict[str, object]``-compatible.
    """
    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)


def load_json_config() -> JsonObject:
    """Read and parse ``config.json`` as a generic object map.

    Returns:
        Root JSON object as string-keyed values.

    Raises:
        ValueError: If the file does not contain a JSON object.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    text = CONFIG_PATH.read_text(encoding=_JSON_ENCODING)
    payload = json.loads(text)
    if not _is_str_key_object_dict(payload):
        raise ValueError(_ERR_NOT_OBJECT)
    return payload


def save_json_config(payload: Mapping[str, object]) -> None:
    """Write ``payload`` to ``config.json`` with stable formatting.

    Args:
        payload: Full configuration object to persist.
    """
    body = json.dumps(
        payload,
        ensure_ascii=_JSON_ENSURE_ASCII,
        indent=_JSON_INDENT,
    )
    CONFIG_PATH.write_text(
        body + _JSON_RECORD_SUFFIX,
        encoding=_JSON_ENCODING,
    )


def _json_int(value: object) -> int:
    """Parse JSON numbers or numeric strings into ``int``.

    Args:
        value: Scalar from ``config.json``.

    Returns:
        Integer value.

    Raises:
        TypeError: If the value cannot be converted.
        ValueError: If a string is not a valid integer.
    """
    if isinstance(value, bool):
        raise TypeError(_ERR_BOOL_AS_INT)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.strip())
    if isinstance(value, float):
        return int(value)
    raise TypeError(
        _ERR_UNSUPPORTED_INT_TYPE.format(name=type(value).__name__)
    )


def _json_bool(value: object, default: bool) -> bool:
    """Parse a JSON-like scalar into ``bool`` with fallback.

    Args:
        value: Scalar from ``config.json``.
        default: Fallback value for unsupported inputs.

    Returns:
        Parsed boolean value.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _BOOL_TRUE_STRINGS:
            return True
        if normalized in _BOOL_FALSE_STRINGS:
            return False
    return default


def _selected_packs(raw: Mapping[str, object]) -> tuple[str, ...]:
    """Resolve pack ids from the last saved UI selection only.

    Unknown ids are dropped. There is no fallback to «all packs»: if the
    key is absent, empty, or nothing matches installed packs, the result
    is empty and the user must pick packs in the session dialog.

    Args:
        raw: Parsed JSON root object.

    Returns:
        Tuple of valid pack ids (possibly empty).
    """
    available = frozenset(AVAILABLE_PACKS)
    packs_raw = raw.get(_K_UI_DEFAULT_PACKS)
    if not isinstance(packs_raw, list) or not packs_raw:
        return ()
    return tuple(p for p in packs_raw if isinstance(p, str) and p in available)


def _session_count(raw: Mapping[str, object]) -> int:
    """Resolve session size from ``default_count`` or
    ``default_session_size``.

    Args:
        raw: Parsed JSON root object.

    Returns:
        Positive task count (legacy key is clamped to at least one).
    """
    if raw.get(_K_DEFAULT_COUNT) is not None:
        return _json_int(raw[_K_DEFAULT_COUNT])
    if raw.get(_K_DEFAULT_SESSION_SIZE) is not None:
        return max(
            _MIN_SESSION_SIZE,
            _json_int(raw[_K_DEFAULT_SESSION_SIZE]),
        )
    return _DEFAULT_COUNT


def _splitter_sizes(raw: Mapping[str, object]) -> tuple[int, int, int, int]:
    """Read ``ui_splitter_sizes`` or use the default four-tuple.

    Args:
        raw: Parsed JSON root object.

    Returns:
        Exactly four positive integers for splitter weights.
    """
    raw_val = raw.get(_K_UI_SPLITTER_SIZES)
    if not isinstance(raw_val, list) or len(raw_val) != _SPLITTER_COUNT:
        return _DEFAULT_SPLITTER
    first, second, third, fourth = (
        _json_int(raw_val[index]) for index in range(_SPLITTER_COUNT)
    )
    return first, second, third, fourth


def _ui_language(raw: Mapping[str, object]) -> str:
    """Read ``ui_language`` from config (``en`` or ``ru``)."""
    val = raw.get(_K_UI_LANGUAGE, _DEFAULT_UI_LANGUAGE)
    if not isinstance(val, str):
        return _DEFAULT_UI_LANGUAGE
    normalized = val.strip().lower()
    if normalized not in _SUPPORTED_UI_LANGUAGES:
        return _DEFAULT_UI_LANGUAGE
    return normalized


def _optional_seed(value: object) -> int | None:
    """Parse optional RNG seed from JSON.

    Args:
        value: Raw JSON value for ``default_seed``.

    Returns:
        Integer seed, or ``None`` if not set or not a plain integer.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        return int(stripped) if stripped.isdigit() else None
    return None


def _checker_entry_mode(raw: Mapping[str, object]) -> CheckerEntryMode:
    """Read checker entry mode from config with fallback.

    Args:
        raw: Parsed JSON root object.

    Returns:
        Either ``strict`` or ``hybrid``.
    """
    value = raw.get(_K_CHECKER_ENTRY_MODE, _DEFAULT_CHECKER_ENTRY_MODE)
    if not isinstance(value, str):
        return _DEFAULT_CHECKER_ENTRY_MODE
    normalized = value.strip().lower()
    if normalized not in _CHECKER_ENTRY_MODE_VALUES:
        return _DEFAULT_CHECKER_ENTRY_MODE
    return cast(CheckerEntryMode, normalized)


def _build_session_defaults(
    *,
    raw: Mapping[str, object],
    packs: tuple[str, ...],
) -> SessionConfig:
    """Build default session settings from raw config values.

    Args:
        raw: Parsed JSON root object.
        packs: Validated selected pack ids.

    Returns:
        Session defaults for a new learner session.
    """
    return SessionConfig(
        selected_packs=packs,
        count=_session_count(raw),
        seed=_optional_seed(raw.get(_K_DEFAULT_SEED)),
        strict_types=_json_bool(
            raw.get(_K_DEFAULT_STRICT_TYPES),
            default=_DEFAULT_STRICT_TYPES,
        ),
        checker_entry_mode=_checker_entry_mode(raw),
        check_timeout_sec=_json_int(
            raw.get(_K_UI_CHECK_TIMEOUT_SEC, _DEFAULT_CHECK_TIMEOUT_SEC),
        ),
        per_task_minutes=_json_int(
            raw.get(_K_UI_PER_TASK_MINUTES, _DEFAULT_PER_TASK_MINUTES),
        ),
    )


def _build_ui_defaults(
    *,
    raw: Mapping[str, object],
    packs: tuple[str, ...],
) -> UiDefaults:
    """Build default UI settings from raw config values.

    Args:
        raw: Parsed JSON root object.
        packs: Validated selected pack ids.

    Returns:
        UI defaults for window layout and behavior.
    """
    return UiDefaults(
        default_packs=packs,
        window_compact=_json_bool(
            raw.get(_K_UI_WINDOW_COMPACT),
            default=_DEFAULT_WINDOW_COMPACT,
        ),
        font_size=_json_int(raw.get(_K_UI_FONT_SIZE, _DEFAULT_FONT_SIZE)),
        autocheck_on_next=_json_bool(
            raw.get(_K_UI_AUTOCHECK_ON_NEXT),
            default=_DEFAULT_AUTOCHECK_ON_NEXT,
        ),
        splitter_sizes=_splitter_sizes(raw),
        ui_language=_ui_language(raw),
    )


def load_defaults() -> AppDefaults:
    """Load :class:`AppDefaults` from ``config.json`` with safe
    fallbacks.

    Returns:
        Session and UI defaults from the file; pack selection is only
        restored from ``ui_default_packs`` when those ids still exist.
    """
    raw = load_json_config()
    packs = _selected_packs(raw)
    session_defaults = _build_session_defaults(raw=raw, packs=packs)
    ui_defaults = _build_ui_defaults(raw=raw, packs=packs)
    return AppDefaults(session=session_defaults, ui=ui_defaults)


def save_defaults_config(session: SessionConfig, ui: UiDefaults) -> None:
    """Merge ``session`` and ``ui`` into the on-disk JSON and save.

    Args:
        session: Current session configuration to persist.
        ui: Current UI defaults to persist.
    """
    payload: JsonObject = dict(load_json_config())
    payload[_K_UI_DEFAULT_PACKS] = list(session.selected_packs)
    payload[_K_DEFAULT_COUNT] = session.count
    payload[_K_DEFAULT_SEED] = session.seed
    payload[_K_DEFAULT_STRICT_TYPES] = session.strict_types
    payload[_K_CHECKER_ENTRY_MODE] = session.checker_entry_mode
    payload[_K_UI_CHECK_TIMEOUT_SEC] = session.check_timeout_sec
    payload[_K_UI_PER_TASK_MINUTES] = session.per_task_minutes
    payload[_K_UI_WINDOW_COMPACT] = ui.window_compact
    payload[_K_UI_FONT_SIZE] = ui.font_size
    payload[_K_UI_AUTOCHECK_ON_NEXT] = ui.autocheck_on_next
    payload[_K_UI_SPLITTER_SIZES] = list(ui.splitter_sizes)
    payload[_K_UI_LANGUAGE] = ui.ui_language
    save_json_config(payload)
