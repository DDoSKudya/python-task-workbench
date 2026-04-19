"""
This module infers simple static types for selected symbols in Python
source code and exposes a helper for listing public methods of those
inferred types.

It works by scanning function parameter annotations and basic assignment
patterns using regular expressions, mapping variable names to a small
set of known type names, and then using sample instances to derive
available methods.

It defines type aliases (KnownTypeName, SymbolTypes, PatternRule),
constants for known type names and their regex pattern (TYPE_LIST,
TYPE_DICT, TYPE_SET, TYPE_STR, TYPE_TUPLE, KNOWN_TYPES, KNOWN_TYPE_MAP,
TYPE_NAME_PATTERN), several compiled regexes for function signatures,
annotations, and assignments, and an ordered set of assignment rules
plus sample objects.

Helper functions _known_type_name_or_none, _pair_from_param_annotation,
_infer_from_function_params, and _infer_from_assignment encapsulate the
logic of extracting a name and type pair from annotations or simple
assignment lines.

The public function infer_symbol_types builds a symbol-to-type map by
seeding a predefined input_data name as a dictionary, merging function
parameter inferences, and then applying assignment rules line by line to
the source text.

The other public function python_type_method_map returns a dictionary
mapping each known type name to the sorted list of its non-private
attributes, which can be used elsewhere in the system for features like
code completion or context-aware suggestions.
"""

from __future__ import annotations

import re

from typing import Final, Literal

from messages import (
    INPUT_DATA_NAME_DINAMIC_POSTFIX_WMI7,
    PARAM_SEPARATOR_DINAMIC_POSTFIX_WMI7,
    PRIVATE_NAME_PREFIX_DINAMIC_POSTFIX_WMI7,
)

type KnownTypeName = Literal["list", "dict", "set", "str", "tuple"]
type SymbolTypes = dict[str, KnownTypeName]
type PatternRule = tuple[re.Pattern[str], KnownTypeName | None]

TYPE_LIST: Final[KnownTypeName] = "list"
TYPE_DICT: Final[KnownTypeName] = "dict"
TYPE_SET: Final[KnownTypeName] = "set"
TYPE_STR: Final[KnownTypeName] = "str"
TYPE_TUPLE: Final[KnownTypeName] = "tuple"

KNOWN_TYPES: Final[tuple[KnownTypeName, ...]] = (
    TYPE_LIST,
    TYPE_DICT,
    TYPE_SET,
    TYPE_STR,
    TYPE_TUPLE,
)
KNOWN_TYPE_MAP: Final[dict[str, KnownTypeName]] = {
    name: name for name in KNOWN_TYPES
}
TYPE_NAME_PATTERN: Final[str] = "|".join(KNOWN_TYPES)

_IDENTIFIER_GROUP: Final[str] = r"([A-Za-z_]\w*)"

_FUNCTION_SIGNATURE_RE: Final[re.Pattern[str]] = re.compile(
    r"def\s+\w+\((.*?)\)\s*:"
)
_PARAM_ANNOTATION_RE: Final[re.Pattern[str]] = re.compile(
    rf"{_IDENTIFIER_GROUP}\s*:\s*({TYPE_NAME_PATTERN})\b"
)
_ANNOTATED_ASSIGNMENT_RE: Final[re.Pattern[str]] = re.compile(
    rf"^\s*{_IDENTIFIER_GROUP}\s*:\s*({TYPE_NAME_PATTERN})\b"
)

_ASSIGNMENT_RULES: Final[tuple[PatternRule, ...]] = (
    (re.compile(rf"^\s*{_IDENTIFIER_GROUP}\s*=\s*\["), TYPE_LIST),
    (
        re.compile(
            rf"^\s*{_IDENTIFIER_GROUP}\s*=\s*" + r"\{",
        ),
        TYPE_DICT,
    ),
    (re.compile(rf"^\s*{_IDENTIFIER_GROUP}\s*=\s*set\("), TYPE_SET),
    (re.compile(rf"^\s*{_IDENTIFIER_GROUP}\s*=\s*list\("), TYPE_LIST),
    (re.compile(rf"^\s*{_IDENTIFIER_GROUP}\s*=\s*dict\("), TYPE_DICT),
    (re.compile(rf"^\s*{_IDENTIFIER_GROUP}\s*=\s*tuple\("), TYPE_TUPLE),
    (re.compile(rf'^\s*{_IDENTIFIER_GROUP}\s*=\s*".*"$'), TYPE_STR),
    (re.compile(rf"^\s*{_IDENTIFIER_GROUP}\s*=\s*'.*'$"), TYPE_STR),
    (_ANNOTATED_ASSIGNMENT_RE, None),
)

