"""Universal task generator: profile + pack-driven variants only."""

from __future__ import annotations

from .core import TaskGeneratorCore

TaskGenerator = TaskGeneratorCore

__all__: tuple[str, ...] = ("TaskGenerator", "TaskGeneratorCore")
