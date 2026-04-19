"""
This module implements parameterized “input recipes” that generate
concrete task payloads (input and expected result) using a shared
fake-data factory.

It works by defining recipe functions that use FakeDataFactory to
produce randomized but controlled structures and values, then wrapping
them into a normalized task payload with metadata from a RecipeSpec.

It defines many numeric and text constants that control ranges and sizes
for generated data (list lengths, value ranges, key lengths, text
length, probabilities) and a RecipeSpec protocol describing the metadata
fields a spec must expose.

Helper functions _random_int_list and _unique_words encapsulate
generation of random integer sequences and unique normalized words, and
_task_payload merges generated input/answer with the specs metadata
into a consistent TaskPayload.

A family of recipe functions (recipe_cl1_sum_nums, recipe_cl1_len_items,
recipe_cl1_last_elem, recipe_cl1_dict_get_default,
recipe_cl1_keys_sorted, recipe_cl1_unique_sorted,
recipe_cl1_merge_two_lists, recipe_cl1_count_char) each implement a
specific task pattern by generating suitable input data and computing
the corresponding expected result.

These recipes are registered in the INPUT_RECIPES mapping from recipe ID
to function, enabling lookup by identifier.

The run_input_recipe function is the public entry point: it verifies
that the factory is a FakeDataFactory, ensures the RecipeSpec declares
a non-empty input_recipe, looks up the recipe in INPUT_RECIPES, and
executes it or raises descriptive errors when the setup is invalid.

Within the broader system, this module provides reusable building blocks
for declarative task specs that reference an input_recipe, allowing
packs to define task shapes in JSON while delegating concrete
input/answer generation to these recipes.
"""

from __future__ import annotations

from collections.abc import Callable

from typing import Literal, Protocol

from generator.fake_data import FakeDataFactory
from messages import (
    ALPHABET_DINAMIC_POSTFIX_KZLL,
    ERR_FACTORY_INVALID_DINAMIC_POSTFIX_KZLL,
    ERR_RECIPE_REQUIRED_DINAMIC_POSTFIX_KZLL,
    ERR_RECIPE_UNKNOWN_DINAMIC_POSTFIX_KZLL,
    FALLBACK_WORD_DINAMIC_POSTFIX_KZLL,
    KEY_ANALOGY_DINAMIC_POSTFIX_KZLL,
    KEY_CH_DINAMIC_POSTFIX_KZLL,
    KEY_CHECK_ENTRY_DINAMIC_POSTFIX_KZLL,
    KEY_CHECK_INPUT_DINAMIC_POSTFIX_KZLL,
    KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_KZLL,
    KEY_COLLECTIONS_DINAMIC_POSTFIX_KZLL,
    KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_KZLL,
    KEY_COMPLEXITY_DINAMIC_POSTFIX_KZLL,
    KEY_CONSTRAINTS_DINAMIC_POSTFIX_KZLL,
    KEY_DATA_DINAMIC_POSTFIX_KZLL,
    KEY_DEFAULT_DINAMIC_POSTFIX_KZLL,
    KEY_DESCRIPTION_DINAMIC_POSTFIX_KZLL,
    KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_KZLL,
    KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_KZLL,
    KEY_FIRST_DINAMIC_POSTFIX_KZLL,
    KEY_INPUT_DATA_DINAMIC_POSTFIX_KZLL,
    KEY_ITEMS_DINAMIC_POSTFIX_KZLL,
    KEY_KEY_DINAMIC_POSTFIX_KZLL,
    KEY_MAPPING_DINAMIC_POSTFIX_KZLL,
    KEY_NUMS_DINAMIC_POSTFIX_KZLL,
    KEY_OPTIMAL_TOOL_DINAMIC_POSTFIX_KZLL,
    KEY_PATTERN_DINAMIC_POSTFIX_KZLL,
    KEY_SECOND_DINAMIC_POSTFIX_KZLL,
    KEY_STARTER_CODE_DINAMIC_POSTFIX_KZLL,
    KEY_TASK_ID_DINAMIC_POSTFIX_KZLL,
    KEY_TEXT_DINAMIC_POSTFIX_KZLL,
    KEY_TITLE_DINAMIC_POSTFIX_KZLL,
    KEY_VALUES_DINAMIC_POSTFIX_KZLL,
    MISSING_KEY_PREFIX_DINAMIC_POSTFIX_KZLL,
    MISSING_KEY_SUFFIX_DINAMIC_POSTFIX_KZLL,
    RECIPE_COUNT_CHAR_DINAMIC_POSTFIX_KZLL,
    RECIPE_DICT_GET_DEFAULT_DINAMIC_POSTFIX_KZLL,
    RECIPE_KEYS_SORTED_DINAMIC_POSTFIX_KZLL,
    RECIPE_LAST_ELEM_DINAMIC_POSTFIX_KZLL,
    RECIPE_LEN_ITEMS_DINAMIC_POSTFIX_KZLL,
    RECIPE_MERGE_TWO_LISTS_DINAMIC_POSTFIX_KZLL,
    RECIPE_SUM_NUMS_DINAMIC_POSTFIX_KZLL,
    RECIPE_UNIQUE_SORTED_DINAMIC_POSTFIX_KZLL,
)

