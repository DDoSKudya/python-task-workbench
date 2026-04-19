"""
This module generates a batch of tasks for a CLI “story mode”, applying
history-based exclusions, deterministic randomness, optional story
metadata, and task inversion.

It works by deriving per-stream seeds from an optional base seed, using
a Blake2b-based hash to produce deterministic pseudo-random integers
and floats, and falling back to secrets when no seed is provided.

It defines constants and type aliases for story ID ranges, random
streams, hash sizes, and small offsets, plus logical stream names for
story IDs and inversion probabilities.

Helper functions read prior task history to compute recent task IDs and
families, determine previous-session context, and build exclusion sets
that avoid immediate repeats and collisions within the current batch.

Task generation uses a configured TaskGenerator per batch index, first
trying to honor both task and family exclusions, then relaxing family
exclusions if that proves too restrictive.

If story mode is enabled, each generated task is decorated with a story
prefix in its description and extra input metadata (session ID, step
index, total steps), and may be transformed into an “inverse” variant
based on a per-step random probability.

The main function generate_tasks_batch orchestrates these steps for the
requested count, tracking which tasks and families have been used in
the batch, and returns the resulting ordered list of enriched tasks for
use by the surrounding application.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

import secrets
from dataclasses import replace
from typing import Final

from generator.app_config import AppConfig
from generator.models import Task, task_family_from_id
from generator.settings import NO_REPEAT_FAMILY_WINDOW, NO_REPEAT_TASK_WINDOW
from generator.task_generator import TaskGenerator
from messages import (
    STORY_ID_PREFIX_DINAMIC_POSTFIX_80ET,
    STORY_INPUT_KEY_DINAMIC_POSTFIX_80ET,
    STORY_PREFIX_TMPL_DINAMIC_POSTFIX_80ET,
    STORY_SESSION_ID_KEY_DINAMIC_POSTFIX_80ET,
    STORY_STEP_KEY_DINAMIC_POSTFIX_80ET,
    STORY_TOTAL_STEPS_KEY_DINAMIC_POSTFIX_80ET,
)

from .inverse import inverse_task
from .state import load_history_from_state

STORY_SEED_OFFSET: Final[int] = 777
STORY_ID_MIN: Final[int] = 1000
STORY_ID_MAX: Final[int] = 9999
FIRST_BATCH_INDEX: Final[int] = 0
STEP_OFFSET: Final[int] = 1
RANDOM_RANGE_OFFSET: Final[int] = 1
HASH_DIGEST_SIZE: Final[int] = 8
STREAM_STORY_ID: Final[str] = "story-id"
STREAM_INVERSE_RATE: Final[str] = "inverse-rate"

type TaskId = str
type TaskFamily = str


def _seed_with_offset(base_seed: int | None, offset: int) -> int | None:
    """Derive a deterministic seed from a base seed and offset.

    Args:
        base_seed: Base seed value or ``None``.
        offset: Offset applied for independent random streams.

    Returns:
        Derived seed value or ``None``.
    """
    return None if base_seed is None else base_seed + offset


def _hashed_number(*, seed: int, stream: str, step: int) -> int:
    """Build a deterministic integer from seed and stream metadata.

    Args:
        seed: Base deterministic seed.
        stream: Logical random stream identifier.
        step: Zero-based step inside the stream.

    Returns:
        Stable unsigned integer.
    """
    payload = f"{seed}:{stream}:{step}".encode()
    digest = hashlib.blake2b(
        payload,
        digest_size=HASH_DIGEST_SIZE,
    ).digest()
    return int.from_bytes(digest, byteorder="big")


def _randbelow(*, seed: int | None, stream: str, step: int, upper: int) -> int:
    """Return pseudo-random integer in ``[0, upper)``.

    Args:
        seed: Base deterministic seed or ``None``.
        stream: Logical random stream identifier.
        step: Zero-based step inside the stream.
        upper: Exclusive upper bound.

    Returns:
        Pseudo-random integer in ``[0, upper)``.
    """
    if seed is None:
        return secrets.randbelow(upper)
    return _hashed_number(seed=seed, stream=stream, step=step) % upper


def _random_unit(*, seed: int | None, stream: str, step: int) -> float:
    """Return pseudo-random float in ``[0.0, 1.0)``.

    Args:
        seed: Base deterministic seed or ``None``.
        stream: Logical random stream identifier.
        step: Zero-based step inside the stream.

    Returns:
        Pseudo-random float in ``[0.0, 1.0)``.
    """
    if seed is None:
        max_value = 1 << 53
        return secrets.randbelow(max_value) / max_value
    max_value = 1 << 64
    hashed = _hashed_number(seed=seed, stream=stream, step=step)
    return hashed / max_value


def _build_story_id(
    config: AppConfig, *, story_seed: int | None
) -> str | None:
    """Build a story session id if story mode is enabled.

    Args:
        config: Application config.
        story_seed: Random seed for story-specific values.

    Returns:
        A story id string or None if story mode is disabled.
    """
    if not config.story_mode:
        return None
    span = STORY_ID_MAX - STORY_ID_MIN + RANDOM_RANGE_OFFSET
    suffix = STORY_ID_MIN + _randbelow(
        seed=story_seed,
        stream=STREAM_STORY_ID,
        step=FIRST_BATCH_INDEX,
        upper=span,
    )
    return f"{STORY_ID_PREFIX_DINAMIC_POSTFIX_80ET}{suffix}"


def _recent_families_from_history(
    history: Sequence[TaskId],
) -> set[TaskFamily]:
    """Extract recently used task families from history.

    Args:
        history: Full task id history.

    Returns:
        Set of task families observed in the configured recent window.
    """
    return {
        task_family_from_id(task_id)
        for task_id in history[-NO_REPEAT_FAMILY_WINDOW:]
    }


def _recent_task_ids_from_history(history: Sequence[TaskId]) -> set[TaskId]:
    """Extract recently used task ids from history.

    Args:
        history: Full task id history.

    Returns:
        Set of task ids observed in the configured recent window.
    """
    return set(history[-NO_REPEAT_TASK_WINDOW:])


def _previous_history_context(
    history: Sequence[TaskId],
) -> tuple[TaskId | None, TaskFamily | None]:
    """Build previous-task context used for first-item exclusions.

    Args:
        history: Full task id history.

    Returns:
        Tuple ``(last_task_id, last_task_family)``.
    """
    last_task_id = history[-1] if history else None
    last_family = (
        task_family_from_id(last_task_id) if last_task_id is not None else None
    )
    return (last_task_id, last_family)


def _excluded_task_ids(
    *,
    recent_task_ids: set[TaskId],
    used_in_batch: set[TaskId],
    idx: int,
    previous_last_task_id: TaskId | None,
) -> set[TaskId]:
    """Compute task id exclusions for the current item.

    Args:
        recent_task_ids: Task ids from the recent history window.
        used_in_batch: Task ids already generated in this batch.
        idx: Zero-based batch index.
        previous_last_task_id: Last task id from previous session, if
        any.

    Returns:
        Set of task ids to exclude for this generation attempt.
    """
    excluded = set(used_in_batch) | set(recent_task_ids)
    if idx == FIRST_BATCH_INDEX and previous_last_task_id is not None:
        excluded.add(previous_last_task_id)
    return excluded


def _excluded_families(
    *,
    recent_families: set[TaskFamily],
    used_families_in_batch: set[TaskFamily],
    idx: int,
    previous_family: TaskFamily | None,
) -> set[TaskFamily]:
    """Compute task family exclusions for the current item.

    Args:
        recent_families: Families from the recent history window.
        used_families_in_batch: Families already used in this batch.
        idx: Zero-based batch index.
        previous_family: Family of the last task from previous session,
        if any.

    Returns:
        Set of task families to exclude for this generation attempt.
    """
    excluded = set(used_families_in_batch) | set(recent_families)
    if idx == FIRST_BATCH_INDEX and previous_family is not None:
        excluded.add(previous_family)
    return excluded


def _generate_task(
    *,
    generator: TaskGenerator,
    topic: str,
    excluded_task_ids: set[TaskId],
    excluded_families: set[TaskFamily],
) -> Task:
    """Generate a task with exclusions, falling back if too restrictive.

    Args:
        generator: Task generator instance.
        topic: Desired topic.
        excluded_task_ids: Task ids to exclude.
        excluded_families: Task families to exclude.

    Returns:
        Generated task.
    """
    try:
        return generator.generate(
            topic=topic,
            excluded_task_ids=excluded_task_ids,
            excluded_families=excluded_families,
        )
    except ValueError:
        return generator.generate(
            topic=topic, excluded_task_ids=excluded_task_ids
        )


def _with_story_metadata(
    task: Task, *, story_id: str, step: int, total_steps: int
) -> Task:
    """Attach story metadata into task description and input data.

    Args:
        task: Original task.
        story_id: Session identifier.
        step: Current step index (1-based).
        total_steps: Total number of steps in the session.

    Returns:
        Updated task instance.
    """
    prefix = STORY_PREFIX_TMPL_DINAMIC_POSTFIX_80ET.format(
        story_id=story_id, step=step, total_steps=total_steps
    )
    return replace(
        task,
        description=f"{prefix}{task.description}",
        input_data={
            **task.input_data,
            STORY_INPUT_KEY_DINAMIC_POSTFIX_80ET: {
                STORY_SESSION_ID_KEY_DINAMIC_POSTFIX_80ET: story_id,
                STORY_STEP_KEY_DINAMIC_POSTFIX_80ET: step,
                STORY_TOTAL_STEPS_KEY_DINAMIC_POSTFIX_80ET: total_steps,
            },
        },
    )


def _maybe_inverse(
    task: Task,
    *,
    story_seed: int | None,
    rate: float,
    step: int,
) -> Task:
    """Optionally transform a task into its inverse form.

    Args:
        task: Original task.
        story_seed: Random seed for story-specific values.
        rate: Probability of inversion in range [0, 1].
        step: Zero-based batch position.

    Returns:
        Possibly transformed task.
    """
    probability = _random_unit(
        seed=story_seed,
        stream=STREAM_INVERSE_RATE,
        step=step,
    )
    if probability >= rate:
        return task
    inversed = inverse_task(task)
    return task if inversed is None else inversed


def _build_task_generator(
    *, config: AppConfig, current_seed: int | None
) -> TaskGenerator:
    """Build a configured task generator for one batch index.

    Args:
        config: Application configuration.
        current_seed: Per-item seed value.

    Returns:
        Configured ``TaskGenerator`` instance.
    """
    return TaskGenerator(
        seed=current_seed,
        stage=config.stage,
        data_volume=config.data_volume,
        data_order=config.data_order,
        data_quality=config.data_quality,
        profile=config.profile,
        domain=config.domain,
        surprise_me=config.surprise_me,
        focus_tool=config.focus_tool,
        content_pack=config.content_pack,
    )


def generate_tasks_batch(config: AppConfig) -> list[Task]:
    """Generate a batch of tasks for CLI with history-aware exclusions.

    Args:
        config: Application configuration for the session.

    Returns:
        Generated tasks in order.
    """
    story_seed = _seed_with_offset(config.seed, STORY_SEED_OFFSET)
    story_id = _build_story_id(config, story_seed=story_seed)
    history: list[TaskId] = load_history_from_state(config.state_file)
    previous_last_task_id, previous_family = _previous_history_context(history)
    recent_task_ids = _recent_task_ids_from_history(history)
    recent_families = _recent_families_from_history(history)
    used_in_batch: set[TaskId] = set()
    used_families_in_batch: set[TaskFamily] = set()
    generated: list[Task] = []
    total_steps = max(config.count, config.session_size)
    for idx in range(config.count):
        current_seed = _seed_with_offset(config.seed, idx)
        generator = _build_task_generator(
            config=config, current_seed=current_seed
        )
        excluded_task_ids = _excluded_task_ids(
            recent_task_ids=recent_task_ids,
            used_in_batch=used_in_batch,
            idx=idx,
            previous_last_task_id=previous_last_task_id,
        )
        excluded_families = _excluded_families(
            recent_families=recent_families,
            used_families_in_batch=used_families_in_batch,
            idx=idx,
            previous_family=previous_family,
        )
        task = _generate_task(
            generator=generator,
            topic=config.topic,
            excluded_task_ids=excluded_task_ids,
            excluded_families=excluded_families,
        )
        if story_id is not None:
            step = idx + STEP_OFFSET
            task = _with_story_metadata(
                task, story_id=story_id, step=step, total_steps=total_steps
            )
        task = _maybe_inverse(
            task,
            story_seed=story_seed,
            rate=config.inverse_rate,
            step=idx,
        )
        used_in_batch.add(task.task_id)
        used_families_in_batch.add(task_family_from_id(task.task_id))
        generated.append(task)
    return generated
