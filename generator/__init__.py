"""Task generation for collection-focused training exercises."""

from __future__ import annotations

from .fake_data import FakeDataFactory
from .models import GeneratedTask, Task, task_family_from_id
from .task_gen import TaskGenerator

__all__: tuple[str, ...] = (
    "FakeDataFactory",
    "GeneratedTask",
    "Task",
    "TaskGenerator",
    "task_family_from_id",
)