CHOOSE_EXISTING_KEY_PROBABILITY: float = 0.5

SUM_NUMS_MIN_LEN: int = 0
SUM_NUMS_MAX_LEN: int = 12
SUM_NUMS_MIN_VALUE: int = -80
SUM_NUMS_MAX_VALUE: int = 80

LEN_ITEMS_MIN_LEN: int = 1
LEN_ITEMS_MAX_LEN: int = 18
LEN_ITEMS_MIN_VALUE: int = -1000
LEN_ITEMS_MAX_VALUE: int = 1000

LAST_ELEM_MIN_LEN: int = 2
LAST_ELEM_MAX_LEN: int = 12
LAST_ELEM_MIN_VALUE: int = -500
LAST_ELEM_MAX_VALUE: int = 500

DICT_KEYS_MIN_LEN: int = 3
DICT_KEYS_MAX_LEN: int = 6
DICT_KEY_SLICE_LEN: int = 8
DICT_VALUE_MIN: int = -40
DICT_VALUE_MAX: int = 40
DICT_DEFAULT_MIN: int = -200
DICT_DEFAULT_MAX: int = 200
MISSING_SUFFIX_MIN: int = 10_000
MISSING_SUFFIX_MAX: int = 99_999

SORTED_KEYS_MIN_LEN: int = 3
SORTED_KEYS_MAX_LEN: int = 8
SORTED_KEY_SLICE_LEN: int = 10
SORTED_VALUE_MIN: int = 0
SORTED_VALUE_MAX: int = 100

UNIQUE_SPAN_MIN: int = 5
UNIQUE_SPAN_MAX: int = 14
UNIQUE_VALUE_MIN: int = -15
UNIQUE_VALUE_MAX: int = 15
UNIQUE_DUPLICATES_MIN: int = 0
UNIQUE_DUPLICATES_MAX: int = 4

MERGE_LIST_MIN_LEN: int = 1
MERGE_LIST_MAX_LEN: int = 8
MERGE_VALUE_MIN: int = -30
MERGE_VALUE_MAX: int = 30

TEXT_MIN_LEN: int = 12
TEXT_MAX_LEN: int = 40


type CheckInputMode = Literal["positional", "keyword"]
type TaskPayload = dict[str, object]