_SAMPLES: Final[tuple[tuple[KnownTypeName, object], ...]] = (
    (TYPE_LIST, []),
    (TYPE_DICT, {}),
    (TYPE_SET, set()),
    (TYPE_STR, ""),
    (TYPE_TUPLE, ()),
)


def _known_type_name_or_none(value: object) -> KnownTypeName | None:
    """Map a ``str`` to a known type name when it matches the catalog.

    Args:
        value: Candidate taken from a regex group or literal rule.

    Returns:
        The same string narrowed to ``KnownTypeName``, or ``None`` if
        missing or unknown.
    """
    return KNOWN_TYPE_MAP.get(value) if isinstance(value, str) else None


def _pair_from_param_annotation(
    param: str,
) -> tuple[str, KnownTypeName] | None:
    """Parse ``name: KnownType`` from one comma-separated parameter
    chunk.

    Args:
        param: Stripped substring from inside a ``def`` parameter list.

    Returns:
        ``(name, type_name)`` when an annotation matches a known type,
        else ``None``.
    """
    match = _PARAM_ANNOTATION_RE.match(param)
    if match is None:
        return None
    type_name = _known_type_name_or_none(match.group(2))
    return (match.group(1), type_name) if type_name is not None else None


def _infer_from_function_params(text: str) -> SymbolTypes:
    """Infer symbol types from ``def`` parameter annotations in
    ``text``.

    Args:
        text: Full Python source to scan.

    Returns:
        A map of parameter names to inferred type names.
    """
    inferred: SymbolTypes = {}
    for match in _FUNCTION_SIGNATURE_RE.finditer(text):
        params = match.group(1)
        for chunk in params.split(PARAM_SEPARATOR_DINAMIC_POSTFIX_WMI7):
            param = chunk.strip()
            if not param:
                continue
            pair = _pair_from_param_annotation(param)
            if pair is not None:
                name, type_name = pair
                inferred[name] = type_name
    return inferred


def _infer_from_assignment(line: str) -> tuple[str, KnownTypeName] | None:
    """Infer a symbol type from one assignment-like source line.

    Args:
        line: Single source line.

    Returns:
        ``(name, type_name)`` when a rule matches, otherwise ``None``.
    """
    for pattern, declared_type in _ASSIGNMENT_RULES:
        match = pattern.search(line)
        if match is None:
            continue
        name = match.group(1)
        raw: object = (
            match.group(2) if declared_type is None else declared_type
        )
        inferred_type = _known_type_name_or_none(raw)
        if inferred_type is not None:
            return (name, inferred_type)
    return None


def infer_symbol_types(text: str) -> SymbolTypes:
    """Infer simple symbol types from source text.

    Args:
        text: Python source code to analyze.

    Returns:
        ``input_data`` is always treated as ``dict``; other names come
        from annotations and simple assignments.
    """
    inferred: SymbolTypes = {
        INPUT_DATA_NAME_DINAMIC_POSTFIX_WMI7: TYPE_DICT,
    }
    inferred.update(_infer_from_function_params(text))
    for line in text.splitlines():
        pair = _infer_from_assignment(line)
        if pair is None:
            continue
        name, type_name = pair
        inferred[name] = type_name
    return inferred


def python_type_method_map() -> dict[KnownTypeName, list[str]]:
    """Build a map from known type names to public method names.

    Returns:
        For each known type, sorted ``dir()`` names that do not start
        with the private-name prefix from the message catalog.
    """
    methods_by_type: dict[KnownTypeName, list[str]] = {}
    for type_name, sample in _SAMPLES:
        methods = [
            name
            for name in dir(sample)
            if not name.startswith(
                PRIVATE_NAME_PREFIX_DINAMIC_POSTFIX_WMI7,
            )
        ]
        methods_by_type[type_name] = sorted(methods)
    return methods_by_type
