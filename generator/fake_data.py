"""
This module provides deterministic pseudo-random generation and
word-faking utilities used by task generation code.

It works by wrapping a small custom RNG, LocalRng, and a “faker-like”
provider inside FakeDataFactory, giving task packs a stable source of
randomness and text tokens, with a graceful fallback when the external
faker library is unavailable.

It defines constants for fallback words, LCG parameters, and RNG
scaling, plus a generic type variable used in typed RNG methods.

The LocalRng class implements a 64-bit linear congruential generator
with methods akin to random.Random: randbelow, random, randint, choice,
choices, and in-place shuffle.

Two protocols, FakerLike and SeedableFaker, specify the minimal
interface the factory expects from a faker implementation and
optionally a seeding hook.

FakeDataFactory constructs a LocalRng, tries to create a faker.Faker
instance configured with project locales, seeds it when possible, and
otherwise falls back to _FallbackFaker, which produces simple word
tokens by sampling from a small fixed vocabulary via the shared RNG.
"""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence

import secrets
from typing import Final, Protocol, TypeVar, runtime_checkable

from .settings import FAKER_LOCALES

FALLBACK_WORDS: Final[tuple[str, ...]] = (
    "alpha",
    "beta",
    "gamma",
    "delta",
    "omega",
    "flux",
    "spark",
)
_DEFAULT_SEED_BITS: Final[int] = 64
_LCG_MODULUS: Final[int] = 2**64
_LCG_MULTIPLIER: Final[int] = 6364136223846793005
_LCG_INCREMENT: Final[int] = 1442695040888963407
_RANDOM_UNIT_SCALE: Final[float] = float(2**64)
_T = TypeVar("_T")


class LocalRng:
    """Deterministic pseudo-random generator for task data.

    This class intentionally implements only the subset of methods that
    the project uses from ``random.Random``.
    """

    def __init__(self, seed: int | None) -> None:
        """Initialize RNG state.

        Args:
            seed: Optional deterministic seed.
        """
        self._state = (
            seed % _LCG_MODULUS
            if seed is not None
            else secrets.randbits(_DEFAULT_SEED_BITS)
        )

    def _next_uint64(self) -> int:
        """Advance generator state and return next 64-bit value.

        Returns:
            Unsigned 64-bit pseudo-random integer.
        """
        self._state = (
            (_LCG_MULTIPLIER * self._state) + _LCG_INCREMENT
        ) % _LCG_MODULUS
        return self._state

    def randbelow(self, upper: int) -> int:
        """Return integer in ``[0, upper)``.

        Args:
            upper: Exclusive upper bound.

        Returns:
            Pseudo-random integer in range.

        Raises:
            ValueError: If upper is not positive.
        """
        if upper <= 0:
            raise ValueError("upper must be positive")
        return self._next_uint64() % upper

    def random(self) -> float:
        """Return float in ``[0.0, 1.0)``.

        Returns:
            Pseudo-random floating-point value.
        """
        return self._next_uint64() / _RANDOM_UNIT_SCALE

    def randint(self, a: int, b: int) -> int:
        """Return integer in inclusive range ``[a, b]``.

        Args:
            a: Lower inclusive bound.
            b: Upper inclusive bound.

        Returns:
            Pseudo-random integer.

        Raises:
            ValueError: If ``a > b``.
        """
        if a > b:
            raise ValueError("a must be <= b")
        return a + self.randbelow((b - a) + 1)

    def choice(self, population: Sequence[_T]) -> _T:
        """Return one random item from a non-empty sequence.

        Args:
            population: Source sequence.

        Returns:
            Selected item.

        Raises:
            IndexError: If the sequence is empty.
        """
        if not population:
            raise IndexError("Cannot choose from an empty sequence")
        return population[self.randbelow(len(population))]

    def choices(self, population: Sequence[_T], *, k: int) -> list[_T]:
        """Return ``k`` items sampled with replacement.

        Args:
            population: Source sequence.
            k: Number of items to sample.

        Returns:
            List of sampled items.
        """
        return [self.choice(population) for _ in range(k)]

    def shuffle(self, seq: MutableSequence[_T]) -> None:
        """Shuffle sequence in-place with Fisher-Yates algorithm.

        Args:
            seq: Mutable sequence to shuffle.
        """
        for idx in range(len(seq) - 1, 0, -1):
            swap_idx = self.randbelow(idx + 1)
            seq[idx], seq[swap_idx] = seq[swap_idx], seq[idx]


@runtime_checkable
class FakerLike(Protocol):
    """Minimal faker surface used by task recipes."""

    def word(self) -> str:
        """Return a random word token.

        Returns:
            Generated word token.
        """
        ...


@runtime_checkable
class SeedableFaker(FakerLike, Protocol):
    """Faker providers that support per-instance seeding."""

    def seed_instance(self, seed: int) -> None:
        """Seed the faker instance.

        Args:
            seed: Deterministic seed value.

        Returns:
            None.
        """
        ...


class FakeDataFactory:
    """Factory exposing RNG and word generation for task packs."""

    def __init__(self, seed: int | None) -> None:
        """Initialize factory with deterministic random generator.

        Args:
            seed: Optional seed for deterministic generation.

        Returns:
            None.
        """
        self.rng = LocalRng(seed)
        self.fake = self._build_faker()
        if seed is not None and isinstance(self.fake, SeedableFaker):
            self.fake.seed_instance(seed)

    def _build_faker(self) -> FakerLike:
        """Build faker implementation with graceful fallback.

        Returns:
            Faker-compatible provider.
        """
        try:
            from faker import Faker

            return Faker(FAKER_LOCALES)
        except Exception:
            return _FallbackFaker(self.rng)


class _FallbackFaker:
    """Fallback when ``faker`` is unavailable."""

    def __init__(self, rng: LocalRng) -> None:
        """Initialize fallback faker provider.

        Args:
            rng: Random generator used for fallback word selection.

        Returns:
            None.
        """
        self.rng = rng

    def word(self) -> str:
        """Return one fallback word token.

        Returns:
            Word sampled from ``FALLBACK_WORDS``.
        """
        return self.rng.choice(FALLBACK_WORDS)
