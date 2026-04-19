"""Tests for :mod:`generator.cli.resolve`."""

from __future__ import annotations

from typing import Final
from unittest.mock import patch

from generator.cli.resolve import resolve_config
from messages import (
    EMPTY_PACK_ID_DINAMIC_POSTFIX_DZXP,
    MIXED_PACK_ID_DINAMIC_POSTFIX_DZXP,
)

_DEFAULT_COLLECTIONS_PACK: Final[str] = "collections-level-1"
_LEX_FIRST: Final[str] = "alpha"
_LEX_SECOND: Final[str] = "zebra"
_SINGLE_PACK: Final[str] = "pack-a"


def test_resolve_config_content_pack_empty_when_no_packs() -> None:
    """Empty pack list selects the empty-pack sentinel.

    Returns:
        None.
    """
    with patch("generator.cli.resolve.list_available_packs", return_value=()):
        cfg = resolve_config()

    assert cfg.content_pack == EMPTY_PACK_ID_DINAMIC_POSTFIX_DZXP


def test_resolve_config_content_pack_uses_default_when_present() -> None:
    """Prefer the default collections pack when listed.

    Returns:
        None.
    """
    with patch(
        "generator.cli.resolve.list_available_packs",
        return_value=("other-pack", _DEFAULT_COLLECTIONS_PACK),
    ):
        cfg = resolve_config()

    assert cfg.content_pack == _DEFAULT_COLLECTIONS_PACK


def test_resolve_config_content_pack_fallback_lexicographic() -> None:
    """Without default pack, pick the lexicographically first id.

    Returns:
        None.
    """
    with patch(
        "generator.cli.resolve.list_available_packs",
        return_value=(_LEX_SECOND, _LEX_FIRST),
    ):
        cfg = resolve_config()

    assert cfg.content_pack == _LEX_FIRST


def test_resolve_config_mixed_pack_when_configured_and_packs_exist() -> None:
    """Mixed default resolves when packs are available.

    Returns:
        None.
    """
    with patch(
        "generator.cli.resolve.DEFAULT_CONTENT_PACK",
        MIXED_PACK_ID_DINAMIC_POSTFIX_DZXP,
    ):
        with patch(
            "generator.cli.resolve.list_available_packs",
            return_value=(_SINGLE_PACK,),
        ):
            cfg = resolve_config()
            expected = MIXED_PACK_ID_DINAMIC_POSTFIX_DZXP

    assert cfg.content_pack == expected


def test_resolve_config_has_expected_keys() -> None:
    """Resolved config exposes mode, count, and inverse rate in range.

    Returns:
        None.
    """
    with patch(
        "generator.cli.resolve.list_available_packs", return_value=("x",)
    ):
        cfg = resolve_config()

    assert cfg.mode in {"solve", "check", "coach"}
    assert isinstance(cfg.count, int)
    assert 0.0 <= cfg.inverse_rate <= 1.0
