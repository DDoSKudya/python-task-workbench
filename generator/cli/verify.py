"""
This module validates and evaluates user-provided solutions for a batch
of tasks, producing structured feedback, warnings, and a summary of
passed checks.

It works by parsing the solution file into an AST, analyzing function
definitions and imports for quality and “tool usage”, checking that the
solutions metadata and task payloads match the current tasks, and then
comparing the users answers to expected results (optionally with strict
structural checks).

It defines type aliases and small helpers for recognizing string-keyed
dicts, extracting tokens from import and call AST nodes, computing
expected solve-function names, and detecting return None in function
bodies.

The quality_warnings, collect_used_tool_tokens, and approach_feedback
functions analyze the solution code to warn about missing or trivial
functions, functions that return None, and cases where the user ignores
the tasks recommended tool or API.

input_mutation_warnings inspects the TASKS payload in the solution
module to detect whether the user has mutated input data or damaged the
tasks structure, helping enforce “no mutation” expectations.

validate_solution_file_context, parse_solution_ast, and
load_answers_from_module ensure the solution file exists, parses
cleanly, and exposes both the expected task IDs and an ANSWERS list of
the right shape.

The main check_answers function orchestrates answer checking: it
verifies answer count, runs either strict or normalized comparisons via
_comparison_issues, prints per-task result lines (and a preview of deep
comparison issues when strict), and finally prints an aggregate summary
of how many tasks passed, integrating this module into the overall
grading workflow.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping, Sequence

from pathlib import Path
from typing import Final, TypeGuard

from generator.models import Task
from messages import (
    ANSWERS_VAR_NAME_DINAMIC_POSTFIX_PHDP,
    ERROR_ANSWERS_COUNT_MISMATCH_DINAMIC_POSTFIX_PHDP,
    ERROR_ANSWERS_MISSING_DINAMIC_POSTFIX_PHDP,
    ERROR_SOLUTION_FILE_MISSING_DINAMIC_POSTFIX_PHDP,
    ERROR_SYNTAX_IN_SOLUTION_FILE_DINAMIC_POSTFIX_PHDP,
    ERROR_TASK_IDS_MISMATCH_DINAMIC_POSTFIX_PHDP,
    ERROR_TASK_IDS_MISSING_DINAMIC_POSTFIX_PHDP,
    ISSUE_LINE_TEMPLATE_DINAMIC_POSTFIX_PHDP,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_PHDP,
    RESULT_LINE_TEMPLATE_DINAMIC_POSTFIX_PHDP,
    SOLUTION_FILE_ENCODING_DINAMIC_POSTFIX_PHDP,
    SOLVE_FUNCTION_NAME_TEMPLATE_DINAMIC_POSTFIX_PHDP,
    STATUS_FAIL_DINAMIC_POSTFIX_PHDP,
    STATUS_OK_DINAMIC_POSTFIX_PHDP,
    SUMMARY_LINE_TEMPLATE_DINAMIC_POSTFIX_PHDP,
    TASK_IDS_VAR_NAME_DINAMIC_POSTFIX_PHDP,
    TASKS_VAR_NAME_DINAMIC_POSTFIX_PHDP,
    TOOL_TOKEN_DELIMITER_DINAMIC_POSTFIX_PHDP,
    WARN_APPROACH_SUGGESTION_DINAMIC_POSTFIX_PHDP,
    WARN_FUNCTION_NOT_FOUND_DINAMIC_POSTFIX_PHDP,
    WARN_FUNCTION_RETURNS_NONE_DINAMIC_POSTFIX_PHDP,
    WARN_FUNCTION_TOO_SHORT_DINAMIC_POSTFIX_PHDP,
    WARN_INPUT_MUTATED_DINAMIC_POSTFIX_PHDP,
    WARN_TASKS_STRUCTURE_DAMAGED_DINAMIC_POSTFIX_PHDP,
    WARN_TASKS_VAR_MISSING_DINAMIC_POSTFIX_PHDP,
)

from .compare import normalize, strict_compare

type ModuleDict = Mapping[str, object]
STRICT_ISSUES_PREVIEW_LIMIT: Final[int] = 5
TASK_INDEX_OFFSET: Final[int] = 1


def _is_str_key_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    """Return whether value is a dictionary with string keys.

    Args:
        value: Candidate object to validate.

    Returns:
        ``True`` when ``value`` is ``dict[str, object]``-compatible.
    """
    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)


def _extract_tokens_from_import(node: ast.Import) -> set[str]:
    """Extract token names from an ``import`` statement.

    Args:
        node: Import AST node.

    Returns:
        A set of import-related tokens.
    """
    tokens: set[str] = set()
    for alias in node.names:
        tokens.add(alias.name)
        if alias.asname:
            tokens.add(alias.asname)
    return tokens


def _extract_tokens_from_import_from(node: ast.ImportFrom) -> set[str]:
    """Extract token names from a ``from ... import ...`` statement.

    Args:
        node: ImportFrom AST node.

    Returns:
        A set of import-related tokens.
    """
    tokens: set[str] = set()
    if node.module:
        tokens.add(node.module)
    for alias in node.names:
        tokens.add(alias.name)
        if alias.asname:
            tokens.add(alias.asname)
    return tokens


def _extract_tokens_from_call(node: ast.Call) -> set[str]:
    """Extract callable tokens from a call expression.

    Args:
        node: Call AST node.

    Returns:
        A set of callable tokens.
    """
    tokens: set[str] = set()
    if isinstance(node.func, ast.Name):
        tokens.add(node.func.id)
    elif isinstance(node.func, ast.Attribute):
        tokens.add(node.func.attr)
    return tokens


def _expected_function_names(tasks_count: int) -> list[str]:
    """Build expected solve-function names for a task count.

    Args:
        tasks_count: Number of generated tasks.

    Returns:
        Ordered list of expected function names.
    """
    return [
        SOLVE_FUNCTION_NAME_TEMPLATE_DINAMIC_POSTFIX_PHDP.format(index=idx)
        for idx in range(TASK_INDEX_OFFSET, tasks_count + TASK_INDEX_OFFSET)
    ]


def _has_return_none(fn: ast.FunctionDef) -> bool:
    """Return whether a function contains ``return None``.

    Args:
        fn: Function AST node.

    Returns:
        ``True`` when a ``return None`` statement is found.
    """
    return any(
        isinstance(node, ast.Return)
        and isinstance(node.value, ast.Constant)
        and (node.value.value is None)
        for node in ast.walk(fn)
    )


def _comparison_issues(
    *, expected: object, actual: object, strict_types: bool
) -> tuple[bool, list[str]]:
    """Compare values and return pass flag with optional issues.

    Args:
        expected: Expected task result.
        actual: User-provided answer.
        strict_types: Whether to enforce strict type-aware comparison.

    Returns:
        Tuple ``(is_ok, issues)``.
    """
    if strict_types:
        issues = strict_compare(expected, actual)
        return (not issues, issues)
    return (normalize(actual) == normalize(expected), [])


def _is_task_rows(value: object) -> TypeGuard[list[dict[str, object]]]:
    """Return whether value is a list of task-row dictionaries.

    Args:
        value: Candidate object from solution module namespace.

    Returns:
        ``True`` when value is ``list[dict[str, object]]``-compatible.
    """
    if not isinstance(value, list):
        return False
    return all(_is_str_key_object_dict(item) for item in value)


def _print_result_line(*, ok: bool, index: int, task: Task) -> None:
    """Print one task check status line.

    Args:
        ok: Whether answer check passed.
        index: Zero-based task index.
        task: Task metadata for output formatting.

    Returns:
        None
    """
    status = (
        STATUS_OK_DINAMIC_POSTFIX_PHDP
        if ok
        else STATUS_FAIL_DINAMIC_POSTFIX_PHDP
    )
    print(
        RESULT_LINE_TEMPLATE_DINAMIC_POSTFIX_PHDP.format(
            status=status,
            index=index + TASK_INDEX_OFFSET,
            task_id=task.task_id,
            title=task.title,
        )
    )


def _print_issues_preview(issues: Sequence[str]) -> None:
    """Print a bounded list of strict-compare issues.

    Args:
        issues: Full list of strict comparison issues.

    Returns:
        None
    """
    for issue in issues[:STRICT_ISSUES_PREVIEW_LIMIT]:
        print(ISSUE_LINE_TEMPLATE_DINAMIC_POSTFIX_PHDP.format(issue=issue))


def load_answers_from_module(module_dict: ModuleDict) -> list[object]:
    """Load user answers from a module namespace mapping.

    Args:
        module_dict: Module namespace mapping.

    Returns:
        List of answers.

    Raises:
        ValueError: If ``ANSWERS`` is missing or invalid.
    """
    answers = module_dict.get(ANSWERS_VAR_NAME_DINAMIC_POSTFIX_PHDP)
    if not isinstance(answers, list):
        raise ValueError(ERROR_ANSWERS_MISSING_DINAMIC_POSTFIX_PHDP)
    return answers


def validate_solution_file_context(
    tasks: Sequence[Task], module_dict: ModuleDict
) -> None:
    """Validate that solution metadata matches the current task set.

    Args:
        tasks: Current tasks loaded from state.
        module_dict: Module namespace mapping.

    Returns:
        None.

    Raises:
        ValueError: If task IDs are missing or mismatched.
    """
    solution_task_ids = module_dict.get(TASK_IDS_VAR_NAME_DINAMIC_POSTFIX_PHDP)
    if not isinstance(solution_task_ids, list):
        raise ValueError(ERROR_TASK_IDS_MISSING_DINAMIC_POSTFIX_PHDP)
    expected_task_ids = [task.task_id for task in tasks]
    if solution_task_ids != expected_task_ids:
        raise ValueError(ERROR_TASK_IDS_MISMATCH_DINAMIC_POSTFIX_PHDP)


def parse_solution_ast(solution_file: str) -> ast.Module:
    """Parse a solution file into an AST.

    Args:
        solution_file: Path to the solution file.

    Returns:
        Parsed module AST.

    Raises:
        ValueError: If the file is missing or contains syntax errors.
    """
    path = Path(solution_file)
    if not path.exists():
        raise ValueError(
            ERROR_SOLUTION_FILE_MISSING_DINAMIC_POSTFIX_PHDP.format(
                path=solution_file
            )
        )
    source = path.read_text(
        encoding=SOLUTION_FILE_ENCODING_DINAMIC_POSTFIX_PHDP
    )
    try:
        return ast.parse(source, filename=str(path))
    except SyntaxError as error:
        raise ValueError(
            ERROR_SYNTAX_IN_SOLUTION_FILE_DINAMIC_POSTFIX_PHDP.format(
                message=error.msg, line=error.lineno
            )
        ) from error


def quality_warnings(tree: ast.Module, tasks_count: int) -> list[str]:
    """Build quality warnings for expected solve functions.

    Args:
        tree: Parsed solution AST.
        tasks_count: Number of generated tasks.

    Returns:
        A list of quality warnings.
    """
    warnings: list[str] = []
    function_defs = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    for fn_name in _expected_function_names(tasks_count):
        fn = function_defs.get(fn_name)
        if fn is None:
            warnings.append(
                WARN_FUNCTION_NOT_FOUND_DINAMIC_POSTFIX_PHDP.format(
                    name=fn_name
                )
            )
            continue
        if len(fn.body) <= 1:
            warnings.append(
                WARN_FUNCTION_TOO_SHORT_DINAMIC_POSTFIX_PHDP.format(
                    name=fn_name
                )
            )
        if _has_return_none(fn):
            warnings.append(
                WARN_FUNCTION_RETURNS_NONE_DINAMIC_POSTFIX_PHDP.format(
                    name=fn_name
                )
            )
    return warnings


def collect_used_tool_tokens(tree: ast.Module) -> set[str]:
    """Collect import and callable tokens from the solution AST.

    Args:
        tree: Parsed solution AST.

    Returns:
        A set of observed tokens.
    """
    tokens: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            tokens.update(_extract_tokens_from_import(node))
        elif isinstance(node, ast.ImportFrom):
            tokens.update(_extract_tokens_from_import_from(node))
        elif isinstance(node, ast.Call):
            tokens.update(_extract_tokens_from_call(node))
    return tokens


def approach_feedback(tasks: Sequence[Task], tree: ast.Module) -> list[str]:
    """Suggest more appropriate tools based on task metadata.

    Args:
        tasks: Tasks to evaluate.
        tree: Parsed solution AST.

    Returns:
        A list of approach suggestions.
    """
    used = collect_used_tool_tokens(tree)
    notes: list[str] = []
    for idx, task in enumerate(tasks, start=TASK_INDEX_OFFSET):
        if not task.optimal_tool:
            continue
        tool_token = task.optimal_tool.split(
            TOOL_TOKEN_DELIMITER_DINAMIC_POSTFIX_PHDP
        )[-1]
        if tool_token not in used and task.optimal_tool not in used:
            notes.append(
                WARN_APPROACH_SUGGESTION_DINAMIC_POSTFIX_PHDP.format(
                    index=idx, tool=task.optimal_tool
                )
            )
    return notes


def input_mutation_warnings(
    tasks: Sequence[Task], module_dict: ModuleDict
) -> list[str]:
    """Check whether user code mutates input data in template payload.

    Args:
        tasks: Current tasks.
        module_dict: Module namespace mapping.

    Returns:
        A list of mutation warnings.
    """
    task_rows = module_dict.get(TASKS_VAR_NAME_DINAMIC_POSTFIX_PHDP)
    if not _is_task_rows(task_rows):
        return [WARN_TASKS_VAR_MISSING_DINAMIC_POSTFIX_PHDP]
    warnings: list[str] = []
    for idx, task in enumerate(tasks):
        if idx >= len(task_rows):
            warnings.append(
                WARN_TASKS_STRUCTURE_DAMAGED_DINAMIC_POSTFIX_PHDP.format(
                    index=idx + TASK_INDEX_OFFSET
                )
            )
            continue
        user_input = task_rows[idx].get(KEY_INPUT_DATA_DINAMIC_POSTFIX_PHDP)
        if normalize(user_input) != normalize(task.input_data):
            warnings.append(
                WARN_INPUT_MUTATED_DINAMIC_POSTFIX_PHDP.format(
                    index=idx + TASK_INDEX_OFFSET
                )
            )
    return warnings


def check_answers(
    tasks: Sequence[Task], answers: Sequence[object], *, strict_types: bool
) -> None:
    """Compare user answers with expected task results and print report.

    Args:
        tasks: Tasks to verify.
        answers: User-provided answers.
        strict_types: Whether to enforce strict structural type checks.

    Returns:
        None.

    Raises:
        ValueError: If answer count does not match task count.
    """
    if len(answers) != len(tasks):
        raise ValueError(
            ERROR_ANSWERS_COUNT_MISMATCH_DINAMIC_POSTFIX_PHDP.format(
                answers_count=len(answers), tasks_count=len(tasks)
            )
        )
    total = len(tasks)
    passed = 0
    for idx, task in enumerate(tasks):
        ok, issues = _comparison_issues(
            expected=task.expected_result,
            actual=answers[idx],
            strict_types=strict_types,
        )
        _print_result_line(ok=ok, index=idx, task=task)
        if strict_types and issues:
            _print_issues_preview(issues)
        if ok:
            passed += 1
    print(
        SUMMARY_LINE_TEMPLATE_DINAMIC_POSTFIX_PHDP.format(
            passed=passed, total=total
        )
    )
