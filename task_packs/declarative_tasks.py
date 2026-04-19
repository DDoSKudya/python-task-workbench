"""
This module loads declarative JSON task definitions, validates them, and
turns them into Variant factories that the task generator can use.

It works by parsing JSON arrays of task rows, coercing each row into a
DeclarativeTaskSpec dataclass when it passes structural and semantic
checks, and then wrapping each spec in a callable that produces a
concrete task payload based on static data, recipes, or pack-level
generators.

It defines type aliases for generated input, pack-level generators, row
lists, and check-input modes, plus a frozen DeclarativeTaskSpec
capturing all task metadata and checker configuration, and a
DeclarativeTaskIssue for reporting problems tied to specific files or
rows.

Helper functions such as _as_non_empty_str, _as_str_tuple,
_normalize_str_key_mapping, _check_input_fields,
_expected_result_from_row, _extract_row_lists, and
_extract_optional_fields enforce that required fields are present,
optional fields are well-typed, mappings use string keys, and that
check_input/check_input_kw are consistent.

_load_task_payload reads a JSON file, ensures the root is a list, and
filters it to dicts with string keys, while _spec_from_row applies all
per-row validations and either builds a DeclarativeTaskSpec or returns
None for invalid rows.

load_task_specs_with_issues orchestrates file loading, iterates rows
with 1-based indexing, collects all valid specs, and accumulates
DeclarativeTaskIssue entries for unreadable files or invalid rows,
returning both as tuples.

The payload factory builders (_declarative_payload_factory,
_recipe_payload_factory, _pack_generator_payload_factory,
_pack_payload_override_factory) capture a spec and an optional generator
or recipe and return callables that produce deep-copied payload dicts,
optionally merging or replacing input data and expected results.

variants_from_specs_with_builders takes all specs for a pack plus
optional pack-level generators, consults the available input recipes,
and yields a list of Variant tuples, each containing a payload factory,
collection tags, and task ID.

The core _variant_from_spec function chooses the generation strategy per
spec: full payload override if payload_generator is provided,
input-only generator if input_generator is provided, recipe-based
generation if a known input_recipe is set, or a pure declarative payload
otherwise, skipping specs that reference unknown recipes.

Within the larger system, this module is the bridge between declarative
pack JSON files and the runtime task generator, turning static metadata
into executable variant factories while surfacing detailed validation
issues.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from copy import deepcopy

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, cast

from messages import (
    CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_US41,
    CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_US41,
    EMPTY_STRING_DINAMIC_POSTFIX_US41,
    ERR_INVALID_GENERATED_INPUT_DINAMIC_POSTFIX_US41,
    ERR_INVALID_GENERATED_PAYLOAD_DINAMIC_POSTFIX_US41,
    KEY_ANALOGY_DINAMIC_POSTFIX_US41,
    KEY_CHECK_ENTRY_DINAMIC_POSTFIX_US41,
    KEY_CHECK_INPUT_DINAMIC_POSTFIX_US41,
    KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_US41,
    KEY_COLLECTIONS_DINAMIC_POSTFIX_US41,
    KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_US41,
    KEY_COMPLEXITY_DINAMIC_POSTFIX_US41,
    KEY_CONSTRAINTS_DINAMIC_POSTFIX_US41,
    KEY_DESCRIPTION_DINAMIC_POSTFIX_US41,
    KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_US41,
    KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_US41,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_US41,
    KEY_INPUT_RECIPE_DINAMIC_POSTFIX_US41,
    KEY_OPTIMAL_TOOL_DINAMIC_POSTFIX_US41,
    KEY_PATTERN_DINAMIC_POSTFIX_US41,
    KEY_STARTER_CODE_DINAMIC_POSTFIX_US41,
    KEY_TASK_ID_DINAMIC_POSTFIX_US41,
    KEY_TITLE_DINAMIC_POSTFIX_US41,
    MSG_INVALID_JSON_OR_PAYLOAD_DINAMIC_POSTFIX_US41,
    MSG_ROW_FAILED_TEMPLATE_DINAMIC_POSTFIX_US41,
)

from .pack_types import Variant

_TASKS_ENCODING: Final[str] = "utf-8"
_FIRST_ROW_NUMBER: Final[int] = 1
CheckInputMode = Literal["positional", "keyword"]
type GeneratedTaskInput = tuple[dict[str, object], object]
type PackInputGenerator = Callable[
    [object, "DeclarativeTaskSpec"],
    GeneratedTaskInput,
]
type PackPayloadGenerator = Callable[
    [object, "DeclarativeTaskSpec"],
    dict[str, object],
]
type OptionalSpecFields = tuple[
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
]
type RowLists = tuple[
    tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]
]
type CheckInputFields = tuple[CheckInputMode, str | None]


@dataclass(frozen=True)
class DeclarativeTaskSpec:
    """Validated declarative task row loaded from JSON.

    Attributes:
        task_id: Unique identifier string within the pack.
        title: Short human-readable title.
        description: Full task description text.
        input_data: Prompt payload that may be empty when
            ``input_recipe`` is set.
        expected_result: Static reference answer; omitted when
        ``input_recipe`` generates input and answer at runtime.
        collections: Non-empty tuple of collection names to bind.
        pattern: Optional solution pattern label.
        constraints: Non-empty strings describing constraints.
        difficulty_hints: Optional hints for difficulty calibration.
        common_pitfalls: Optional known mistake descriptions.
        real_world_analogy: Optional analogy text.
        estimated_complexity: Optional coarse complexity label.
        optimal_tool: Optional suggested tool name.
        input_recipe: Optional engine recipe id from
            :mod:`task_packs.input_recipes`.
        starter_code: If the JSON key is absent, the app uses its
        default editor stub. If the key is present and ``null``, the
        editor starts empty. If a string, that text is the initial
        solution buffer.
        check_entry: Global callable name to invoke after ``exec``.
            Any valid identifier is allowed, not only ``solve``.
        check_input: ``positional`` — pass the task dict as the first
            positional argument; ``keyword`` — pass it as the parameter
            named by ``check_input_kw``.
        check_input_kw: Required when ``check_input`` is ``keyword``.
            Must be absent or null when ``positional``.
    """

    task_id: str
    title: str
    description: str
    input_data: dict[str, object]
    expected_result: object | None
    collections: tuple[str, ...]
    pattern: str | None
    constraints: tuple[str, ...]
    difficulty_hints: tuple[str, ...]
    common_pitfalls: tuple[str, ...]
    real_world_analogy: str | None
    estimated_complexity: str | None
    optimal_tool: str | None
    input_recipe: str | None
    starter_code: str | None
    check_entry: str
    check_input: CheckInputMode
    check_input_kw: str | None


@dataclass(frozen=True)
class DeclarativeTaskIssue:
    """Single validation problem tied to a declarative task file.

    Attributes:
        file_name: Path or label of the offending JSON file.
        message: Human-readable explanation of the issue.
    """

    file_name: str
    message: str


def _as_non_empty_str(raw: object) -> str | None:
    """Return stripped non-empty text, or None if unusable.

    Args:
        raw: Value taken from a JSON object (often str).

    Returns:
        Stripped string if ``raw`` is a non-empty str; otherwise None.
    """
    if not isinstance(raw, str):
        return None
    value = raw.strip()
    return value or None


def _as_str_tuple(raw: object) -> tuple[str, ...] | None:
    """Normalize an optional JSON array of strings.

    Args:
        raw: ``None``, a list of strings, or an invalid type.

    Returns:
        Tuple of non-empty stripped strings. Empty list becomes an
        empty tuple. Returns None if ``raw`` is not None and not a list
        of strings.
    """
    if raw is None:
        return ()
    if not isinstance(raw, list):
        return None
    values: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            return None
        value = item.strip()
        if value:
            values.append(value)
    return tuple(values)


def _optional_input_data(row: dict[str, object]) -> dict[str, object] | None:
    """Parse ``input_data``; missing or null yields empty dict.

    Returns:
        Normalized mapping, or None if the value is present but not an
        object with string keys.
    """
    if KEY_INPUT_DATA_DINAMIC_POSTFIX_US41 not in row:
        return {}
    raw = row[KEY_INPUT_DATA_DINAMIC_POSTFIX_US41]
    return {} if raw is None else _normalize_str_key_mapping(raw)


def _check_input_mode(raw: object) -> CheckInputMode | None:
    """Normalize check input mode from row payload.

    Args:
        raw: Value from ``check_input`` key.

    Returns:
        Normalized mode string, or None when value is invalid.
    """
    if raw is None:
        return cast(
            CheckInputMode,
            CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_US41,
        )
    if not isinstance(raw, str):
        return None
    if raw == CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_US41:
        return cast(
            CheckInputMode,
            CHECK_INPUT_POSITIONAL_DINAMIC_POSTFIX_US41,
        )
    if raw == CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_US41:
        return cast(
            CheckInputMode,
            CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_US41,
        )
    return None


def _optional_text_field(raw: object) -> tuple[bool, str | None]:
    """Validate optional text field that may be missing.

    Args:
        raw: Candidate field value from JSON row.

    Returns:
        Pair ``(is_valid, value)`` where value is ``None`` or ``str``.
    """
    if raw is None:
        return True, None
    return (True, raw) if isinstance(raw, str) else (False, None)


def _starter_code_from_row(row: dict[str, object]) -> tuple[bool, str | None]:
    """Parse ``starter_code`` preserving null-vs-missing behavior.

    Args:
        row: Normalized JSON object for one declarative task.

    Returns:
        Pair ``(is_valid, starter_code)``.
    """
    if KEY_STARTER_CODE_DINAMIC_POSTFIX_US41 not in row:
        return True, None
    starter_raw = row.get(KEY_STARTER_CODE_DINAMIC_POSTFIX_US41)
    if starter_raw is None:
        return True, EMPTY_STRING_DINAMIC_POSTFIX_US41
    return (
        (True, starter_raw) if isinstance(starter_raw, str) else (False, None)
    )


def _check_input_fields(
    row: dict[str, object],
) -> CheckInputFields | None:
    """Parse and validate check input mode and keyword parameter.

    Args:
        row: Normalized JSON object for one declarative task.

    Returns:
        Pair ``(check_input, check_input_kw)`` or None when invalid.
    """
    check_input = _check_input_mode(
        row.get(KEY_CHECK_INPUT_DINAMIC_POSTFIX_US41)
    )
    if check_input is None:
        return None
    ckw_raw = row.get(KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_US41)
    if check_input == CHECK_INPUT_KEYWORD_DINAMIC_POSTFIX_US41:
        check_input_kw = _as_non_empty_str(ckw_raw)
        return (
            None if check_input_kw is None else (check_input, check_input_kw)
        )
    if ckw_raw is None or ckw_raw == EMPTY_STRING_DINAMIC_POSTFIX_US41:
        return check_input, None
    return None


def _optional_recipe_id(raw: object) -> str | None:
    """Normalize optional non-empty recipe id.

    Args:
        raw: Candidate field value from JSON row.

    Returns:
        Recipe id string, or None.
    """
    return raw.strip() if isinstance(raw, str) and raw.strip() else None


def _normalize_str_key_mapping(
    raw: object,
) -> dict[str, object] | None:
    """Ensure a JSON object uses only string keys.

    Args:
        raw: Candidate mapping from a JSON row.

    Returns:
        ``dict`` copy with ``str`` keys, or None if ``raw`` is not a
        dict or contains a non-string key.
    """
    if not isinstance(raw, dict):
        return None
    result: dict[str, object] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            return None
        result[key] = value
    return result


def _load_task_payload(
    path: Path,
) -> list[dict[str, object]] | None:
    """Read a JSON list of object rows from ``path``.

    Args:
        path: Declarative task file location.

    Returns:
        List of row dicts, or None if the file is unreadable, not valid
        JSON, or the root value is not a list.
    """
    try:
        raw_text = path.read_text(encoding=_TASKS_ENCODING)
        payload = json.loads(raw_text)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, list):
        return None
    rows: list[dict[str, object]] = []
    for item in payload:
        normalized = _normalize_str_key_mapping(item)
        if normalized is not None:
            rows.append(normalized)
    return rows


def _spec_from_row(row: dict[str, object]) -> DeclarativeTaskSpec | None:
    """Parse and validate one declarative task row.

    Args:
        row: Normalized JSON object for a single task.

    Returns:
        Frozen spec if the row is valid; otherwise None.
    """
    task_id = _as_non_empty_str(row.get(KEY_TASK_ID_DINAMIC_POSTFIX_US41))
    title = _as_non_empty_str(row.get(KEY_TITLE_DINAMIC_POSTFIX_US41))
    description = _as_non_empty_str(
        row.get(KEY_DESCRIPTION_DINAMIC_POSTFIX_US41),
    )
    input_data = _optional_input_data(row)
    row_lists = _extract_row_lists(row)
    input_recipe = _optional_recipe_id(
        row.get(KEY_INPUT_RECIPE_DINAMIC_POSTFIX_US41)
    )
    optional_fields = _extract_optional_fields(row)
    if row_lists is None or optional_fields is None:
        return None
    pattern, analogy, complexity, optimal_tool, starter_code, check_entry = (
        optional_fields
    )
    collections, constraints, difficulty_hints, common_pitfalls = row_lists
    if (
        task_id is None
        or title is None
        or description is None
        or input_data is None
        or not collections
        or check_entry is None
    ):
        return None
    check_input_fields = _check_input_fields(row)
    if check_input_fields is None:
        return None
    expected_result = _expected_result_from_row(
        row=row, input_recipe=input_recipe
    )
    if expected_result is _MISSING_EXPECTED_RESULT:
        return None
    check_input, check_input_kw = check_input_fields
    return DeclarativeTaskSpec(
        task_id=task_id,
        title=title,
        description=description,
        input_data=input_data,
        expected_result=expected_result,
        collections=collections,
        pattern=pattern,
        constraints=constraints,
        difficulty_hints=difficulty_hints,
        common_pitfalls=common_pitfalls,
        real_world_analogy=analogy,
        estimated_complexity=complexity,
        optimal_tool=optimal_tool,
        input_recipe=input_recipe,
        starter_code=starter_code,
        check_entry=check_entry,
        check_input=check_input,
        check_input_kw=check_input_kw,
    )


_MISSING_EXPECTED_RESULT: Final[object] = object()


def _expected_result_from_row(
    *,
    row: dict[str, object],
    input_recipe: str | None,
) -> object:
    """Return expected result according to recipe settings.

    Args:
        row: Normalized task row payload.
        input_recipe: Optional recipe id.

    Returns:
        Expected result object, None for recipe-based rows,
        or a sentinel when validation fails.
    """
    if input_recipe is not None:
        return None
    if KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_US41 not in row:
        return _MISSING_EXPECTED_RESULT
    return row[KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_US41]


def _extract_row_lists(row: dict[str, object]) -> RowLists | None:
    """Parse list-like tuple fields from one task row.

    Args:
        row: Normalized task row payload.

    Returns:
        Parsed tuple fields, or None when any field is invalid.
    """
    collections = _as_str_tuple(row.get(KEY_COLLECTIONS_DINAMIC_POSTFIX_US41))
    constraints = _as_str_tuple(row.get(KEY_CONSTRAINTS_DINAMIC_POSTFIX_US41))
    difficulty_hints = _as_str_tuple(
        row.get(KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_US41),
    )
    common_pitfalls = _as_str_tuple(
        row.get(KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_US41),
    )
    if (
        collections is None
        or constraints is None
        or difficulty_hints is None
        or common_pitfalls is None
    ):
        return None
    return collections, constraints, difficulty_hints, common_pitfalls


def _extract_optional_fields(
    row: dict[str, object],
) -> OptionalSpecFields | None:
    """Parse optional text and checker fields from one task row.

    Args:
        row: Normalized task row payload.

    Returns:
        Parsed optional field tuple, or None when validation fails.
    """
    pattern_ok, pattern = _optional_text_field(
        row.get(KEY_PATTERN_DINAMIC_POSTFIX_US41),
    )
    analogy_ok, analogy = _optional_text_field(
        row.get(KEY_ANALOGY_DINAMIC_POSTFIX_US41),
    )
    complexity_ok, complexity = _optional_text_field(
        row.get(KEY_COMPLEXITY_DINAMIC_POSTFIX_US41),
    )
    optimal_tool_ok, optimal_tool = _optional_text_field(
        row.get(KEY_OPTIMAL_TOOL_DINAMIC_POSTFIX_US41),
    )
    starter_ok, starter_code = _starter_code_from_row(row)
    check_entry = _as_non_empty_str(
        row.get(KEY_CHECK_ENTRY_DINAMIC_POSTFIX_US41)
    )
    if (
        not pattern_ok
        or not analogy_ok
        or not complexity_ok
        or not optimal_tool_ok
        or not starter_ok
    ):
        return None
    return (
        pattern,
        analogy,
        complexity,
        optimal_tool,
        starter_code,
        check_entry,
    )


def _task_payload_dict(spec: DeclarativeTaskSpec) -> dict[str, object]:
    """Build the JSON-like payload for a declarative (non-builder) task.

    Args:
        spec: Source specification with all fields populated.

    Returns:
        Mapping suitable for downstream task generation.
    """
    out: dict[str, object] = {
        KEY_TASK_ID_DINAMIC_POSTFIX_US41: spec.task_id,
        KEY_TITLE_DINAMIC_POSTFIX_US41: spec.title,
        KEY_DESCRIPTION_DINAMIC_POSTFIX_US41: spec.description,
        KEY_INPUT_DATA_DINAMIC_POSTFIX_US41: deepcopy(spec.input_data),
        KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_US41: deepcopy(
            spec.expected_result
        ),
        KEY_COLLECTIONS_DINAMIC_POSTFIX_US41: list(spec.collections),
        KEY_PATTERN_DINAMIC_POSTFIX_US41: spec.pattern,
        KEY_CONSTRAINTS_DINAMIC_POSTFIX_US41: list(spec.constraints),
        KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_US41: list(spec.difficulty_hints),
        KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_US41: list(spec.common_pitfalls),
        KEY_ANALOGY_DINAMIC_POSTFIX_US41: spec.real_world_analogy,
        KEY_COMPLEXITY_DINAMIC_POSTFIX_US41: spec.estimated_complexity,
        KEY_OPTIMAL_TOOL_DINAMIC_POSTFIX_US41: spec.optimal_tool,
        KEY_CHECK_ENTRY_DINAMIC_POSTFIX_US41: spec.check_entry,
        KEY_CHECK_INPUT_DINAMIC_POSTFIX_US41: spec.check_input,
        KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_US41: spec.check_input_kw,
    }
    if spec.starter_code is not None:
        out[KEY_STARTER_CODE_DINAMIC_POSTFIX_US41] = spec.starter_code
    return out


def _declarative_payload_factory(
    spec: DeclarativeTaskSpec,
) -> Callable[[object], dict[str, object]]:
    """Bind ``spec`` into a Variant-compatible payload callable.

    Args:
        spec: Declarative task used when the pack has no
            ``input_recipe``.

    Returns:
        Callable accepting the generator placeholder required by the
        Variant protocol and returning a fresh payload dict.
    """

    def build(_factory: object) -> dict[str, object]:
        """Build payload from bound declarative task spec.

        Args:
            _factory: Unused factory placeholder from Variant protocol.

        Returns:
            Fresh task payload dictionary.
        """
        return _task_payload_dict(spec)

    return build


def _recipe_payload_factory(
    spec: DeclarativeTaskSpec,
) -> Callable[[object], dict[str, object]]:
    """Bind ``spec`` to :func:`input_recipes.run_input_recipe`.

    Args:
        spec: Declarative task spec with recipe id.

    Returns:
        Callable that builds payload via runtime input recipe.
    """

    def run(factory_obj: object) -> dict[str, object]:
        """Run recipe-backed payload generation.

        Args:
            factory_obj: Fake-data factory from generator runtime.

        Returns:
            Generated task payload dictionary.
        """
        from .input_recipes import run_input_recipe

        return run_input_recipe(factory_obj, spec)

    return run


def _pack_generator_payload_factory(
    *,
    spec: DeclarativeTaskSpec,
    input_generator: PackInputGenerator,
) -> Callable[[object], dict[str, object]]:
    """Build payload factory that delegates inputs to a pack generator.

    Args:
        spec: Declarative task spec with metadata and checker settings.
        input_generator: Pack-specific generator callback.

    Returns:
        Callable that builds full payload with generated input/answer.

    Raises:
        TypeError: If generator returns an invalid payload structure.
    """

    def run(factory_obj: object) -> dict[str, object]:
        """Generate one task payload using pack-level generator.

        Args:
            factory_obj: Runtime fake-data factory object.

        Returns:
            Full task payload dictionary.

        Raises:
            TypeError: If generated input is not a string-keyed mapping.
        """
        input_data, expected_result = input_generator(factory_obj, spec)
        normalized = _normalize_str_key_mapping(input_data)
        if normalized is None:
            raise TypeError(ERR_INVALID_GENERATED_INPUT_DINAMIC_POSTFIX_US41)
        payload = _task_payload_dict(spec)
        payload[KEY_INPUT_DATA_DINAMIC_POSTFIX_US41] = deepcopy(normalized)
        payload[KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_US41] = deepcopy(
            expected_result
        )
        return payload

    return run


def _pack_payload_override_factory(
    *,
    spec: DeclarativeTaskSpec,
    payload_generator: PackPayloadGenerator,
) -> Callable[[object], dict[str, object]]:
    """Build payload factory that allows full contract overrides.

    Args:
        spec: Declarative task spec with default metadata values.
        payload_generator: Pack-level callback that returns payload
            overrides or full payload.

    Returns:
        Callable that merges generator payload into default payload.

    Raises:
        TypeError: If generator returns a non-dictionary payload.
    """

    def run(factory_obj: object) -> dict[str, object]:
        """Generate one task payload with pack-level contract override.

        Args:
            factory_obj: Runtime fake-data factory object.

        Returns:
            Task payload with pack overrides applied.

        Raises:
            TypeError: If generated payload uses non-string keys.
        """
        generated = payload_generator(factory_obj, spec)
        normalized = _normalize_str_key_mapping(generated)
        if normalized is None:
            raise TypeError(ERR_INVALID_GENERATED_PAYLOAD_DINAMIC_POSTFIX_US41)
        payload = _task_payload_dict(spec)
        payload.update(deepcopy(normalized))
        return payload

    return run


def load_task_specs_with_issues(
    task_files: tuple[Path, ...],
) -> tuple[tuple[DeclarativeTaskSpec, ...], tuple[DeclarativeTaskIssue, ...]]:
    """Load declarative JSON task files and collect validation issues.

    Args:
        task_files: Paths to JSON files where each file root is a JSON
            array of objects.

    Returns:
        A pair ``(specs, issues)`` where ``specs`` holds every valid row
        in order and ``issues`` describes files or rows that failed.
    """
    specs: list[DeclarativeTaskSpec] = []
    issues: list[DeclarativeTaskIssue] = []
    for file_path in task_files:
        payload = _load_task_payload(file_path)
        if payload is None:
            issues.append(
                DeclarativeTaskIssue(
                    file_name=str(file_path),
                    message=MSG_INVALID_JSON_OR_PAYLOAD_DINAMIC_POSTFIX_US41,
                )
            )
            continue
        for index, row in enumerate(payload, start=_FIRST_ROW_NUMBER):
            spec = _spec_from_row(row)
            if spec is None:
                issues.append(
                    DeclarativeTaskIssue(
                        file_name=str(file_path),
                        message=MSG_ROW_FAILED_TEMPLATE_DINAMIC_POSTFIX_US41.format(
                            index=index,
                        ),
                    )
                )
                continue
            specs.append(spec)
    return tuple(specs), tuple(issues)


def variants_from_specs_with_builders(
    *,
    specs: tuple[DeclarativeTaskSpec, ...],
    input_generator: PackInputGenerator | None = None,
    payload_generator: PackPayloadGenerator | None = None,
) -> list[Variant]:
    """Produce Variant tuples for all static and recipe-based specs.

    Args:
        specs: All declarative specs discovered for the pack.
        input_generator: Optional pack-level input generator. When
            provided, it overrides static/recipe input generation.
        payload_generator: Optional pack-level payload generator. When
            provided, it overrides all generation paths.

    Returns:
        List of ``Variant`` entries. Recipe ids that are not registered
        are skipped.
    """
    from .input_recipes import INPUT_RECIPES

    variants: list[Variant] = []
    for spec in specs:
        variant = _variant_from_spec(
            spec=spec,
            input_generator=input_generator,
            payload_generator=payload_generator,
            available_recipes=INPUT_RECIPES,
        )
        if variant is not None:
            variants.append(variant)
    return variants


def _variant_from_spec(
    *,
    spec: DeclarativeTaskSpec,
    input_generator: PackInputGenerator | None,
    payload_generator: PackPayloadGenerator | None,
    available_recipes: Mapping[str, object],
) -> Variant | None:
    """Build one Variant for a declarative task spec.

    Args:
        spec: One validated declarative task specification.
        input_generator: Optional pack-level input generator.
        payload_generator: Optional pack-level payload generator.
        available_recipes: Registered recipe mapping.

    Returns:
        Variant tuple, or None when recipe id is unknown.
    """
    if payload_generator is not None:
        factory = _pack_payload_override_factory(
            spec=spec,
            payload_generator=payload_generator,
        )
        return factory, spec.collections, spec.task_id
    if input_generator is not None:
        factory = _pack_generator_payload_factory(
            spec=spec,
            input_generator=input_generator,
        )
        return factory, spec.collections, spec.task_id
    if spec.input_recipe:
        if spec.input_recipe not in available_recipes:
            return None
        factory = _recipe_payload_factory(spec)
        return factory, spec.collections, spec.task_id
    factory = _declarative_payload_factory(spec)
    return factory, spec.collections, spec.task_id
