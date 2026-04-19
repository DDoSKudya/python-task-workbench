"""Tests for editor type inference (:mod:`ui.editor.type_inference`)."""

from __future__ import annotations

from typing import Final

from ui.editor.type_inference import (
    infer_symbol_types,
    python_type_method_map,
)

_SAMPLE: Final[str] = "def f(input_data: dict) -> None:\n    xs: list = []\n"


def test_infer_symbol_types_sees_input_data_as_dict() -> None:
    """Annotations populate the symbol-to-type map.

    Returns:
        None.
    """
    types = infer_symbol_types(_SAMPLE)
    assert types.get("input_data") == "dict"
    assert types.get("xs") == "list"


def test_python_type_method_map_has_known_types() -> None:
    """Built-in types expose expected method names.

    Returns:
        None.
    """
    mmap = python_type_method_map()
    assert "list" in mmap
    assert "dict" in mmap
    assert "append" in mmap["list"]
