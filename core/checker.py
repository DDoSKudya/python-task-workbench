"""
This module runs user-submitted Python solutions in a sandboxed
subprocess, compares their output to an expected result, and returns a
structured check result.

It works by spawning a worker process that execs the learner code,
locates and calls a configured entry function with task input, and
sends either a result or traceback back over a multiprocessing queue.

It defines many message and behavior constants for formatting hints,
mismatch descriptions, traceback summaries, and runtime error
explanations used in user-facing feedback.

The core worker logic (_worker) prepares and validates the code and task
configuration, executes the code safely, invokes the entry function in
positional or keyword mode, and packages success or failure payloads.

Helper functions handle short repr generation, traceback parsing and
summarization, runtime error hint detection, value normalization for
loose comparison, strict vs non-strict equality checks, and IPC payload
validation.

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

import ast
import inspect
import multiprocessing
import re
import traceback
from collections.abc import Callable, Mapping
from multiprocessing.queues import Queue
from types import CodeType

from typing import Final, Literal, TypedDict, TypeGuard

from messages import (
    MSG_BIND_FAILED_TMPL_DINAMIC_POSTFIX_UJRO,
    MSG_EMPTY_CODE_DINAMIC_POSTFIX_UJRO,
    MSG_EMPTY_TRACEBACK_DINAMIC_POSTFIX_UJRO,
    MSG_ERR_BEFORE_ENTRY_DINAMIC_POSTFIX_UJRO,
    MSG_ERR_IN_ENTRY_TMPL_DINAMIC_POSTFIX_UJRO,
    MSG_FULL_TRACEBACK_NOTE_DINAMIC_POSTFIX_UJRO,
    MSG_HINT_ATTR_DINAMIC_POSTFIX_UJRO,
    MSG_HINT_INDEX_DINAMIC_POSTFIX_UJRO,
    MSG_HINT_KEY_DINAMIC_POSTFIX_UJRO,
    MSG_HINT_LIST_AS_DICT_DINAMIC_POSTFIX_UJRO,
    MSG_HINT_NOT_CALL_DINAMIC_POSTFIX_UJRO,
    MSG_HINT_NOT_SUB_DINAMIC_POSTFIX_UJRO,
    MSG_HINT_VALUE_DINAMIC_POSTFIX_UJRO,
    MSG_HYBRID_AUTO_CALLABLE_BIND_FAILED_DINAMIC_POSTFIX_UJRO,
    MSG_HYBRID_MULTIPLE_CALLABLES_TMPL_DINAMIC_POSTFIX_UJRO,
    MSG_HYBRID_NO_RESULT_DINAMIC_POSTFIX_UJRO,
    MSG_KEYWORD_NEEDS_KW_DINAMIC_POSTFIX_UJRO,
    MSG_LINE_BULLET_DINAMIC_POSTFIX_UJRO,
    MSG_LINE_HINT_DINAMIC_POSTFIX_UJRO,
    MSG_LINE_LOCATION_DINAMIC_POSTFIX_UJRO,
    MSG_LINE_PY_MSG_DINAMIC_POSTFIX_UJRO,
    MSG_LINE_TYPE_DINAMIC_POSTFIX_UJRO,
    MSG_MISMATCH_ACT_FRAG_DINAMIC_POSTFIX_UJRO,
    MSG_MISMATCH_ACT_TYPE_DINAMIC_POSTFIX_UJRO,
    MSG_MISMATCH_EXP_FRAG_DINAMIC_POSTFIX_UJRO,
    MSG_MISMATCH_EXP_TYPE_DINAMIC_POSTFIX_UJRO,
    MSG_MISMATCH_HEAD_DINAMIC_POSTFIX_UJRO,
    MSG_NEED_CALLABLE_TMPL_DINAMIC_POSTFIX_UJRO,
    MSG_NO_CHECK_ENTRY_DINAMIC_POSTFIX_UJRO,
    MSG_QUEUE_EMPTY_DINAMIC_POSTFIX_UJRO,
    MSG_TIMEOUT_TMPL_DINAMIC_POSTFIX_UJRO,
)

from .models import CheckerEntryMode, CheckInputMode, CheckResult, Task

_REPR_MAX_DEFAULT: Final[int] = 220
_REPR_ELLIPSIS: Final[str] = "..."
_REPR_ELLIPSIS_LEN: Final[int] = len(_REPR_ELLIPSIS)

_TAB_REPLACEMENT: Final[str] = "    "
_TRACEBACK_FRAME_LIMIT: Final[int] = 8
_PROCESS_JOIN_AFTER_TERMINATE_SEC: Final[int] = 1

_CHECK_INPUT_KEYWORD: Final[CheckInputMode] = "keyword"
_CHECK_INPUT_POSITIONAL: Final[CheckInputMode] = "positional"
_CHECKER_ENTRY_MODE_STRICT: Final[CheckerEntryMode] = "strict"
_CHECKER_ENTRY_MODE_HYBRID: Final[CheckerEntryMode] = "hybrid"

_FALLBACK_ENTRY_LABEL: Final[str] = "solution"
_AUTO_RESULT_VAR: Final[str] = "__cursor_last_result__"
_RESULT_VAR_CANDIDATES: Final[tuple[str, ...]] = ("result", "answer")
_NEWLINE: Final[str] = "\n"

_RE_LAST_LINE_EXC: Final[re.Pattern[str]] = re.compile(r"^([\w.]+):\s*(.*)$")

_KEY_OK: Final[str] = "ok"
_KEY_RESULT: Final[str] = "result"
_KEY_ERROR: Final[str] = "error"

_EXC_TYPE_ERROR: Final[str] = "TypeError"
_EXC_KEY_ERROR: Final[str] = "KeyError"
_EXC_INDEX_ERROR: Final[str] = "IndexError"
_EXC_ATTR_ERROR: Final[str] = "AttributeError"
_EXC_VALUE_ERROR: Final[str] = "ValueError"

_TYPE_ERR_LIST_STR_INDEX: Final[str] = "list indices must be integers"
_TYPE_ERR_NOT_STR: Final[str] = "not str"
_TYPE_ERR_NOT_SUBSCRIPTABLE: Final[str] = "not subscriptable"
_TYPE_ERR_NOT_CALLABLE: Final[str] = "not callable"

_MSG_EMPTY_CODE: Final[str] = MSG_EMPTY_CODE_DINAMIC_POSTFIX_UJRO
_MSG_NO_CHECK_ENTRY: Final[str] = MSG_NO_CHECK_ENTRY_DINAMIC_POSTFIX_UJRO
_MSG_KEYWORD_NEEDS_KW: Final[str] = MSG_KEYWORD_NEEDS_KW_DINAMIC_POSTFIX_UJRO
_MSG_NEED_CALLABLE_TMPL: Final[str] = (
    MSG_NEED_CALLABLE_TMPL_DINAMIC_POSTFIX_UJRO
)
_MSG_HYBRID_AUTO_CALLABLE_BIND_FAILED: Final[str] = (
    MSG_HYBRID_AUTO_CALLABLE_BIND_FAILED_DINAMIC_POSTFIX_UJRO
)
_MSG_HYBRID_MULTIPLE_CALLABLES_TMPL: Final[str] = (
    MSG_HYBRID_MULTIPLE_CALLABLES_TMPL_DINAMIC_POSTFIX_UJRO
)
_MSG_HYBRID_NO_RESULT: Final[str] = MSG_HYBRID_NO_RESULT_DINAMIC_POSTFIX_UJRO
_MSG_BIND_FAILED_TMPL: Final[str] = MSG_BIND_FAILED_TMPL_DINAMIC_POSTFIX_UJRO
_MSG_TIMEOUT_TMPL: Final[str] = MSG_TIMEOUT_TMPL_DINAMIC_POSTFIX_UJRO
_MSG_QUEUE_EMPTY: Final[str] = MSG_QUEUE_EMPTY_DINAMIC_POSTFIX_UJRO
_MSG_EMPTY_TRACEBACK: Final[str] = MSG_EMPTY_TRACEBACK_DINAMIC_POSTFIX_UJRO
_MSG_ERR_IN_ENTRY_TMPL: Final[str] = MSG_ERR_IN_ENTRY_TMPL_DINAMIC_POSTFIX_UJRO
_MSG_ERR_BEFORE_ENTRY: Final[str] = MSG_ERR_BEFORE_ENTRY_DINAMIC_POSTFIX_UJRO
_MSG_FULL_TRACEBACK_NOTE: Final[str] = (
    MSG_FULL_TRACEBACK_NOTE_DINAMIC_POSTFIX_UJRO
)
_MSG_HINT_LIST_AS_DICT: Final[str] = MSG_HINT_LIST_AS_DICT_DINAMIC_POSTFIX_UJRO
_MSG_HINT_NOT_SUB: Final[str] = MSG_HINT_NOT_SUB_DINAMIC_POSTFIX_UJRO
_MSG_HINT_NOT_CALL: Final[str] = MSG_HINT_NOT_CALL_DINAMIC_POSTFIX_UJRO
_MSG_HINT_KEY: Final[str] = MSG_HINT_KEY_DINAMIC_POSTFIX_UJRO
_MSG_HINT_INDEX: Final[str] = MSG_HINT_INDEX_DINAMIC_POSTFIX_UJRO
_MSG_HINT_ATTR: Final[str] = MSG_HINT_ATTR_DINAMIC_POSTFIX_UJRO
_MSG_HINT_VALUE: Final[str] = MSG_HINT_VALUE_DINAMIC_POSTFIX_UJRO
_MSG_MISMATCH_HEAD: Final[str] = MSG_MISMATCH_HEAD_DINAMIC_POSTFIX_UJRO
_MSG_MISMATCH_EXP_TYPE: Final[str] = MSG_MISMATCH_EXP_TYPE_DINAMIC_POSTFIX_UJRO
_MSG_MISMATCH_ACT_TYPE: Final[str] = MSG_MISMATCH_ACT_TYPE_DINAMIC_POSTFIX_UJRO
_MSG_MISMATCH_EXP_FRAG: Final[str] = MSG_MISMATCH_EXP_FRAG_DINAMIC_POSTFIX_UJRO
_MSG_MISMATCH_ACT_FRAG: Final[str] = MSG_MISMATCH_ACT_FRAG_DINAMIC_POSTFIX_UJRO
_MSG_LINE_TYPE: Final[str] = MSG_LINE_TYPE_DINAMIC_POSTFIX_UJRO
_MSG_LINE_PY_MSG: Final[str] = MSG_LINE_PY_MSG_DINAMIC_POSTFIX_UJRO
_MSG_LINE_BULLET: Final[str] = MSG_LINE_BULLET_DINAMIC_POSTFIX_UJRO
_MSG_LINE_LOCATION: Final[str] = MSG_LINE_LOCATION_DINAMIC_POSTFIX_UJRO
_MSG_LINE_HINT: Final[str] = MSG_LINE_HINT_DINAMIC_POSTFIX_UJRO

_HINT_SUPPRESS_SUBSTRINGS: Final[tuple[str, ...]] = (
    _MSG_EMPTY_CODE,
    _MSG_NO_CHECK_ENTRY,
    _MSG_KEYWORD_NEEDS_KW,
)


class _WorkerSuccess(TypedDict):
    """Successful worker IPC payload (``ok`` is true)."""

    ok: Literal[True]
    result: object


class _WorkerFailure(TypedDict):
    """Failed worker IPC payload (``ok`` is false)."""

    ok: Literal[False]
    error: str


def _is_str_key_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    """Return whether ``value`` is a ``dict`` with only ``str`` keys.

    Args:
        value: Object received from the worker queue or elsewhere.

    Returns:
        ``True`` when ``value`` is a string-keyed mapping suitable for
        checker IPC.
    """
    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)


def _frame_line_regex(entry: str) -> re.Pattern[str]:
    """Build a regex that finds the solution frame line for ``entry``.

    Args:
        entry: Callable name configured as ``check_entry``.

    Returns:
        Compiled pattern matching ``File "<string>", line N, in ...``.
    """
    safe = re.escape(entry)
    return re.compile(rf'File "<string>", line (\d+), in {safe}')


def _short_repr(value: object, limit: int = _REPR_MAX_DEFAULT) -> str:
    """Return a bounded ``repr`` string for UI and error text.

    Args:
        value: Any Python value.
        limit: Maximum length of the returned string.

    Returns:
        ``repr(value)``, possibly truncated with an ellipsis suffix.
    """
    text = repr(value)
    if len(text) > limit:
        head = text[: limit - _REPR_ELLIPSIS_LEN]
        return f"{head}{_REPR_ELLIPSIS}"
    return text


def _hint_for_runtime_error(
    exc_name: str | None,
    message: str,
) -> str | None:
    """Return a short English hint for common learner mistakes.

    Args:
        exc_name: Exception class name from the last traceback line.
        message: Exception message text (may be empty).

    Returns:
        A hint string, or ``None`` when no hint applies.
    """
    if exc_name == _EXC_TYPE_ERROR:
        lower = message.lower()
        type_checks = (
            (
                _TYPE_ERR_LIST_STR_INDEX in lower
                and _TYPE_ERR_NOT_STR in lower,
                _MSG_HINT_LIST_AS_DICT,
            ),
            (_TYPE_ERR_NOT_SUBSCRIPTABLE in lower, _MSG_HINT_NOT_SUB),
            (_TYPE_ERR_NOT_CALLABLE in lower, _MSG_HINT_NOT_CALL),
        )
        return next(
            (hint for predicate, hint in type_checks if predicate),
            None,
        )
    if exc_name == _EXC_VALUE_ERROR:
        if any(s in message for s in _HINT_SUPPRESS_SUBSTRINGS):
            return None
        return _MSG_HINT_VALUE
    if exc_name is None:
        return None
    return {
        _EXC_KEY_ERROR: _MSG_HINT_KEY,
        _EXC_INDEX_ERROR: _MSG_HINT_INDEX,
        _EXC_ATTR_ERROR: _MSG_HINT_ATTR,
    }.get(exc_name)


def _parse_exception_tail(line: str) -> tuple[str | None, str]:
    """Extract exception type and message from traceback tail line.

    Args:
        line: Last non-empty traceback line.

    Returns:
        Tuple of ``(exception_name, message)``.
    """
    match = _RE_LAST_LINE_EXC.match(line)
    if match is None:
        return None, line
    return match.group(1), match.group(2).strip()


def _entry_line_number(*, lines: list[str], entry: str) -> int | None:
    """Find the first traceback line number for checker entry frame.

    Args:
        lines: Traceback lines.
        entry: Callable name configured as ``check_entry``.

    Returns:
        Source line number inside learner code, or ``None``.
    """
    frame_re = _frame_line_regex(entry)
    for line in lines:
        frame_match = frame_re.search(line)
        if frame_match is not None:
            return int(frame_match.group(1))
    return None


def _traceback_summary_lines(
    *,
    entry: str,
    entry_line: int | None,
    exc_name: str | None,
    exc_msg: str,
    fallback_last_line: str,
) -> list[str]:
    """Build short human-readable traceback summary lines.

    Args:
        entry: Entry callable name.
        entry_line: Entry source line when detected.
        exc_name: Parsed exception class name.
        exc_msg: Parsed exception message.
        fallback_last_line: Last traceback line when parsing fails.

    Returns:
        Summary lines without full traceback text.
    """
    if entry_line is not None:
        parts: list[str] = [_MSG_ERR_IN_ENTRY_TMPL.format(entry=entry)]
    else:
        parts = [_MSG_ERR_BEFORE_ENTRY]
    if exc_name is None:
        parts.append(_MSG_LINE_BULLET.format(text=fallback_last_line))
    else:
        parts.append(_MSG_LINE_TYPE.format(name=exc_name))
        if exc_msg:
            parts.append(_MSG_LINE_PY_MSG.format(text=exc_msg))
    if entry_line is not None:
        parts.append(
            _MSG_LINE_LOCATION.format(
                line_no=entry_line,
                entry=entry,
            )
        )
    hint = _hint_for_runtime_error(exc_name, exc_msg)
    if hint:
        parts.append(_MSG_LINE_HINT.format(text=hint))
    return parts


def format_executor_traceback(raw: str, *, entry: str) -> str:
    """Format a raw worker traceback into a summary plus full text.

    Args:
        raw: Full traceback string from the subprocess worker.
        entry: Callable name used to locate the learner frame.

    Returns:
        A multi-line message with a short summary and the original
        traceback.
    """
    stripped = raw.strip()
    if not stripped:
        return _MSG_EMPTY_TRACEBACK

    lines = [ln.rstrip() for ln in stripped.splitlines()]
    last = lines[-1] if lines else ""
    exc_name, exc_msg = _parse_exception_tail(last)
    entry_line = _entry_line_number(lines=lines, entry=entry)
    parts = _traceback_summary_lines(
        entry=entry,
        entry_line=entry_line,
        exc_name=exc_name,
        exc_msg=exc_msg,
        fallback_last_line=last,
    )
    parts.extend(("", _MSG_FULL_TRACEBACK_NOTE, stripped))
    return _NEWLINE.join(parts)


def format_mismatch_message(expected: object, actual: object) -> str:
    """Describe a failed equality check between expected and actual.

    Args:
        expected: Expected value from the task definition.
        actual: Value returned by the learner entry point.

    Returns:
        Human-readable explanation including types and short ``repr``
        fragments.
    """
    exp_name = type(expected).__name__
    act_name = type(actual).__name__
    return (
        _MSG_MISMATCH_HEAD
        + _MSG_MISMATCH_EXP_TYPE.format(name=exp_name)
        + _MSG_MISMATCH_ACT_TYPE.format(name=act_name)
        + _MSG_MISMATCH_EXP_FRAG.format(frag=_short_repr(expected))
        + _MSG_MISMATCH_ACT_FRAG.format(frag=_short_repr(actual))
    )


def _normalize(value: object) -> object:
    """Recursively normalize nested structures for loose comparison.

    Args:
        value: Any JSON-like or Python value.

    Returns:
        Normalized value (dict keys as ``str``, sets sorted by
        ``repr``).
    """
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, set):
        normalized = (_normalize(v) for v in value)
        return sorted(normalized, key=repr)
    return value


def _strict_compare(expected: object, actual: object) -> bool:
    """Compare values using identical runtime types and ``==``.

    Args:
        expected: Expected value from the task definition.
        actual: Value produced by the learner code.

    Returns:
        ``True`` when types match and values compare equal.
    """
    return type(expected) is type(actual) and expected == actual


def _prepare_code(code: str) -> str:
    """Normalize tabs, strip whitespace, and ensure a trailing newline.

    Args:
        code: Raw learner source text.

    Returns:
        Text suitable for ``exec``.

    Raises:
        ValueError: When the code is empty after stripping.
    """
    prepared = code.replace("\t", _TAB_REPLACEMENT).strip()
    if not prepared:
        raise ValueError(_MSG_EMPTY_CODE)
    return prepared + "\n"


def _compile_exec_code(code: str) -> CodeType:
    """Compile learner code for ``exec`` with last-expression fallback.

    If the final top-level statement is an expression, rewrite it to an
    assignment into ``_AUTO_RESULT_VAR`` so hybrid mode can use that as
    a result fallback.
    """
    module = ast.parse(code, mode="exec")
    if module.body and isinstance(module.body[-1], ast.Expr):
        tail = module.body[-1]
        module.body[-1] = ast.Assign(
            targets=[ast.Name(id=_AUTO_RESULT_VAR, ctx=ast.Store())],
            value=tail.value,
            type_comment=None,
        )
        ast.fix_missing_locations(module)
    return compile(module, "<string>", "exec")


def _invoke_check_entry(
    fn: Callable[..., object],
    input_data: Mapping[str, object],
    *,
    mode: CheckInputMode,
    kw_name: str | None,
    entry: str,
) -> object:
    """Call the learner entry point with the task input mapping.

    Args:
        fn: Callable loaded from the learner namespace.
        input_data: Task input mapping (``task.input_data``).
        mode: Positional single-arg vs keyword wrapper mode.
        kw_name: Keyword parameter name when ``mode`` is keyword.
        entry: Entry name (for error messages).

    Returns:
        Return value from the learner callable.

    Raises:
        ValueError: When binding arguments fails or keyword mode lacks a
            parameter name.
    """
    sig = inspect.signature(fn)
    if mode == _CHECK_INPUT_KEYWORD:
        if not kw_name:
            raise ValueError(_MSG_KEYWORD_NEEDS_KW)
        try:
            bound = sig.bind(**{kw_name: input_data})
        except TypeError as exc:
            raise ValueError(
                _MSG_BIND_FAILED_TMPL.format(
                    entry=entry,
                    mode=_CHECK_INPUT_KEYWORD,
                )
            ) from exc
    else:
        try:
            bound = sig.bind(input_data)
        except TypeError as exc:
            raise ValueError(
                _MSG_BIND_FAILED_TMPL.format(
                    entry=entry,
                    mode=_CHECK_INPUT_POSITIONAL,
                )
            ) from exc
    bound.apply_defaults()
    return fn(*bound.args, **bound.kwargs)


def _invoke_auto_callable(
    fn: Callable[..., object],
    input_data: Mapping[str, object],
) -> object:
    """Invoke an auto-detected callable with compatible arguments."""
    sig = inspect.signature(fn)
    bind_attempts: tuple[tuple[tuple[object, ...], dict[str, object]], ...] = (
        ((input_data,), {}),
        ((), {"input_data": input_data}),
        ((), {"data": input_data}),
        ((), {"task": input_data}),
        ((), {}),
    )
    for args, kwargs in bind_attempts:
        try:
            bound = sig.bind(*args, **kwargs)
        except TypeError:
            continue
        bound.apply_defaults()
        return fn(*bound.args, **bound.kwargs)
    raise ValueError(_MSG_HYBRID_AUTO_CALLABLE_BIND_FAILED)


def _strict_entry_callable(
    *,
    namespace: dict[str, object],
    task: Task,
) -> Callable[..., object]:
    """
    Resolve configured entry callable or raise strict contract error.
    """
    entry = task.check_entry.strip()
    if not entry:
        raise ValueError(_MSG_NO_CHECK_ENTRY)
    try:
        candidate = namespace[entry]
    except KeyError as exc:
        raise ValueError(_MSG_NEED_CALLABLE_TMPL.format(entry=entry)) from exc
    if not callable(candidate):
        raise ValueError(_MSG_NEED_CALLABLE_TMPL.format(entry=entry))
    return candidate


def _hybrid_callable_candidates(
    namespace: dict[str, object],
) -> list[tuple[str, Callable[..., object]]]:
    """Return callable candidates for automatic invocation."""
    candidates = [
        (name, value)
        for name, value in namespace.items()
        if not name.startswith("_")
        and callable(value)
        and not inspect.isclass(value)
    ]
    candidates.sort(key=lambda item: item[0])
    return candidates


def _callable_compatible_with_input(
    *,
    fn: Callable[..., object],
    input_data: Mapping[str, object],
) -> bool:
    """Check whether callable can be invoked by auto strategy."""
    sig = inspect.signature(fn)
    bind_attempts: tuple[tuple[tuple[object, ...], dict[str, object]], ...] = (
        ((input_data,), {}),
        ((), {"input_data": input_data}),
        ((), {"data": input_data}),
        ((), {"task": input_data}),
        ((), {}),
    )
    for args, kwargs in bind_attempts:
        try:
            sig.bind(*args, **kwargs)
            return True
        except TypeError:
            continue
    return False


def _resolve_hybrid_result(
    *,
    namespace: dict[str, object],
    task: Task,
) -> object:
    """Resolve result using hybrid fallback order."""
    entry = task.check_entry.strip()
    if entry:
        candidate = namespace.get(entry)
        if callable(candidate):
            return _invoke_check_entry(
                candidate,
                task.input_data,
                mode=task.check_input,
                kw_name=task.check_input_kw,
                entry=entry,
            )

    compatible = [
        (name, fn)
        for name, fn in _hybrid_callable_candidates(namespace)
        if _callable_compatible_with_input(fn=fn, input_data=task.input_data)
    ]
    if len(compatible) == 1:
        return _invoke_auto_callable(compatible[0][1], task.input_data)
    if len(compatible) > 1:
        names = ", ".join(name for name, _ in compatible)
        raise ValueError(
            _MSG_HYBRID_MULTIPLE_CALLABLES_TMPL.format(names=names)
        )

    for var_name in _RESULT_VAR_CANDIDATES:
        if var_name in namespace:
            return namespace[var_name]
    if _AUTO_RESULT_VAR in namespace:
        return namespace[_AUTO_RESULT_VAR]
    raise ValueError(_MSG_HYBRID_NO_RESULT)


def _resolve_result(
    *,
    namespace: dict[str, object],
    task: Task,
    checker_entry_mode: CheckerEntryMode,
) -> object:
    """Resolve the learner result according to checker mode."""
    if checker_entry_mode == _CHECKER_ENTRY_MODE_STRICT:
        candidate = _strict_entry_callable(namespace=namespace, task=task)
        entry = task.check_entry.strip()
        return _invoke_check_entry(
            candidate,
            task.input_data,
            mode=task.check_input,
            kw_name=task.check_input_kw,
            entry=entry,
        )
    return _resolve_hybrid_result(namespace=namespace, task=task)


def _worker_success_payload(result: object) -> dict[str, object]:
    """Build a typed success record for the result queue.

    Args:
        result: Return value from the learner entry point.

    Returns:
        Serializable mapping for IPC.
    """
    payload: _WorkerSuccess = {_KEY_OK: True, _KEY_RESULT: result}
    return dict(payload)


def _worker_failure_payload(traceback_text: str) -> dict[str, object]:
    """Build a typed failure record for the result queue.

    Args:
        traceback_text: Formatted traceback string.

    Returns:
        Serializable mapping for IPC.
    """
    failure: _WorkerFailure = {_KEY_OK: False, _KEY_ERROR: traceback_text}
    return dict(failure)


def _worker(
    code: str,
    task: Task,
    checker_entry_mode: CheckerEntryMode,
    result_queue: Queue[dict[str, object]],
) -> None:
    """Execute learner code in a subprocess and enqueue the outcome.

    Args:
        code: Learner source text.
        task: Task definition (entry name, input mode, input data).
        result_queue: Queue receiving a success or failure payload.
    """
    namespace: dict[str, object] = {"input_data": dict(task.input_data)}
    try:
        prepared = _prepare_code(code)
        if (
            checker_entry_mode == _CHECKER_ENTRY_MODE_STRICT
            and not task.check_entry.strip()
        ):
            raise ValueError(_MSG_NO_CHECK_ENTRY)
        if (
            checker_entry_mode == _CHECKER_ENTRY_MODE_STRICT
            and task.check_input == _CHECK_INPUT_KEYWORD
            and not task.check_input_kw
        ):
            raise ValueError(_MSG_KEYWORD_NEEDS_KW)
        exec_code = _compile_exec_code(prepared)
        exec(exec_code, namespace)
        out = _resolve_result(
            namespace=namespace,
            task=task,
            checker_entry_mode=checker_entry_mode,
        )
        result_queue.put(_worker_success_payload(out))
    except Exception:
        tb = traceback.format_exc(limit=_TRACEBACK_FRAME_LIMIT)
        result_queue.put(_worker_failure_payload(tb))


def _failed_result(*, task_index: int, error_text: str) -> CheckResult:
    """Build a failed checker result with consistent defaults.

    Args:
        task_index: Index of the task in the current session.
        error_text: Human-readable error message for learners.

    Returns:
        Failed ``CheckResult`` with ``error_text`` filled.
    """
    return CheckResult(
        task_index=task_index,
        passed=False,
        error_text=error_text,
    )


def _task_validation_error(
    task: Task, checker_entry_mode: CheckerEntryMode
) -> str | None:
    """Validate checker-related task settings.

    Args:
        task: Task definition to validate before process start.

    Returns:
        Error text when configuration is invalid, otherwise ``None``.
    """
    if (
        checker_entry_mode == _CHECKER_ENTRY_MODE_STRICT
        and not task.check_entry.strip()
    ):
        return _MSG_NO_CHECK_ENTRY
    if (
        checker_entry_mode == _CHECKER_ENTRY_MODE_STRICT
        and task.check_input == _CHECK_INPUT_KEYWORD
        and not task.check_input_kw
    ):
        return _MSG_KEYWORD_NEEDS_KW
    return None


def _spawn_worker(
    *,
    code: str,
    task: Task,
    checker_entry_mode: CheckerEntryMode,
) -> tuple[multiprocessing.Process, Queue[dict[str, object]]]:
    """Create and start the checker subprocess and queue.

    Args:
        code: Learner solution source code.
        task: Task used by the checker worker.

    Returns:
        Started process and queue for the worker payload.
    """
    result_queue: Queue[dict[str, object]] = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=_worker,
        args=(code, task, checker_entry_mode, result_queue),
    )
    process.start()
    return process, result_queue


def _wait_for_worker_result(
    *,
    process: multiprocessing.Process,
    result_queue: Queue[dict[str, object]],
    timeout_sec: int,
) -> tuple[dict[str, object] | None, bool]:
    """Wait for worker completion and return payload when available.

    Args:
        process: Started checker process.
        result_queue: Queue used for worker IPC.
        timeout_sec: Max allowed worker runtime.

    Returns:
        Tuple ``(payload, timed_out)`` where ``payload`` is the worker
        dict on success, and ``timed_out`` indicates process timeout.
    """
    process.join(timeout=timeout_sec)
    if process.is_alive():
        process.terminate()
        process.join(timeout=_PROCESS_JOIN_AFTER_TERMINATE_SEC)
        return None, True
    if result_queue.empty():
        return None, False
    payload_raw: object = result_queue.get()
    if not _is_str_key_object_dict(payload_raw):
        return None, False
    return payload_raw, False


def _check_worker_payload(
    payload: dict[str, object],
    *,
    task_index: int,
    task: Task,
    strict_types: bool,
) -> CheckResult:
    """Compare worker output against the task definition.

    Args:
        payload: Decoded worker IPC mapping.
        task_index: Index of the task in the current session.
        task: Task definition (expected result, check settings).
        strict_types: Whether to require identical runtime types.

    Returns:
        Pass or fail result with optional error text and actual value.
    """
    ok_flag = payload.get(_KEY_OK)
    entry = task.check_entry.strip() or _FALLBACK_ENTRY_LABEL
    if ok_flag is False:
        err_obj = payload.get(_KEY_ERROR, "")
        err_text = err_obj if isinstance(err_obj, str) else str(err_obj)
        return CheckResult(
            task_index=task_index,
            passed=False,
            error_text=format_executor_traceback(err_text, entry=entry),
        )
    if ok_flag is not True:
        return CheckResult(
            task_index=task_index,
            passed=False,
            error_text=_MSG_QUEUE_EMPTY,
        )
    if _KEY_RESULT not in payload:
        return CheckResult(
            task_index=task_index,
            passed=False,
            error_text=_MSG_QUEUE_EMPTY,
        )
    actual = payload[_KEY_RESULT]
    passed = (
        _strict_compare(task.expected_result, actual)
        if strict_types
        else _normalize(task.expected_result) == _normalize(actual)
    )
    return CheckResult(
        task_index=task_index,
        passed=passed,
        actual_result=actual,
        error_text=(
            None
            if passed
            else format_mismatch_message(task.expected_result, actual)
        ),
    )


def check_solution(
    *,
    task_index: int,
    task: Task,
    code: str,
    strict_types: bool,
    checker_entry_mode: CheckerEntryMode = _CHECKER_ENTRY_MODE_HYBRID,
    timeout_sec: int,
) -> CheckResult:
    """Run learner code in a subprocess and compare to the expected
    result.

    Invocation is controlled by ``check_entry``, ``check_input``, and
    ``check_input_kw``. The return value is compared to
    ``task.expected_result`` (strictly or after normalization).

    Args:
        task_index: Index of the task in the current session.
        task: Task definition (input, expected result, check fields).
        code: Learner source code.
        strict_types: When ``True``, require matching runtime types.
        timeout_sec: Wall-clock limit for the checker subprocess.

    Returns:
        Pass or fail result with optional error text and actual value.
    """
    validation_error = _task_validation_error(task, checker_entry_mode)
    if validation_error is not None:
        return _failed_result(
            task_index=task_index,
            error_text=validation_error,
        )
    process, result_queue = _spawn_worker(
        code=code,
        task=task,
        checker_entry_mode=checker_entry_mode,
    )
    payload_raw, timed_out = _wait_for_worker_result(
        process=process,
        result_queue=result_queue,
        timeout_sec=timeout_sec,
    )
    if timed_out:
        return _failed_result(
            task_index=task_index,
            error_text=_MSG_TIMEOUT_TMPL.format(sec=timeout_sec),
        )
    if payload_raw is None:
        return _failed_result(
            task_index=task_index,
            error_text=_MSG_QUEUE_EMPTY,
        )
    return _check_worker_payload(
        payload_raw,
        task_index=task_index,
        task=task,
        strict_types=strict_types,
    )
