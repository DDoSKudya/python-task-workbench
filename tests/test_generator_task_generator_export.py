"""Smoke tests for :mod:`generator.task_generator` public API."""

from __future__ import annotations

from typing import Final

from generator.task_generator import TaskGenerator

_SEED: Final[int] = 123


def test_task_generator_instantiation() -> None:
    """Constructor stores the configured RNG seed.

    Returns:
        None.
    """
    gen = TaskGenerator(seed=_SEED)
    assert gen.seed == _SEED
