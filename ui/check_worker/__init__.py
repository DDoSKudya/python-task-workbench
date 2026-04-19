"""
This module exports the CheckWorker class, a background worker that
executes solution checks in a sandboxed subprocess.

It works by spawning a worker process that execs the learner code,
locates and calls a configured entry function with task input, and
sends either a result or traceback back over a multiprocessing queue.

It defines many message and behavior constants for formatting hints,
mismatch descriptions, traceback summaries, and runtime error
explanations used in user-facing feedback.

The core worker logic (_worker) prepares and validates the code and task
configuration, executes the code safely, invokes the entry function in
positional or keyword mode, and packages success or failure payloads.

The main orchestration function check_solution validates the task
configuration, starts the worker process, waits with a timeout for its
queue payload, handles timeouts and empty queues, and converts the
worker payload into a CheckResult reflecting pass/fail, actual value,
and error text.

Overall, this module is the execution and grading engine that the
broader system uses to safely run learner code, enforce time limits,
and produce detailed, learner-friendly feedback on failures.
"""

from __future__ import annotations

from .worker import CheckWorker as CheckWorker

__all__: tuple[str, ...] = ("CheckWorker",)
