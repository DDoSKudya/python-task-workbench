"""Tests for :mod:`ui.dialogs.common`."""

from __future__ import annotations

from typing import Final

from ui.dialogs.common import pack_label

_UNKNOWN_PACK: Final[str] = "nonexistent_pack_id_xyz"


def test_pack_label_delegates_to_registry() -> None:
    """Unknown pack ids fall back to the raw id string.

    Returns:
        None.
    """
    label = pack_label(_UNKNOWN_PACK)
    assert label == _UNKNOWN_PACK
