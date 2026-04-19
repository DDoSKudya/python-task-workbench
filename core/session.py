"""
This module builds a task session by selecting concrete task variants
from configured task packs, ensuring uniqueness and optional
determinism via a seed.

It works by deriving a per-position seed, instantiating a TaskGenerator
and FakeDataFactory, querying all variants from the selected packs,
filtering out variants already used in the session, and then choosing
one eligible variant per position.

It defines constants describing the layout of Variant tuples, hashing
parameters, and error messages, along with helpers for type-guarding
dicts, computing per-task seeds, merging variants across packs, and
normalizing payloads from dicts or dataclasses into string-keyed
dictionaries.

The _choose_position function encapsulates the deterministic index
selection, using a Blake2b hash of the session seed, position index,
and variant list length, or falling back to secrets.randbelow when no
seed is provided.

The main function build_session orchestrates the loop over task
positions, enforces that variants exist and that there are enough
unique variants for the requested count, converts the chosen variants
payload into a Task, and finally returns a TaskSession containing all
tasks wired to the given SessionConfig.

Within the larger application, this module is responsible for turning
high-level session configuration and pack selection into a concrete,
reproducible set of tasks that the learner will see and solve.
"""

from __future__ import annotations

import hashlib

import secrets
from dataclasses import asdict, is_dataclass
from typing import Final, TypeGuard

from generator import FakeDataFactory, TaskGenerator
from messages import (
    ERR_NO_VARIANTS_DINAMIC_POSTFIX_ZQK1,
    ERR_NOT_ENOUGH_VARIANTS_DINAMIC_POSTFIX_ZQK1,
    ERR_UNSUPPORTED_PAYLOAD_DINAMIC_POSTFIX_ZQK1,
)
from task_packs import get_variants as get_pack_variants
from task_packs.pack_types import Variant

from .models import SessionConfig, Task, TaskSession

VARIANT_PAYLOAD_FACTORY_INDEX: Final[int] = 0
VARIANT_ID_INDEX: Final[int] = 2
SESSION_POSITION_OFFSET: Final[int] = 1
_HASH_SIZE_BYTES: Final[int] = 8
ERR_UPPER_MUST_BE_POSITIVE: Final[str] = "upper must be positive"


def _is_str_key_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    """Return whether value is a dictionary with string keys.

    Args:
        value: Candidate payload object.

    Returns:
        ``True`` when ``value`` is ``dict[str, object]``-compatible.
    """
    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)


def _seed_for_position(base_seed: int | None, index: int) -> int | None:
    """Derive deterministic per-task seed from session seed and index.

    Args:
        base_seed: Session-level seed or ``None`` for non-deterministic
        mode.
        index: Zero-based task position in the session.

    Returns:
        Derived seed for the current task position or ``None``.
    """
    return None if base_seed is None else base_seed + index


def _variants_for_pack(
    pack_name: str, generator: TaskGenerator
) -> list[Variant]:
    """Return all task variants for one pack.

    Args:
        pack_name: Pack identifier.
        generator: Task generator seeded for current position.

    Returns:
        List of variants returned by the pack implementation.
    """
    return get_pack_variants(pack_name, generator)


def _merged_variants_for_packs(
    *,
    selected_packs: tuple[str, ...],
    generator: TaskGenerator,
) -> list[tuple[str, Variant]]:
    """Collect all variants across the selected pack list.

    Args:
        selected_packs: Ordered pack identifiers selected for the
        session.
        generator: Task generator seeded for current position.

    Returns:
        Flat list of ``(pack_name, variant)`` pairs.
    """
    combined: list[tuple[str, Variant]] = []
    for pack in selected_packs:
        combined.extend(
            (pack, variant) for variant in _variants_for_pack(pack, generator)
        )
    return combined


def _payload_from_candidate(candidate: object) -> dict[str, object]:
    """Normalize task payload returned by a variant factory.

    Args:
        candidate: Factory result, expected ``dict`` or dataclass
        instance.

    Returns:
        Payload dictionary with string keys.

    Raises:
        TypeError: If payload type is unsupported.
    """
    if isinstance(candidate, dict):
        return {str(key): value for key, value in candidate.items()}
    if is_dataclass(candidate) and not isinstance(candidate, type):
        payload = asdict(candidate)
        if _is_str_key_object_dict(payload):
            return payload
    msg = ERR_UNSUPPORTED_PAYLOAD_DINAMIC_POSTFIX_ZQK1.format(
        payload_type=type(candidate),
    )
    raise TypeError(msg)


def _eligible_variants(
    *,
    combined: list[tuple[str, Variant]],
    used_variant_ids: set[str],
) -> list[tuple[str, Variant]]:
    """Filter out variants that were already used in this session.

    Args:
        combined: Flat list of ``(pack_name, variant)`` pairs.
        used_variant_ids: Set of already chosen variant ids.

    Returns:
        Variants that can still be selected.
    """
    return [
        (pack, variant)
        for pack, variant in combined
        if variant[VARIANT_ID_INDEX] not in used_variant_ids
    ]


def _choose_position(*, seed: int | None, index: int, upper: int) -> int:
    """Choose an index in ``range(upper)`` deterministically when
    seeded.

    Args:
        seed: Base session seed or ``None`` for non-deterministic
        choice.
        index: Zero-based task position inside the session.
        upper: Exclusive upper bound for the chosen index.

    Returns:
        Integer in ``[0, upper)``.

    Raises:
        ValueError: When ``upper`` is not positive.
    """
    if upper <= 0:
        raise ValueError(ERR_UPPER_MUST_BE_POSITIVE)
    if seed is None:
        return secrets.randbelow(upper)
    payload = f"{seed}:{index}:{upper}".encode()
    digest = hashlib.blake2b(payload, digest_size=_HASH_SIZE_BYTES).digest()
    return int.from_bytes(digest, byteorder="big") % upper


def build_session(config: SessionConfig) -> TaskSession:
    """Build a task session with unique variants across all positions.

    Args:
        config: Session parameters and pack selection.

    Returns:
        Fully initialized task session.

    Raises:
        ValueError: If no variants exist or uniqueness is exhausted.
    """
    tasks: list[Task] = []
    used_variant_ids: set[str] = set()
    task_count = config.count

    for index in range(task_count):
        seed = _seed_for_position(config.seed, index)
        generator = TaskGenerator(seed=seed)
        factory = FakeDataFactory(seed=seed)
        combined = _merged_variants_for_packs(
            selected_packs=config.selected_packs,
            generator=generator,
        )
        if not combined:
            raise ValueError(ERR_NO_VARIANTS_DINAMIC_POSTFIX_ZQK1)
        eligible = _eligible_variants(
            combined=combined,
            used_variant_ids=used_variant_ids,
        )
        if not eligible:
            message = ERR_NOT_ENOUGH_VARIANTS_DINAMIC_POSTFIX_ZQK1.format(
                index=index + SESSION_POSITION_OFFSET,
                count=task_count,
            )
            raise ValueError(message)
        choice = _choose_position(
            seed=config.seed,
            index=index,
            upper=len(eligible),
        )
        pack_name, variant = eligible[choice]
        used_variant_ids.add(variant[VARIANT_ID_INDEX])
        payload_factory = variant[VARIANT_PAYLOAD_FACTORY_INDEX]
        payload = _payload_from_candidate(payload_factory(factory))
        tasks.append(Task.from_payload(payload, pack_name=pack_name))
    return TaskSession(config=config, tasks=tasks)
