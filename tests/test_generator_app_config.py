"""Tests for :mod:`generator.app_config`."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Final

import pytest

from generator.app_config import AppConfig
from generator.cli.resolve import resolve_config

_BAD_ASSIGN: Final[int] = 99


def test_app_config_is_frozen_dataclass() -> None:
    """Resolved config is frozen and rejects attribute assignment.

    Returns:
        None.
    """
    cfg = resolve_config()
    assert isinstance(cfg, AppConfig)
    with pytest.raises(FrozenInstanceError):
        setattr(cfg, "count", _BAD_ASSIGN)


def test_resolve_config_matches_app_config_fields() -> None:
    """Every ``AppConfig`` field exists on a resolved instance.

    Returns:
        None.
    """
    cfg = resolve_config()
    fields = {f.name for f in AppConfig.__dataclass_fields__.values()}
    for name in fields:
        assert hasattr(cfg, name)
