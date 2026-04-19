"""Tests for :mod:`core.paths`."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.paths import (
    CONFIG_DIR_NAME,
    DATA_DIR_NAME,
    HISTORY_DIR_NAME,
    ROOT,
    ensure_data_directories,
)


def test_root_is_project_directory() -> None:
    """Assert ``ROOT`` is the project tree that owns ``core.paths``.

    The checkout directory name may differ (fork, rename); structure must
    match a normal install.

    Returns:
        None.
    """
    assert (ROOT / "pyproject.toml").is_file()
    assert (ROOT / "core" / "paths.py").is_file()


def test_path_constants_resolve_under_root() -> None:
    """Assert config path under ``ROOT`` resolves to an existing file.

    Returns:
        None.
    """
    assert (ROOT / CONFIG_DIR_NAME / "config.json").is_file()


def test_ensure_data_directories_creates_dirs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create config, data, and history dirs when attributes are
    patched.

    Args:
        tmp_path: Pytest temporary directory.
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        None.
    """
    root = tmp_path / "proj"
    root.mkdir()
    cfg = root / CONFIG_DIR_NAME
    data = root / DATA_DIR_NAME
    hist = data / HISTORY_DIR_NAME
    monkeypatch.setattr("core.paths.CONFIG_DIR", cfg)
    monkeypatch.setattr("core.paths.DATA_DIR", data)
    monkeypatch.setattr("core.paths.HISTORY_DIR", hist)
    ensure_data_directories()
    assert cfg.is_dir()
    assert data.is_dir()
    assert hist.is_dir()
