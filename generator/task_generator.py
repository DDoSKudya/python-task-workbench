"""Expose the public task generator entry point."""

from __future__ import annotations

from . import task_gen as _task_gen

TaskGenerator = _task_gen.TaskGenerator

__all__: tuple[str, ...] = ("TaskGenerator",)
