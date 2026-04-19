"""
Unit tests for :mod:`generator.cli.batch_generate` without disk packs.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Final
from unittest.mock import patch

from generator.app_config import AppConfig
from generator.cli.batch_generate import generate_tasks_batch
from generator.cli.resolve import resolve_config
from generator.models import GeneratedTask

_BATCH_COUNT: Final[int] = 2
_SESSION_SIZE: Final[int] = 2
_SEED: Final[int] = 42
_INVERSE_ZERO: Final[float] = 0.0
_SINGLE_COUNT: Final[int] = 1


def _minimal_app_config(tmp_state: str) -> AppConfig:
    """Build an :class:`AppConfig` for batch tests with a mock pack
    list.

    Args:
        tmp_state: Path string for the state file.

    Returns:
        Patched configuration suitable for batch generation.
    """
    with patch(
        "generator.cli.resolve.list_available_packs",
        return_value=("mock",),
    ):
        base = resolve_config()
    return replace(
        base,
        count=_BATCH_COUNT,
        session_size=_SESSION_SIZE,
        state_file=tmp_state,
        content_pack="mock-pack",
        story_mode=False,
        inverse_rate=_INVERSE_ZERO,
        seed=_SEED,
    )


def _fake_task(n: int) -> GeneratedTask:
    """Create a trivial generated task with a numeric suffix id.

    Args:
        n: Suffix used in ``task_id``.

    Returns:
        A :class:`GeneratedTask` instance.
    """
    return GeneratedTask.from_dict(
        {
            "task_id": f"auto-batch-{n}",
            "title": "T",
            "description": "d",
            "input_data": {},
            "expected_result": 0,
        }
    )


def test_generate_tasks_batch_returns_requested_count(
    tmp_path: Path,
) -> None:
    """Batch size matches ``cfg.count`` with a patched generator.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None.
    """
    state = str(tmp_path / "batch_state.pkl")
    cfg = _minimal_app_config(state)
    counter = {"n": 0}

    def fake_generate(**_kwargs: object) -> GeneratedTask:
        counter["n"] += 1
        return _fake_task(counter["n"])

    with patch(
        "generator.cli.batch_generate.load_history_from_state",
        return_value=[],
    ):
        with patch(
            "generator.cli.batch_generate._generate_task",
            side_effect=fake_generate,
        ):
            tasks = generate_tasks_batch(cfg)
    assert len(tasks) == _BATCH_COUNT
    assert tasks[0].task_id != tasks[1].task_id


def test_generate_task_retries_when_first_generate_raises(
    tmp_path: Path,
) -> None:
    """A failed first attempt is retried until a task is produced.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        None.
    """
    state = str(tmp_path / "batch_state.pkl")
    cfg = replace(_minimal_app_config(state), count=_SINGLE_COUNT)

    class Gen:
        """Stateful fake generator that fails once then succeeds."""

        def __init__(self) -> None:
            self.calls = 0

        def generate(self, **_kwargs: object) -> GeneratedTask:
            self.calls += 1
            if self.calls == 1:
                raise ValueError("too restrictive")
            return _fake_task(1)

    gen = Gen()
    with patch(
        "generator.cli.batch_generate.load_history_from_state",
        return_value=[],
    ):
        with patch(
            "generator.cli.batch_generate._build_task_generator",
            return_value=gen,
        ):
            tasks = generate_tasks_batch(cfg)
    assert len(tasks) == 1
    assert gen.calls == 2