class RecipeSpec(Protocol):
    """Protocol describing fields required by recipe generators.

    Attributes:
        task_id: Unique task identifier.
        title: Task title.
        description: Human-readable task description.
        collections: Target collections for task grouping.
        pattern: Optional solution pattern descriptor.
        constraints: Constraints shown to learner.
        difficulty_hints: Optional hints for difficulty calibration.
        common_pitfalls: Frequent mistakes list.
        real_world_analogy: Optional analogy text.
        estimated_complexity: Optional complexity hint.
        optimal_tool: Optional recommendation.
        starter_code: Optional default code shown in editor.
        check_entry: Callable name to execute for checker.
        check_input: Checker input mode.
        check_input_kw: Optional keyword parameter name.
        input_recipe: Identifier of recipe to execute.
    """

    @property
    def task_id(self) -> str: ...

    @property
    def title(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def collections(self) -> tuple[str, ...]: ...

    @property
    def pattern(self) -> str | None: ...

    @property
    def constraints(self) -> tuple[str, ...]: ...

    @property
    def difficulty_hints(self) -> tuple[str, ...]: ...

    @property
    def common_pitfalls(self) -> tuple[str, ...]: ...

    @property
    def real_world_analogy(self) -> str | None: ...

    @property
    def estimated_complexity(self) -> str | None: ...

    @property
    def optimal_tool(self) -> str | None: ...

    @property
    def starter_code(self) -> str | None: ...

    @property
    def check_entry(self) -> str: ...

    @property
    def check_input(self) -> CheckInputMode: ...

    @property
    def check_input_kw(self) -> str | None: ...

    @property
    def input_recipe(self) -> str | None: ...


type RecipeFn = Callable[[FakeDataFactory, RecipeSpec], TaskPayload]


def _random_int_list(
    *,
    factory: FakeDataFactory,
    min_len: int,
    max_len: int,
    min_value: int,
    max_value: int,
) -> list[int]:
    """Build a random integer list for recipe inputs.

    Args:
        factory: Runtime data factory with random generator.
        min_len: Minimal list size.
        max_len: Maximal list size.
        min_value: Minimal integer value.
        max_value: Maximal integer value.

    Returns:
        List of random integers.
    """
    size: int = factory.rng.randint(min_len, max_len)
    return [factory.rng.randint(min_value, max_value) for _ in range(size)]


def _unique_words(
    *,
    factory: FakeDataFactory,
    size: int,
    max_len: int,
) -> list[str]:
    """Generate a list of unique normalized words.

    Args:
        factory: Runtime data factory with fake providers.
        size: Count of unique words to generate.
        max_len: Maximal length for each normalized word.

    Returns:
        Unique words preserving generation order.
    """
    words: list[str] = []
    seen: set[str] = set()
    while len(words) < size:
        source: str = factory.fake.word().lower()
        candidate: str = (
            source[:max_len] if source else FALLBACK_WORD_DINAMIC_POSTFIX_KZLL
        )
        if candidate in seen:
            continue
        seen.add(candidate)
        words.append(candidate)
    return words


def _task_payload(
    *,
    spec: RecipeSpec,
    input_data: TaskPayload,
    expected_result: object,
) -> TaskPayload:
    """Build one generated payload from recipe output.

    Args:
        spec: Declarative specification with metadata.
        input_data: Generated input block for the task.
        expected_result: Expected checker answer.

    Returns:
        Task payload ready for downstream generation.
    """
    payload: TaskPayload = {
        KEY_TASK_ID_DINAMIC_POSTFIX_KZLL: spec.task_id,
        KEY_TITLE_DINAMIC_POSTFIX_KZLL: spec.title,
        KEY_DESCRIPTION_DINAMIC_POSTFIX_KZLL: spec.description,
        KEY_INPUT_DATA_DINAMIC_POSTFIX_KZLL: input_data,
        KEY_EXPECTED_RESULT_DINAMIC_POSTFIX_KZLL: expected_result,
        KEY_COLLECTIONS_DINAMIC_POSTFIX_KZLL: list(spec.collections),
        KEY_PATTERN_DINAMIC_POSTFIX_KZLL: spec.pattern,
        KEY_CONSTRAINTS_DINAMIC_POSTFIX_KZLL: list(spec.constraints),
        KEY_DIFFICULTY_HINTS_DINAMIC_POSTFIX_KZLL: list(
            spec.difficulty_hints,
        ),
        KEY_COMMON_PITFALLS_DINAMIC_POSTFIX_KZLL: list(
            spec.common_pitfalls,
        ),
        KEY_ANALOGY_DINAMIC_POSTFIX_KZLL: spec.real_world_analogy,
        KEY_COMPLEXITY_DINAMIC_POSTFIX_KZLL: spec.estimated_complexity,
        KEY_OPTIMAL_TOOL_DINAMIC_POSTFIX_KZLL: spec.optimal_tool,
        KEY_CHECK_ENTRY_DINAMIC_POSTFIX_KZLL: spec.check_entry,
        KEY_CHECK_INPUT_DINAMIC_POSTFIX_KZLL: spec.check_input,
        KEY_CHECK_INPUT_KW_DINAMIC_POSTFIX_KZLL: spec.check_input_kw,
    }
    if spec.starter_code is not None:
        payload[KEY_STARTER_CODE_DINAMIC_POSTFIX_KZLL] = spec.starter_code
    return payload


def recipe_cl1_sum_nums(
    factory: FakeDataFactory,
    spec: RecipeSpec,
) -> TaskPayload:
    """Build a task where answer is the sum of list values.

    Args:
        factory: Runtime data factory with random generator.
        spec: Recipe-capable task specification.

    Returns:
        Generated task payload.
    """
    nums: list[int] = _random_int_list(
        factory=factory,
        min_len=SUM_NUMS_MIN_LEN,
        max_len=SUM_NUMS_MAX_LEN,
        min_value=SUM_NUMS_MIN_VALUE,
        max_value=SUM_NUMS_MAX_VALUE,
    )
    return _task_payload(
        spec=spec,
        input_data={KEY_NUMS_DINAMIC_POSTFIX_KZLL: nums},
        expected_result=sum(nums),
    )


def recipe_cl1_len_items(
    factory: FakeDataFactory,
    spec: RecipeSpec,
) -> TaskPayload:
    """Build a task where answer is the number of generated items.

    Args:
        factory: Runtime data factory with random generator.
        spec: Recipe-capable task specification.

    Returns:
        Generated task payload.
    """
    items: list[int] = _random_int_list(
        factory=factory,
        min_len=LEN_ITEMS_MIN_LEN,
        max_len=LEN_ITEMS_MAX_LEN,
        min_value=LEN_ITEMS_MIN_VALUE,
        max_value=LEN_ITEMS_MAX_VALUE,
    )
    return _task_payload(
        spec=spec,
        input_data={KEY_ITEMS_DINAMIC_POSTFIX_KZLL: items},
        expected_result=len(items),
    )


def recipe_cl1_last_elem(
    factory: FakeDataFactory,
    spec: RecipeSpec,
) -> TaskPayload:
    """Build a task where answer is the list last element.

    Args:
        factory: Runtime data factory with random generator.
        spec: Recipe-capable task specification.

    Returns:
        Generated task payload.
    """
    values: list[int] = _random_int_list(
        factory=factory,
        min_len=LAST_ELEM_MIN_LEN,
        max_len=LAST_ELEM_MAX_LEN,
        min_value=LAST_ELEM_MIN_VALUE,
        max_value=LAST_ELEM_MAX_VALUE,
    )
    return _task_payload(
        spec=spec,
        input_data={KEY_VALUES_DINAMIC_POSTFIX_KZLL: values},
        expected_result=values[-1],
    )


def recipe_cl1_dict_get_default(
    factory: FakeDataFactory,
    spec: RecipeSpec,
) -> TaskPayload:
    """Build a task where answer mirrors dict.get behavior.

    Args:
        factory: Runtime data factory with random generator.
        spec: Recipe-capable task specification.

    Returns:
        Generated task payload.
    """
    key_count: int = factory.rng.randint(DICT_KEYS_MIN_LEN, DICT_KEYS_MAX_LEN)
    keys: list[str] = _unique_words(
        factory=factory,
        size=key_count,
        max_len=DICT_KEY_SLICE_LEN,
    )
    data: dict[str, int] = {
        key: factory.rng.randint(DICT_VALUE_MIN, DICT_VALUE_MAX)
        for key in keys
    }
    default: int = factory.rng.randint(DICT_DEFAULT_MIN, DICT_DEFAULT_MAX)

    use_existing_key: bool = (
        factory.rng.random() < CHOOSE_EXISTING_KEY_PROBABILITY
    )
    if use_existing_key:
        selected_key: str = factory.rng.choice(keys)
        expected: int = data[selected_key]
    else:
        suffix: int = factory.rng.randint(
            MISSING_SUFFIX_MIN, MISSING_SUFFIX_MAX
        )
        selected_key = f"{MISSING_KEY_PREFIX_DINAMIC_POSTFIX_KZLL}{suffix}"
        while selected_key in data:
            selected_key += MISSING_KEY_SUFFIX_DINAMIC_POSTFIX_KZLL
        expected = default

    return _task_payload(
        spec=spec,
        input_data={
            KEY_DATA_DINAMIC_POSTFIX_KZLL: data,
            KEY_KEY_DINAMIC_POSTFIX_KZLL: selected_key,
            KEY_DEFAULT_DINAMIC_POSTFIX_KZLL: default,
        },
        expected_result=expected,
    )


def recipe_cl1_keys_sorted(
    factory: FakeDataFactory,
    spec: RecipeSpec,
) -> TaskPayload:
    """Build a task where answer is sorted mapping keys.

    Args:
        factory: Runtime data factory with random generator.
        spec: Recipe-capable task specification.

    Returns:
        Generated task payload.
    """
    size: int = factory.rng.randint(SORTED_KEYS_MIN_LEN, SORTED_KEYS_MAX_LEN)
    keys: list[str] = _unique_words(
        factory=factory,
        size=size,
        max_len=SORTED_KEY_SLICE_LEN,
    )
    mapping: dict[str, int] = {
        key: factory.rng.randint(SORTED_VALUE_MIN, SORTED_VALUE_MAX)
        for key in keys
    }
    return _task_payload(
        spec=spec,
        input_data={KEY_MAPPING_DINAMIC_POSTFIX_KZLL: mapping},
        expected_result=sorted(mapping),
    )


def recipe_cl1_unique_sorted(
    factory: FakeDataFactory,
    spec: RecipeSpec,
) -> TaskPayload:
    """Build a task where answer is sorted unique integers.

    Args:
        factory: Runtime data factory with random generator.
        spec: Recipe-capable task specification.

    Returns:
        Generated task payload.
    """
    span: int = factory.rng.randint(UNIQUE_SPAN_MIN, UNIQUE_SPAN_MAX)
    pool: list[int] = [
        factory.rng.randint(UNIQUE_VALUE_MIN, UNIQUE_VALUE_MAX)
        for _ in range(span)
    ]
    duplicates_count: int = factory.rng.randint(
        UNIQUE_DUPLICATES_MIN,
        UNIQUE_DUPLICATES_MAX,
    )
    nums: list[int] = pool + [
        factory.rng.choice(pool) for _ in range(duplicates_count)
    ]
    nums = sorted(nums, key=lambda _: factory.rng.random())
    return _task_payload(
        spec=spec,
        input_data={KEY_NUMS_DINAMIC_POSTFIX_KZLL: nums},
        expected_result=sorted(set(nums)),
    )


def recipe_cl1_merge_two_lists(
    factory: FakeDataFactory,
    spec: RecipeSpec,
) -> TaskPayload:
    """Build a task where answer is concatenation of two lists.

    Args:
        factory: Runtime data factory with random generator.
        spec: Recipe-capable task specification.

    Returns:
        Generated task payload.
    """
    first: list[int] = _random_int_list(
        factory=factory,
        min_len=MERGE_LIST_MIN_LEN,
        max_len=MERGE_LIST_MAX_LEN,
        min_value=MERGE_VALUE_MIN,
        max_value=MERGE_VALUE_MAX,
    )
    second: list[int] = _random_int_list(
        factory=factory,
        min_len=MERGE_LIST_MIN_LEN,
        max_len=MERGE_LIST_MAX_LEN,
        min_value=MERGE_VALUE_MIN,
        max_value=MERGE_VALUE_MAX,
    )
    return _task_payload(
        spec=spec,
        input_data={
            KEY_FIRST_DINAMIC_POSTFIX_KZLL: first,
            KEY_SECOND_DINAMIC_POSTFIX_KZLL: second,
        },
        expected_result=first + second,
    )


def recipe_cl1_count_char(
    factory: FakeDataFactory,
    spec: RecipeSpec,
) -> TaskPayload:
    """Build a task where answer is character frequency in text.

    Args:
        factory: Runtime data factory with random generator.
        spec: Recipe-capable task specification.

    Returns:
        Generated task payload.
    """
    length: int = factory.rng.randint(TEXT_MIN_LEN, TEXT_MAX_LEN)
    text: str = "".join(
        factory.rng.choices(ALPHABET_DINAMIC_POSTFIX_KZLL, k=length),
    )
    ch: str = factory.rng.choice(ALPHABET_DINAMIC_POSTFIX_KZLL)
    return _task_payload(
        spec=spec,
        input_data={
            KEY_TEXT_DINAMIC_POSTFIX_KZLL: text,
            KEY_CH_DINAMIC_POSTFIX_KZLL: ch,
        },
        expected_result=text.count(ch),
    )


INPUT_RECIPES: dict[str, RecipeFn] = {
    RECIPE_SUM_NUMS_DINAMIC_POSTFIX_KZLL: recipe_cl1_sum_nums,
    RECIPE_LEN_ITEMS_DINAMIC_POSTFIX_KZLL: recipe_cl1_len_items,
    RECIPE_LAST_ELEM_DINAMIC_POSTFIX_KZLL: recipe_cl1_last_elem,
    RECIPE_DICT_GET_DEFAULT_DINAMIC_POSTFIX_KZLL: (
        recipe_cl1_dict_get_default
    ),
    RECIPE_KEYS_SORTED_DINAMIC_POSTFIX_KZLL: recipe_cl1_keys_sorted,
    RECIPE_UNIQUE_SORTED_DINAMIC_POSTFIX_KZLL: recipe_cl1_unique_sorted,
    RECIPE_MERGE_TWO_LISTS_DINAMIC_POSTFIX_KZLL: (recipe_cl1_merge_two_lists),
    RECIPE_COUNT_CHAR_DINAMIC_POSTFIX_KZLL: recipe_cl1_count_char,
}


def run_input_recipe(factory: object, spec: RecipeSpec) -> TaskPayload:
    """Build a task payload via a registered recipe.

    Args:
        factory: Runtime fake-data factory object.
        spec: Declarative task spec with recipe id.

    Returns:
        Generated task payload dictionary.

    Raises:
        TypeError: If factory is not FakeDataFactory.
        ValueError: If spec.input_recipe is empty.
        KeyError: If recipe id is not registered.
    """
    if not isinstance(factory, FakeDataFactory):
        raise TypeError(ERR_FACTORY_INVALID_DINAMIC_POSTFIX_KZLL)

    recipe_name: str | None = spec.input_recipe
    if not recipe_name:
        raise ValueError(ERR_RECIPE_REQUIRED_DINAMIC_POSTFIX_KZLL)

    recipe: RecipeFn | None = INPUT_RECIPES.get(recipe_name)
    if recipe is None:
        raise KeyError(
            ERR_RECIPE_UNKNOWN_DINAMIC_POSTFIX_KZLL.format(
                name=recipe_name,
            ),
        )
    return recipe(factory, spec)
