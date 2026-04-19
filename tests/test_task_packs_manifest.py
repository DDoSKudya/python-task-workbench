"""
Tests for pack manifest loading (:mod:`task_packs.module_manifest`).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from task_packs.module_manifest import load_manifest

_SCHEMA_V1: Final[int] = 1
_SCHEMA_BAD: Final[int] = 99
_MINIMAL_ID: Final[str] = "test-pack"
_TASK_FILE: Final[str] = "tasks.yaml"


def test_load_manifest_valid_minimal(tmp_path: Path) -> None:
    """Load a minimal v1 manifest from disk.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "module.json"
    path.write_text(
        json.dumps(
            {
                "id": _MINIMAL_ID,
                "version": "1.0.0",
                "schema_version": _SCHEMA_V1,
                "task_files": [_TASK_FILE],
            }
        ),
        encoding="utf-8",
    )
    manifest = load_manifest(path)
    assert manifest is not None
    assert manifest.module_id == _MINIMAL_ID
    assert manifest.schema_version == _SCHEMA_V1
    assert manifest.task_files == (_TASK_FILE,)


def test_load_manifest_missing_returns_none(tmp_path: Path) -> None:
    """Absent files return ``None`` without raising.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    assert load_manifest(tmp_path / "none.json") is None


def test_load_manifest_invalid_json_returns_none(tmp_path: Path) -> None:
    """Malformed JSON returns ``None``.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    assert load_manifest(bad) is None


def test_load_manifest_wrong_schema_returns_none(tmp_path: Path) -> None:
    """Unsupported schema version returns ``None``.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "module.json"
    path.write_text(
        json.dumps(
            {
                "id": "x",
                "version": "1",
                "schema_version": _SCHEMA_BAD,
                "task_files": ["a.yaml"],
            }
        ),
        encoding="utf-8",
    )
    assert load_manifest(path) is None


def test_load_manifest_invalid_enabled_returns_none(tmp_path: Path) -> None:
    """Non-boolean ``enabled`` field rejects the manifest.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        None.
    """
    path = tmp_path / "module.json"
    path.write_text(
        json.dumps(
            {
                "id": "x",
                "version": "1",
                "schema_version": _SCHEMA_V1,
                "enabled": "yes",
                "task_files": ["a.yaml"],
            }
        ),
        encoding="utf-8",
    )
    assert load_manifest(path) is None
