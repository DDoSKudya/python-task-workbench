"""Tests for learner code compilation helpers in :mod:`core.checker`."""

from __future__ import annotations

from typing import Final

from core import checker as ch

_CODE_ASSIGN: Final[str] = "x = 40 + 2\n"
_CODE_EXPR: Final[str] = "40 + 2\n"
_EXPECTED: Final[int] = 42


def test_compile_exec_code_preserves_simple_statement() -> None:
    """Compile and run a simple assignment statement.

    Returns:
        None.
    """
    co = ch._compile_exec_code(  # pyright: ignore[reportPrivateUsage]
        _CODE_ASSIGN
    )
    ns: dict[str, object] = {}
    exec(co, ns, ns)
    assert ns["x"] == _EXPECTED


def test_compile_exec_code_wraps_trailing_expression() -> None:
    """Compile a trailing expression into the auto-result variable.

    Returns:
        None.
    """
    co = ch._compile_exec_code(  # pyright: ignore[reportPrivateUsage]
        _CODE_EXPR
    )
    ns: dict[str, object] = {}
    exec(co, ns, ns)
    assert (
        ns[ch._AUTO_RESULT_VAR]  # pyright: ignore[reportPrivateUsage]
        == _EXPECTED
    )
