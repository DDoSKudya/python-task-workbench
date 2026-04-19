"""
This module implements the “solve” and “check/coach” modes of a CLI
learning tool, handling task generation, solution template creation,
answer checking, and feedback printing.

It works by orchestrating calls to task generation, state persistence,
solution export, user-module loading, AST analysis, and answer
verification, while emitting formatted summaries and previews to the
terminal.

It defines small constants for preview limits and enumeration start
indices, plus helper functions for printing bullet-note sections,
previewing a subset of tasks, and rendering expected and input previews
using shared pretty-print utilities.

In solve mode, run_solve_mode generates a batch of tasks, saves them to
a state file, writes a skeleton solution file, optionally exports tasks
(e.g., Markdown/pytest), renders each task to the terminal, and then
prints a summary of created files.

For checking, run_check_mode reloads tasks from state, parses the user
solution file into an AST, prints code-quality warnings and optional
coach feedback (including a short task preview), dynamically imports the
solution module, validates its contents, warns about input mutation,
extracts answers, and finally compares them against the expected results
with configurable type strictness.

Internal helpers like _load_solution_module and _module_context
encapsulate dynamic importing and namespace access, while
_run_coach_feedback conditionally adds higher-level teaching guidance
when coach mode is enabled, making this module the central coordinator
for the CLIs learning workflow.
"""

from __future__ import annotations

import ast
import importlib.util
from collections.abc import Sequence
from types import ModuleType

from pathlib import Path
from typing import Final

from generator.app_config import AppConfig
from generator.models import Task
from messages import (
    APPROACH_FEEDBACK_HEADER_DINAMIC_POSTFIX_JMR6,
    COACH_PREVIEW_HEADER_DINAMIC_POSTFIX_JMR6,
    ERR_IMPORT_SOLUTION_MODULE_DINAMIC_POSTFIX_JMR6,
    EXPECTED_PREVIEW_PREFIX_DINAMIC_POSTFIX_JMR6,
    INPUT_PREVIEW_LINE_DINAMIC_POSTFIX_JMR6,
    MUTATION_WARNINGS_HEADER_DINAMIC_POSTFIX_JMR6,
    NOTE_BULLET_TEMPLATE_DINAMIC_POSTFIX_JMR6,
    QUALITY_WARNINGS_HEADER_DINAMIC_POSTFIX_JMR6,
    SOLUTION_FILE_CREATED_MESSAGE_DINAMIC_POSTFIX_JMR6,
    SOLUTION_MODULE_NAME_DINAMIC_POSTFIX_JMR6,
    STATE_SAVED_MESSAGE_DINAMIC_POSTFIX_JMR6,
    TASK_PREVIEW_LINE_DINAMIC_POSTFIX_JMR6,
    TASKS_EXPORTED_MESSAGE_DINAMIC_POSTFIX_JMR6,
)

from .batch_generate import generate_tasks_batch
from .export_tasks import export_tasks
from .formatting import preview_value, to_pretty
from .render_terminal import render_task
from .solution_template import write_solution_template
from .state import load_tasks_from_state, save_state
from .verify import (
    approach_feedback,
    check_answers,
    input_mutation_warnings,
    load_answers_from_module,
    parse_solution_ast,
    quality_warnings,
    validate_solution_file_context,
)

COACH_PREVIEW_LIMIT: Final[int] = 3
ENUMERATE_START_INDEX: Final[int] = 1


def _print_notes(header: str, notes: Sequence[str]) -> None:
    """Print a header and a list of bullet notes.

    Args:
        header: Section header to print.
        notes: Notes to print as bullet points.

    Returns:
        None.
    """
    if not notes:
        return
    print(header)
    for note in notes:
        print(NOTE_BULLET_TEMPLATE_DINAMIC_POSTFIX_JMR6.format(note=note))
    print()


def _preview_tasks(tasks: Sequence[Task]) -> Sequence[Task]:
    """Return a bounded slice used for coach preview output.

    Args:
        tasks: Full task sequence loaded from state.

    Returns:
        Leading tasks limited by ``COACH_PREVIEW_LIMIT``.
    """
    return tasks[: min(COACH_PREVIEW_LIMIT, len(tasks))]


def _print_expected_preview(task: Task) -> None:
    """Print expected-result preview line for one task.

    Args:
        task: Task to preview.

    Returns:
        None
    """
    expected = to_pretty(preview_value(task.expected_result))
    print(f"{EXPECTED_PREVIEW_PREFIX_DINAMIC_POSTFIX_JMR6}{expected}")


