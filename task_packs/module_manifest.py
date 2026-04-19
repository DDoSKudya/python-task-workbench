"""
This module loads and validates module.json manifest files for task
packs, normalizing them into a strongly-typed ModuleManifest object
used during pack discovery.

It works by reading JSON from disk, ensuring the root is a string-keyed
mapping, checking required fields and schema version, and returning
either a populated manifest or None when the payload is invalid.

It defines constants for the current schema version, default enabled
flag, default task-files list, and uses message-driven field keys and
encoding settings.

The ModuleManifest dataclass captures the validated manifest fields:
module_id, label, version, schema_version, enabled, and a tuple of
task-file paths.

Helper functions _normalize_root_object, _read_json_object,
_required_non_empty_string, _required_int, _parse_task_files,
_parse_enabled, and _resolve_label perform type checks, strip strings,
enforce boolean and integer constraints, normalize task-file lists, and
derive a label with a sensible fallback to module_id.

The core _build_manifest function ties these together, rejecting
payloads with missing or mismatched required fields, wrong schema
version, invalid enabled type, or malformed task-files, and returns a
ModuleManifest only when all checks pass.

The public load_manifest function is the entry point: it calls
_read_json_object on the given Path and, if successful, delegates to
_build_manifest, making this module the single place where manifest
files are parsed and validated for the rest of the system.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from pathlib import Path

from messages import (
    EMPTY_STRING_DINAMIC_POSTFIX_2D5Z,
    KEY_ENABLED_DINAMIC_POSTFIX_2D5Z,
    KEY_ID_DINAMIC_POSTFIX_2D5Z,
    KEY_LABEL_DINAMIC_POSTFIX_2D5Z,
    KEY_SCHEMA_VERSION_DINAMIC_POSTFIX_2D5Z,
    KEY_TASK_FILES_DINAMIC_POSTFIX_2D5Z,
    KEY_VERSION_DINAMIC_POSTFIX_2D5Z,
    MANIFEST_ENCODING_DINAMIC_POSTFIX_2D5Z,
)

SCHEMA_VERSION_CURRENT: int = 1
DEFAULT_ENABLED_WHEN_KEY_MISSING: bool = True
DEFAULT_TASK_FILES: tuple[()] = ()


@dataclass(frozen=True, slots=True)
class ModuleManifest:
    """Validated module manifest used by pack discovery.

    Attributes:
        module_id: Stable non-empty pack identifier.
        label: Human-readable name for UI and diagnostics.
        version: Pack semantic version or revision string.
        schema_version: Manifest schema version supported by loader.
        enabled: Flag that controls whether pack is discoverable.
        task_files: Relative paths to declarative task files.
    """

    module_id: str
    label: str
    version: str
    schema_version: int
    enabled: bool
    task_files: tuple[str, ...]


def _normalize_root_object(raw_payload: object) -> dict[str, object] | None:
    """Validate that JSON root object has string keys only.

    Args:
        raw_payload: Value produced by ``json.loads``.

    Returns:
        Copy of the source mapping when valid, otherwise ``None``.
    """
    if not isinstance(raw_payload, dict):
        return None

    result: dict[str, object] = {}
    for raw_key, value in raw_payload.items():
        if not isinstance(raw_key, str):
            return None
        result[raw_key] = value
    return result


def _read_json_object(path: Path) -> dict[str, object] | None:
    """Read and parse JSON object from disk.

    Args:
        path: Filesystem path to manifest file.

    Returns:
        Parsed payload when file is readable and valid, otherwise
        ``None``.
    """
    try:
        text: str = path.read_text(
            encoding=MANIFEST_ENCODING_DINAMIC_POSTFIX_2D5Z,
        )
        raw_payload: object = json.loads(text)
    except (OSError, json.JSONDecodeError):
        return None

    return _normalize_root_object(raw_payload)


def _required_non_empty_string(
    *,
    payload: dict[str, object],
    key: str,
) -> str | None:
    """Extract required non-empty string value from payload.

    Args:
        payload: Root manifest mapping.
        key: Name of required field.

    Returns:
        Stripped string value or ``None`` when invalid.
    """
    raw_value: object | None = payload.get(key)
    if not isinstance(raw_value, str):
        return None

    value: str = raw_value.strip()
    return value or None


def _required_int(payload: dict[str, object], key: str) -> int | None:
    """Extract required integer field excluding booleans.

    Args:
        payload: Root manifest mapping.
        key: Name of required integer field.

    Returns:
        Integer value or ``None`` when invalid.
    """
    raw_value: object | None = payload.get(key)
    if isinstance(raw_value, bool) or not isinstance(raw_value, int):
        return None
    return raw_value


def _parse_task_files(raw_task_files: object) -> tuple[str, ...] | None:
    """Convert raw task files value to normalized tuple.

    Args:
        raw_task_files: Candidate payload value for task files field.

    Returns:
        Tuple of non-empty stripped paths or ``None`` when invalid.
    """
    if raw_task_files is None or not isinstance(raw_task_files, list):
        return None

    task_files: list[str] = []
    for item in raw_task_files:
        if not isinstance(item, str):
            continue
        path_value: str = item.strip()
        if path_value:
            task_files.append(path_value)
    return tuple(task_files)


def _parse_enabled(payload: dict[str, object]) -> bool | None:
    """Extract optional enabled flag with strict boolean check.

    Args:
        payload: Root manifest mapping.

    Returns:
        Enabled value or ``None`` when field type is invalid.
    """
    raw_enabled: object = payload.get(
        KEY_ENABLED_DINAMIC_POSTFIX_2D5Z,
        DEFAULT_ENABLED_WHEN_KEY_MISSING,
    )
    return raw_enabled if isinstance(raw_enabled, bool) else None


def _resolve_label(*, payload: dict[str, object], module_id: str) -> str:
    """Resolve module label with fallback to module identifier.

    Args:
        payload: Root manifest mapping.
        module_id: Validated module identifier.

    Returns:
        Label value or fallback identifier.
    """
    raw_label: object | None = payload.get(KEY_LABEL_DINAMIC_POSTFIX_2D5Z)
    label: str = (
        raw_label.strip()
        if isinstance(raw_label, str)
        else EMPTY_STRING_DINAMIC_POSTFIX_2D5Z
    )
    return label or module_id


def _build_manifest(payload: dict[str, object]) -> ModuleManifest | None:
    """Build validated module manifest from parsed payload.

    Args:
        payload: Root manifest mapping.

    Returns:
        Manifest object when payload is valid, otherwise ``None``.
    """
    module_id: str | None = _required_non_empty_string(
        payload=payload,
        key=KEY_ID_DINAMIC_POSTFIX_2D5Z,
    )
    version: str | None = _required_non_empty_string(
        payload=payload,
        key=KEY_VERSION_DINAMIC_POSTFIX_2D5Z,
    )
    schema_version: int | None = _required_int(
        payload,
        KEY_SCHEMA_VERSION_DINAMIC_POSTFIX_2D5Z,
    )

    if module_id is None or version is None or schema_version is None:
        return None
    if schema_version != SCHEMA_VERSION_CURRENT:
        return None

    enabled: bool | None = _parse_enabled(payload)
    if enabled is None:
        return None

    raw_task_files: object = payload.get(
        KEY_TASK_FILES_DINAMIC_POSTFIX_2D5Z,
        DEFAULT_TASK_FILES,
    )
    task_files: tuple[str, ...] | None = _parse_task_files(raw_task_files)
    if task_files is None:
        return None

    label: str = _resolve_label(payload=payload, module_id=module_id)
    return ModuleManifest(
        module_id=module_id,
        label=label,
        version=version,
        schema_version=schema_version,
        enabled=enabled,
        task_files=task_files,
    )


def load_manifest(path: Path) -> ModuleManifest | None:
    """Load, parse, and validate module manifest from file.

    Args:
        path: Filesystem path to ``module.json`` file.

    Returns:
        Validated module manifest or ``None`` when invalid.
    """
    payload: dict[str, object] | None = _read_json_object(path)
    return _build_manifest(payload) if payload is not None else None
