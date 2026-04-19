"""
This module loads and validates application-wide default settings from a
JSON config file and exposes them as typed constants used across the
generator and CLI.

It works by reading config.json via core.paths.CONFIG_PATH, asserting
that the root is a mapping, and then fetching individual keys with
type-specific helpers that raise descriptive errors if keys are missing
or of the wrong type.

It defines global tuning constants like NO_REPEAT_TASK_WINDOW,
NO_REPEAT_FAMILY_WINDOW, STATE_HISTORY_MAX, FAKER_LOCALES,
AUTO_FAMILY_PARTS_MIN, and a PROJECT_DIR root path.

Helper functions _get_required_* and _get_optional_* encapsulate strict
type validation for strings, ints, floats, bools, and optionals, while
_resolved_path and _resolve_required_path convert relative paths from
settings into absolute paths under the project directory.

At import time it reads the JSON into SETTINGS and initializes many
DEFAULT_* constants (count, data volume/order/quality, profile, mode,
topic, seed, flags, export settings, content pack, and resolved
state/solution file paths).

Within the broader system, these constants act as the central
configuration source that other components (task generation, CLI modes,
export logic) use to determine default behavior and file locations.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from pathlib import Path
from typing import Final, TypeVar

from core.paths import CONFIG_PATH as CONFIG_FILE
from messages import (
    ERROR_SETTING_MISSING_DINAMIC_POSTFIX_3JC2,
    ERROR_SETTING_TYPE_DINAMIC_POSTFIX_3JC2,
    ERROR_SETTINGS_TYPE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_CONTENT_PACK_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_COUNT_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_DATA_ORDER_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_DATA_QUALITY_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_DATA_VOLUME_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_DOMAIN_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_EXPORT_FILE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_EXPORT_FORMAT_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_FOCUS_TOOL_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_HINTS_STEP_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_INVERSE_RATE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_MODE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_PROFILE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_SEED_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_SESSION_SIZE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_SHOW_FULL_EXAMPLE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_SHOW_SOLUTION_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_SOLUTION_FILE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_STAGE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_STATE_FILE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_STORY_MODE_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_STRICT_TYPES_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_SURPRISE_ME_DINAMIC_POSTFIX_3JC2,
    KEY_DEFAULT_TOPIC_DINAMIC_POSTFIX_3JC2,
    TYPE_KIND_BOOL_DINAMIC_POSTFIX_3JC2,
    TYPE_KIND_FLOAT_DINAMIC_POSTFIX_3JC2,
    TYPE_KIND_INT_DINAMIC_POSTFIX_3JC2,
    TYPE_KIND_OPTIONAL_INT_DINAMIC_POSTFIX_3JC2,
    TYPE_KIND_OPTIONAL_STR_DINAMIC_POSTFIX_3JC2,
    TYPE_KIND_STR_DINAMIC_POSTFIX_3JC2,
    UTF8_ENCODING_DINAMIC_POSTFIX_3JC2,
)

NO_REPEAT_TASK_WINDOW: Final[int] = 100
NO_REPEAT_FAMILY_WINDOW: Final[int] = 40
STATE_HISTORY_MAX: Final[int] = 1000
FAKER_LOCALES: Final[tuple[str, str]] = ("ru_RU", "en_US")
AUTO_FAMILY_PARTS_MIN: Final[int] = 4
PROJECT_DIR: Final[Path] = Path(__file__).resolve().parent.parent
type SettingsMap = dict[str, object]
_SettingT = TypeVar("_SettingT")


def _load_settings() -> SettingsMap:
    """Load raw settings from `config.json`.

    Returns:
        Parsed settings dictionary.

    Raises:
        ValueError: If payload is not a JSON object.
    """
    payload = json.loads(
        CONFIG_FILE.read_text(encoding=UTF8_ENCODING_DINAMIC_POSTFIX_3JC2)
    )
    if not isinstance(payload, dict):
        raise ValueError(ERROR_SETTINGS_TYPE_DINAMIC_POSTFIX_3JC2)
    return payload


def _get_required(
    settings: Mapping[str, _SettingT],
    key: str,
) -> _SettingT:
    """Read a required key from settings mapping.

    Args:
        settings: Source settings mapping.
        key: Required key.

    Returns:
        Value associated with the key.

    Raises:
        ValueError: If key is absent.
    """
    if key not in settings:
        raise ValueError(
            ERROR_SETTING_MISSING_DINAMIC_POSTFIX_3JC2.format(key=key)
        )
    return settings[key]


def _get_required_str(settings: Mapping[str, object], key: str) -> str:
    """Read and validate required string setting.

    Args:
        settings: Source settings mapping.
        key: Required key.

    Returns:
        String value.

    Raises:
        ValueError: If key is absent or value is not a string.
    """
    value = _get_required(settings, key)
    if not isinstance(value, str):
        raise ValueError(
            ERROR_SETTING_TYPE_DINAMIC_POSTFIX_3JC2.format(
                key=key, kind=TYPE_KIND_STR_DINAMIC_POSTFIX_3JC2
            )
        )
    return value


def _get_required_int(settings: Mapping[str, object], key: str) -> int:
    """Read and validate required integer setting.

    Args:
        settings: Source settings mapping.
        key: Required key.

    Returns:
        Integer value.

    Raises:
        ValueError: If key is absent or value is not an integer.
    """
    value = _get_required(settings, key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(
            ERROR_SETTING_TYPE_DINAMIC_POSTFIX_3JC2.format(
                key=key, kind=TYPE_KIND_INT_DINAMIC_POSTFIX_3JC2
            )
        )
    return value


def _get_required_float(settings: Mapping[str, object], key: str) -> float:
    """Read and validate required float setting.

    Args:
        settings: Source settings mapping.
        key: Required key.

    Returns:
        Float value.

    Raises:
        ValueError: If key is absent or value has invalid type.
    """
    value = _get_required(settings, key)
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(
            ERROR_SETTING_TYPE_DINAMIC_POSTFIX_3JC2.format(
                key=key, kind=TYPE_KIND_FLOAT_DINAMIC_POSTFIX_3JC2
            )
        )
    return float(value)


def _get_required_bool(settings: Mapping[str, object], key: str) -> bool:
    """Read and validate required boolean setting.

    Args:
        settings: Source settings mapping.
        key: Required key.

    Returns:
        Boolean value.

    Raises:
        ValueError: If key is absent or value is not a boolean.
    """
    value = _get_required(settings, key)
    if not isinstance(value, bool):
        raise ValueError(
            ERROR_SETTING_TYPE_DINAMIC_POSTFIX_3JC2.format(
                key=key, kind=TYPE_KIND_BOOL_DINAMIC_POSTFIX_3JC2
            )
        )
    return value


def _get_optional_str(settings: Mapping[str, object], key: str) -> str | None:
    """Read and validate optional string setting.

    Args:
        settings: Source settings mapping.
        key: Optional key.

    Returns:
        String value or `None` when absent.

    Raises:
        ValueError: If value exists but is not a string.
    """
    value = settings.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(
            ERROR_SETTING_TYPE_DINAMIC_POSTFIX_3JC2.format(
                key=key, kind=TYPE_KIND_OPTIONAL_STR_DINAMIC_POSTFIX_3JC2
            )
        )
    return value


def _get_optional_int(settings: Mapping[str, object], key: str) -> int | None:
    """Read and validate optional integer setting.

    Args:
        settings: Source settings mapping.
        key: Optional key.

    Returns:
        Integer value or `None` when absent.

    Raises:
        ValueError: If value exists but is not an integer.
    """
    value = settings.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(
            ERROR_SETTING_TYPE_DINAMIC_POSTFIX_3JC2.format(
                key=key, kind=TYPE_KIND_OPTIONAL_INT_DINAMIC_POSTFIX_3JC2
            )
        )
    return value


def _resolved_path(setting_value: str) -> str:
    """Resolve a relative config path against project root.

    Args:
        setting_value: Path value from config.

    Returns:
        Absolute path string.
    """
    path_candidate = Path(setting_value)
    if path_candidate.is_absolute():
        return str(path_candidate)
    return str(PROJECT_DIR / setting_value)


def _resolve_required_path(settings: SettingsMap, key: str) -> str:
    """Read required string setting and resolve it to absolute path.

    Args:
        settings: Source settings mapping.
        key: Required key containing path-like value.

    Returns:
        Absolute path string.
    """
    return _resolved_path(_get_required_str(settings, key))


SETTINGS: Final[SettingsMap] = _load_settings()
DEFAULT_COUNT: Final[int] = _get_required_int(
    SETTINGS, KEY_DEFAULT_COUNT_DINAMIC_POSTFIX_3JC2
)
DEFAULT_DATA_VOLUME: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_DATA_VOLUME_DINAMIC_POSTFIX_3JC2
)
DEFAULT_DATA_ORDER: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_DATA_ORDER_DINAMIC_POSTFIX_3JC2
)
DEFAULT_DATA_QUALITY: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_DATA_QUALITY_DINAMIC_POSTFIX_3JC2
)
DEFAULT_PROFILE: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_PROFILE_DINAMIC_POSTFIX_3JC2
)
DEFAULT_SHOW_SOLUTION: Final[bool] = _get_required_bool(
    SETTINGS, KEY_DEFAULT_SHOW_SOLUTION_DINAMIC_POSTFIX_3JC2
)
DEFAULT_SHOW_FULL_EXAMPLE: Final[bool] = _get_required_bool(
    SETTINGS, KEY_DEFAULT_SHOW_FULL_EXAMPLE_DINAMIC_POSTFIX_3JC2
)
DEFAULT_HINTS_STEP: Final[bool] = _get_required_bool(
    SETTINGS, KEY_DEFAULT_HINTS_STEP_DINAMIC_POSTFIX_3JC2
)
DEFAULT_STRICT_TYPES: Final[bool] = _get_required_bool(
    SETTINGS, KEY_DEFAULT_STRICT_TYPES_DINAMIC_POSTFIX_3JC2
)
DEFAULT_SEED: Final[int | None] = _get_optional_int(
    SETTINGS, KEY_DEFAULT_SEED_DINAMIC_POSTFIX_3JC2
)
DEFAULT_MODE: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_MODE_DINAMIC_POSTFIX_3JC2
)
DEFAULT_TOPIC: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_TOPIC_DINAMIC_POSTFIX_3JC2
)
DEFAULT_DOMAIN: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_DOMAIN_DINAMIC_POSTFIX_3JC2
)
DEFAULT_STAGE: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_STAGE_DINAMIC_POSTFIX_3JC2
)
DEFAULT_SURPRISE_ME: Final[bool] = _get_required_bool(
    SETTINGS, KEY_DEFAULT_SURPRISE_ME_DINAMIC_POSTFIX_3JC2
)
DEFAULT_FOCUS_TOOL: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_FOCUS_TOOL_DINAMIC_POSTFIX_3JC2
)
DEFAULT_EXPORT_FORMAT: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_EXPORT_FORMAT_DINAMIC_POSTFIX_3JC2
)
DEFAULT_EXPORT_FILE: Final[str | None] = _get_optional_str(
    SETTINGS, KEY_DEFAULT_EXPORT_FILE_DINAMIC_POSTFIX_3JC2
)
DEFAULT_STORY_MODE: Final[bool] = _get_required_bool(
    SETTINGS, KEY_DEFAULT_STORY_MODE_DINAMIC_POSTFIX_3JC2
)
DEFAULT_SESSION_SIZE: Final[int] = _get_required_int(
    SETTINGS, KEY_DEFAULT_SESSION_SIZE_DINAMIC_POSTFIX_3JC2
)
DEFAULT_INVERSE_RATE: Final[float] = _get_required_float(
    SETTINGS, KEY_DEFAULT_INVERSE_RATE_DINAMIC_POSTFIX_3JC2
)
DEFAULT_CONTENT_PACK: Final[str] = _get_required_str(
    SETTINGS, KEY_DEFAULT_CONTENT_PACK_DINAMIC_POSTFIX_3JC2
)
DEFAULT_STATE_FILE: Final[str] = _resolve_required_path(
    SETTINGS,
    KEY_DEFAULT_STATE_FILE_DINAMIC_POSTFIX_3JC2,
)
DEFAULT_SOLUTION_FILE: Final[str] = _resolve_required_path(
    SETTINGS,
    KEY_DEFAULT_SOLUTION_FILE_DINAMIC_POSTFIX_3JC2,
)
