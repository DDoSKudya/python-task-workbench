"""
This module defines a Qt-based worker thread that runs solution checks
asynchronously for a given task.

It works by wrapping the core check_solution function inside a QThread
subclass and emitting a signal when the check completes so the UI can
react without blocking.

It contains a CheckResult type alias and a single CheckWorker class that
stores task index, task model, user code, strictness flag, timeout, and
a run ID.

The CheckWorker exposes a finished_for pyqtSignal carrying (run_id,
task_index, result), and its run method invokes check_solution with the
stored parameters, then emits that signal with the outcome, integrating
the core checker into the PyQt event loop.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from core.checker import check_solution
from core.models import CheckerEntryMode, Task

type CheckResult = object


class CheckWorker(QThread):
    """Run solution checks in a background Qt thread.

    Attributes:
        finished_for: Signal with ``run_id``, ``task_index``, and check
            result payload.
    """

    finished_for = pyqtSignal(int, int, object)

    def __init__(
        self,
        *,
        task_index: int,
        task: Task,
        code: str,
        strict_types: bool,
        checker_entry_mode: CheckerEntryMode,
        timeout_sec: int,
        run_id: int,
        parent: QObject | None = None,
    ) -> None:
        """Initialize worker for asynchronous solution checking.

        Args:
            task_index: Index of task in current session.
            task: Task model for verification.
            code: User solution source code.
            strict_types: Whether strict type checks are enabled.
            checker_entry_mode: Entry point resolution mode.
            timeout_sec: Maximum check timeout in seconds.
            run_id: Identifier of current check run.
            parent: Optional Qt parent object.
        """
        super().__init__(parent)
        self._task_index = task_index
        self._task = task
        self._code = code
        self._strict_types = strict_types
        self._checker_entry_mode: CheckerEntryMode = checker_entry_mode
        self._timeout_sec = timeout_sec
        self._run_id = run_id

    def run(self) -> None:
        """Execute check routine and emit completion signal."""
        result: CheckResult = check_solution(
            task_index=self._task_index,
            task=self._task,
            code=self._code,
            strict_types=self._strict_types,
            checker_entry_mode=self._checker_entry_mode,
            timeout_sec=self._timeout_sec,
        )
        self.finished_for.emit(self._run_id, self._task_index, result)
