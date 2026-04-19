"""Tests for :mod:`core.formatting`."""

from __future__ import annotations

from core.formatting import pretty, structure_signature


def test_pretty_empty_containers() -> None:
    """Format empty dict, list, and tuple literals.

    Returns:
        None.
    """
    assert pretty({}) == "{}"
    assert pretty([]) == "[]"
    assert pretty(()) == "()"


def test_pretty_nested_dict() -> None:
    """Pretty-print includes keys from nested structures.

    Returns:
        None.
    """
    text = pretty({"b": 1, "a": [2, 3]})
    assert "'a'" in text
    assert "'b'" in text


def test_structure_signature_scalar() -> None:
    """Scalar values map to simple type names.

    Returns:
        None.
    """
    assert structure_signature(42) == "int"
    assert structure_signature("x") == "str"


def test_structure_signature_nested() -> None:
    """Nested containers appear in the signature string.

    Returns:
        None.
    """
    sig = structure_signature({"k": [1, 2]})
    assert "dict" in sig
    assert "list" in sig
