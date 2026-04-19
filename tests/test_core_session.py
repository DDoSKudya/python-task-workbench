"""
Tests for session building and variant selection (:mod:`core.session`).
"""

from __future__ import annotations

from typing import Final
from unittest.mock import patch

import pytest

from core.models import SessionConfig
from core.session import (
    _choose_position,  # pyright: ignore[reportPrivateUsage]
)
from core.session import (
    _seed_for_position,  # pyright: ignore[reportPrivateUsage]
)
from core.session import (
    build_session,
)
from task_packs.pack_types import Variant

_SEED_BASE: Final[int] = 10
_SEED_INDEX_FOR_PAIR: Final[int] = 2
_NONE_SEED_INDEX: Final[int] = 3
_CHOOSE_SEED: Final[int] = 42
_CHOOSE_INDEX: Final[int] = 0
_UPPER_FIVE: Final[int] = 5
_UPPER_INVALID: Final[int] = 0
_VARIANT_TITLE: Final[str] = "T"
_PACK_ID: Final[str] = "fake-pack"
_SESSION_COUNT: Final[int] = 1
_SESSION_SEED: Final[int] = 123


def test_seed_for_position() -> None:
    """Map seed and index for deterministic RNG when seed is set.

    Returns:
        None.
    """
    assert _seed_for_position(None, _NONE_SEED_INDEX) is None
    assert _seed_for_position(_SEED_BASE, _SEED_INDEX_FOR_PAIR) == 12


def test_choose_position_deterministic_with_seed() -> None:
    """Same seed and index pick the same position in ``[0, upper)``.

    Returns:
        None.
    """
    first = _choose_position(
        seed=_CHOOSE_SEED,
        index=_CHOOSE_INDEX,
        upper=_UPPER_FIVE,
    )
    second = _choose_position(
        seed=_CHOOSE_SEED,
        index=_CHOOSE_INDEX,
        upper=_UPPER_FIVE,
    )
    assert first == second
    assert 0 <= first < _UPPER_FIVE


def test_choose_position_upper_invalid() -> None:
    """Reject a non-positive upper bound.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="positive"):
        _choose_position(seed=1, index=0, upper=_UPPER_INVALID)


def _one_variant(task_id: str = "v1") -> Variant:
    """Build a single fake pack variant triple.

    Args:
        task_id: Identifier embedded in the fake task dict.

    Returns:
        A :data:`task_packs.pack_types.Variant` tuple for patching.
    """

    def factory(_fake: object) -> dict[str, object]:
        return {
            "task_id": task_id,
            "title": _VARIANT_TITLE,
            "description": "",
            "input_data": {},
            "expected_result": 0,
        }

    return (factory, (), task_id)


def test_build_session_raises_when_no_variants() -> None:
    """Raise when the pack exposes no variants.

    Returns:
        None.
    """
    cfg = SessionConfig(
        selected_packs=("empty-pack",),
        count=_SESSION_COUNT,
        seed=1,
        strict_types=True,
    )
    with patch("core.session.get_pack_variants", return_value=[]):
        with pytest.raises(ValueError, match="variants"):
            build_session(cfg)


def test_build_session_smoke_with_mocked_variants() -> None:
    """Build a session when variants are injected.

    Returns:
        None.
    """
    variants = [_one_variant("t-a"), _one_variant("t-b")]
    cfg = SessionConfig(
        selected_packs=(_PACK_ID,),
        count=_SESSION_COUNT,
        seed=_SESSION_SEED,
        strict_types=True,
    )
    with patch(
        "core.session.get_pack_variants",
        return_value=variants,
    ):
        session = build_session(cfg)
    assert len(session.tasks) == 1
    assert session.tasks[0].task_id
