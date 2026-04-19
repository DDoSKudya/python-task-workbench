"""Tests for :mod:`generator.fake_data`."""

from __future__ import annotations

from typing import Final

import pytest

from generator.fake_data import FakeDataFactory, LocalRng

_SEED_A: Final[int] = 12345
_SEED_B: Final[int] = 1
_RANDINT_HI: Final[int] = 100
_BAD_BELOW: Final[int] = 0
_RANDINT_LOW: Final[int] = 5
_RANDINT_HIGH: Final[int] = 1
_FACTORY_SEED: Final[int] = 99


def test_local_rng_reproducible_with_seed() -> None:
    """Identical seeds yield identical random sequences.

    Returns:
        None.
    """
    first = LocalRng(_SEED_A)
    second = LocalRng(_SEED_A)
    assert first.randint(0, _RANDINT_HI) == second.randint(0, _RANDINT_HI)
    assert first.random() == second.random()


def test_local_rng_randbelow_requires_positive_upper() -> None:
    """``randbelow`` rejects non-positive bounds.

    Returns:
        None.
    """
    rng = LocalRng(_SEED_B)
    with pytest.raises(ValueError):
        rng.randbelow(_BAD_BELOW)


def test_local_rng_randint_requires_ordered_bounds() -> None:
    """``randint`` rejects inverted bounds.

    Returns:
        None.
    """
    rng = LocalRng(_SEED_B)
    with pytest.raises(ValueError):
        rng.randint(_RANDINT_LOW, _RANDINT_HIGH)


def test_local_rng_choice_empty_raises() -> None:
    """``choice`` on an empty sequence raises.

    Returns:
        None.
    """
    rng = LocalRng(_SEED_B)
    with pytest.raises(IndexError):
        rng.choice(())


def test_fake_data_factory_word_returns_str() -> None:
    """Factory produces string tokens.

    Returns:
        None.
    """
    factory = FakeDataFactory(seed=_FACTORY_SEED)
    assert isinstance(factory.fake.word(), str)