def _print_coach_preview(tasks_only: Sequence[Task]) -> None:
    """Print input and expected-result previews for coach mode.

    Args:
        tasks_only: Task sequence loaded from persisted state.

    Returns:
        None.
    """
    print(COACH_PREVIEW_HEADER_DINAMIC_POSTFIX_JMR6)
    for idx, task in enumerate(
        _preview_tasks(tasks_only),
        start=ENUMERATE_START_INDEX,
    ):
        print(
            TASK_PREVIEW_LINE_DINAMIC_POSTFIX_JMR6.format(
                index=idx, task_id=task.task_id
            )
        )
        input_preview = to_pretty(preview_value(task.input_data))
        print(
            INPUT_PREVIEW_LINE_DINAMIC_POSTFIX_JMR6.format(value=input_preview)
        )
        _print_expected_preview(task)
    print()


def _render_generated_tasks(
    generated: Sequence[Task], config: AppConfig
) -> None:
    """Render generated tasks in solve mode.

    Args:
        generated: Tasks generated for the current session.
        config: Application configuration.

    Returns:
        None
    """
    for idx, task in enumerate(generated, start=ENUMERATE_START_INDEX):
        render_task(
            task,
            index=idx,
            show_solution=config.show_solution,
            show_full_example=config.show_full_example,
            hints_step=config.hints_step,
        )


def _print_solve_summary(
    *,
    state_file: str,
    solution_file: str,
    exported_path: str | None,
) -> None:
    """Print summary messages after solve-mode completion.

    Args:
        state_file: Path where state was saved.
        solution_file: Path to generated solution template.
        exported_path: Optional path to exported tasks file.

    Returns:
        None
    """
    print(STATE_SAVED_MESSAGE_DINAMIC_POSTFIX_JMR6.format(path=state_file))
    print(
        SOLUTION_FILE_CREATED_MESSAGE_DINAMIC_POSTFIX_JMR6.format(
            path=solution_file
        )
    )
    if exported_path:
        print(
            TASKS_EXPORTED_MESSAGE_DINAMIC_POSTFIX_JMR6.format(
                path=exported_path
            )
        )


def run_solve_mode(config: AppConfig) -> None:
    """Generate tasks, persist state, and create a solution template.

    Args:
        config: Application configuration.

    Returns:
        None.
    """
    generated = generate_tasks_batch(config)
    save_state(generated, config.state_file)
    write_solution_template(generated, config.solution_file)
    exported_path = export_tasks(generated, config)
    _render_generated_tasks(generated, config)
    _print_solve_summary(
        state_file=config.state_file,
        solution_file=config.solution_file,
        exported_path=exported_path,
    )


def _load_solution_module(path: str) -> ModuleType:
    """Load a user solution module from a file path.

    Args:
        path: Path to a Python file with user answers.

    Returns:
        Imported module instance.

    Raises:
        ImportError: If the module cannot be imported.
    """
    module_path = Path(path)
    spec = importlib.util.spec_from_file_location(
        SOLUTION_MODULE_NAME_DINAMIC_POSTFIX_JMR6, module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            ERR_IMPORT_SOLUTION_MODULE_DINAMIC_POSTFIX_JMR6.format(
                module_path=module_path
            )
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _module_context(module: ModuleType) -> dict[str, object]:
    """Return mutable symbol table used by solution validators.

    Args:
        module: Imported user solution module.

    Returns:
        Module namespace as a plain dictionary.
    """
    return vars(module)


def _run_coach_feedback(
    *,
    tasks_only: Sequence[Task],
    tree: ast.Module,
    coach_mode: bool,
) -> None:
    """Print optional coach feedback sections.

    Args:
        tasks_only: Tasks loaded from persisted state.
        tree: Parsed AST object for the solution file.
        coach_mode: Whether coach-mode output is enabled.

    Returns:
        None
    """
    approach_notes = approach_feedback(tasks_only, tree)
    if not coach_mode:
        return
    _print_notes(APPROACH_FEEDBACK_HEADER_DINAMIC_POSTFIX_JMR6, approach_notes)
    _print_coach_preview(tasks_only)


def run_check_mode(config: AppConfig, *, coach_mode: bool = False) -> None:
    """Validate and check user answers against generated tasks.

    Args:
        config: Application configuration.
        coach_mode: If True, prints additional feedback and live
        previews.

    Returns:
        None.
    """
    tasks_only = load_tasks_from_state(config.state_file)
    tree = parse_solution_ast(config.solution_file)
    q_notes = quality_warnings(tree, len(tasks_only))
    _print_notes(QUALITY_WARNINGS_HEADER_DINAMIC_POSTFIX_JMR6, q_notes)
    _run_coach_feedback(
        tasks_only=tasks_only,
        tree=tree,
        coach_mode=coach_mode,
    )
    module = _load_solution_module(config.solution_file)
    module_scope = _module_context(module)
    mutation_notes = input_mutation_warnings(tasks_only, module_scope)
    _print_notes(MUTATION_WARNINGS_HEADER_DINAMIC_POSTFIX_JMR6, mutation_notes)
    validate_solution_file_context(tasks_only, module_scope)
    answers = load_answers_from_module(module_scope)
    check_answers(tasks_only, answers, strict_types=config.strict_types)
