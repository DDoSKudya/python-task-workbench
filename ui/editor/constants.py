"""
This module provides curated sets of symbol names used as completion
hints in the Python code editor.

It works by defining two frozensets of strings—one for typing-related
names and one for commonly used standard-library and built-in
symbols—and re-exporting them for use by the completion engine.

It contains a type alias CompletionHintNames and two constants:
TYPING_NAMES, which lists common type-annotation identifiers, and
STDLIB_HINTS, which lists builtin functions, core types, and a few
standard modules.

Through __all__, it explicitly exposes only TYPING_NAMES and
STDLIB_HINTS, allowing other modules (such as the completion builder)
to import these sets and merge them into their candidate word lists.
"""

from __future__ import annotations

from typing import Final

type CompletionHintNames = frozenset[str]

TYPING_NAMES: Final[CompletionHintNames] = frozenset(
    {
        "Any",
        "Callable",
        "ClassVar",
        "Final",
        "Generic",
        "Iterable",
        "Iterator",
        "Literal",
        "Mapping",
        "Never",
        "Optional",
        "Protocol",
        "Self",
        "Sequence",
        "TypeVar",
        "TypedDict",
        "Union",
    }
)

STDLIB_HINTS: Final[CompletionHintNames] = frozenset(
    {
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "breakpoint",
        "bytearray",
        "bytes",
        "chr",
        "classmethod",
        "collections",
        "complex",
        "copy",
        "dataclasses",
        "delattr",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "filter",
        "float",
        "format",
        "frozenset",
        "functools",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "itertools",
        "json",
        "len",
        "list",
        "locals",
        "map",
        "math",
        "max",
        "memoryview",
        "min",
        "next",
        "object",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "property",
        "range",
        "re",
        "repr",
        "reversed",
        "round",
        "set",
        "setattr",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "typing",
        "vars",
        "zip",
    }
)

__all__: Final[tuple[str, ...]] = ("TYPING_NAMES", "STDLIB_HINTS")
