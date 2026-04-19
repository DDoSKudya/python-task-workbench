"""Tests for saving GUI/CLI defaults (:mod:`core.config`)."""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path
from typing import Final

import pytest

import core.config as cc
from core.paths import ROOT

_NEW_DEFAULT_COUNT: Final[int] = 7
_CONFIG_KEY_COUNT: Final[str] = "default_count"


def test_save_defaults_config_updates_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persist updated session count through ``save_defaults_config``.

    Args:
        tmp_path: Pytest temporary directory.
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        None.
    """
    src = ROOT / "config" / "config.json"
    dst = tmp_path / "config.json"
    shutil.copyfile(src, dst)
    monkeypatch.setattr(cc, "CONFIG_PATH", dst)

    before = cc.load_defaults()
    new_session = replace(before.session, count=_NEW_DEFAULT_COUNT)
    cc.save_defaults_config(new_session, before.ui)

    raw = json.loads(dst.read_text(encoding="utf-8"))
    assert raw[_CONFIG_KEY_COUNT] == _NEW_DEFAULT_COUNT
