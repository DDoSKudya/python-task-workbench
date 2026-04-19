"""
This module implements the core “task generator” used to pick and shape
tasks from content packs according to profiles, randomness, exclusions,
and metadata constraints.

It works by fetching task variants from a configured content pack,
applying topic and exclusion filters, sampling with a seeded
FakeDataFactory, and then validating and enriching the chosen task with
profile-derived constraints and default hints.

It defines type aliases for profile presets, variant factories, and
variant tuples, plus many constants that describe profiles,
surprise-mode ranges, constraint messages, and indices into the variant
tuple structure.

The TaskGeneratorCore class holds generation settings (stage, data
volume, order, quality, profile, domain, surprise-me flag, focus tool,
and content pack) and applies a profile preset or “surprise”
randomization to these parameters before generating tasks.

Helper methods like _variants, _filtered_variants,
_variant_matches_topic, _variant_not_excluded_id, and
_variant_not_excluded_family control which variants are eligible, using
topic tags, explicit ID exclusions, and derived “family” IDs.

Quality checks in _is_task_reasonable ensure that generated tasks have
required fields and that description text markers (for groups, dicts,
lists, tuples) are consistent with the expected results container type.

The _with_profile_constraints method merges profile-specific constraints
and fills in missing difficulty hints, common pitfalls, real-world
analogy, and estimated complexity, producing a richer Task instance.

The main generate method orchestrates the process: it builds a
FakeDataFactory, optionally randomizes the profile, retrieves and
filters variants, retries sampling up to a configured limit while
enforcing focus-tool and “reasonableness” filters, and finally returns a
suitably constrained task or raises a descriptive error, making this
class the central engine behind task selection for the rest of the
system.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from dataclasses import replace
from typing import Final

from messages import (
    CONSTRAINT_DIRTY_DATA_DINAMIC_POSTFIX_HTIQ,
    CONSTRAINT_GROUPED_ORDER_DINAMIC_POSTFIX_HTIQ,
    CONSTRAINT_LARGE_VOLUME_DINAMIC_POSTFIX_HTIQ,
    CONSTRAINT_SORTED_ORDER_DINAMIC_POSTFIX_HTIQ,
    CONSTRAINT_STAGE_THREE_DINAMIC_POSTFIX_HTIQ,
    DATA_ORDER_GROUPED_DINAMIC_POSTFIX_HTIQ,
    DATA_ORDER_RANDOM_DINAMIC_POSTFIX_HTIQ,
    DATA_ORDER_SORTED_DINAMIC_POSTFIX_HTIQ,
    DATA_QUALITY_CLEAN_DINAMIC_POSTFIX_HTIQ,
    DATA_QUALITY_DIRTY_DINAMIC_POSTFIX_HTIQ,
    DATA_VOLUME_LARGE_DINAMIC_POSTFIX_HTIQ,
    DATA_VOLUME_MEDIUM_DINAMIC_POSTFIX_HTIQ,
    DATA_VOLUME_SMALL_DINAMIC_POSTFIX_HTIQ,
    DEFAULT_COMMON_PITFALL_1_DINAMIC_POSTFIX_HTIQ,
    DEFAULT_COMMON_PITFALL_2_DINAMIC_POSTFIX_HTIQ,
    DEFAULT_DIFFICULTY_HINT_1_DINAMIC_POSTFIX_HTIQ,
    DEFAULT_DIFFICULTY_HINT_2_DINAMIC_POSTFIX_HTIQ,
    DEFAULT_ESTIMATED_COMPLEXITY_DINAMIC_POSTFIX_HTIQ,
    DEFAULT_REAL_WORLD_ANALOGY_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_ALL_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_ANALYTICS_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_DEVOPS_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_ECOMMERCE_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_EDUCATION_DINAMIC_POSTFIX_HTIQ,
    ERROR_GENERATION_FAILED_DINAMIC_POSTFIX_HTIQ,
    ERROR_NO_VARIANTS_DINAMIC_POSTFIX_HTIQ,
    PROFILE_EDGE_CASES_DINAMIC_POSTFIX_HTIQ,
    PROFILE_INTERVIEW_TRAP_DINAMIC_POSTFIX_HTIQ,
    PROFILE_PRODUCTION_LIKE_DINAMIC_POSTFIX_HTIQ,
    PROFILE_STREAM_SIMULATION_DINAMIC_POSTFIX_HTIQ,
    STAGE_MIXED_DINAMIC_POSTFIX_HTIQ,
    STAGE_ONE_DINAMIC_POSTFIX_HTIQ,
    STAGE_THREE_DINAMIC_POSTFIX_HTIQ,
    STAGE_TWO_DINAMIC_POSTFIX_HTIQ,
    TEXT_MARKER_DICT_DINAMIC_POSTFIX_HTIQ,
    TEXT_MARKER_GROUP_DINAMIC_POSTFIX_HTIQ,
    TEXT_MARKER_LIST_DINAMIC_POSTFIX_HTIQ,
    TEXT_MARKER_TUPLE_DINAMIC_POSTFIX_HTIQ,
    TOOL_TOKEN_DELIMITER_DINAMIC_POSTFIX_HTIQ,
)
from task_packs import get_variants as get_pack_variants

from ..fake_data import FakeDataFactory
from ..models import GeneratedTask, task_family_from_id
from ..settings import (
    DEFAULT_CONTENT_PACK,
    DEFAULT_DATA_ORDER,
    DEFAULT_DATA_QUALITY,
    DEFAULT_DATA_VOLUME,
    DEFAULT_DOMAIN,
    DEFAULT_FOCUS_TOOL,
    DEFAULT_PROFILE,
    DEFAULT_STAGE,
    DEFAULT_SURPRISE_ME,
    DEFAULT_TOPIC,
)

type ProfilePreset = tuple[str, str, str, str | None]
type TaskLike = GeneratedTask | Mapping[str, object]
type VariantFactory = Callable[[FakeDataFactory], TaskLike]
type Variant = tuple[VariantFactory, tuple[str, ...], str]

PROFILE_PRESET_BY_NAME: Final[dict[str, ProfilePreset]] = {
    PROFILE_PRODUCTION_LIKE_DINAMIC_POSTFIX_HTIQ: (
        DATA_VOLUME_LARGE_DINAMIC_POSTFIX_HTIQ,
        DATA_ORDER_SORTED_DINAMIC_POSTFIX_HTIQ,
        DATA_QUALITY_DIRTY_DINAMIC_POSTFIX_HTIQ,
        None,
    ),
    PROFILE_INTERVIEW_TRAP_DINAMIC_POSTFIX_HTIQ: (
        DATA_VOLUME_MEDIUM_DINAMIC_POSTFIX_HTIQ,
        DATA_ORDER_GROUPED_DINAMIC_POSTFIX_HTIQ,
        DATA_QUALITY_DIRTY_DINAMIC_POSTFIX_HTIQ,
        STAGE_TWO_DINAMIC_POSTFIX_HTIQ,
    ),
    PROFILE_STREAM_SIMULATION_DINAMIC_POSTFIX_HTIQ: (
        DATA_VOLUME_LARGE_DINAMIC_POSTFIX_HTIQ,
        DATA_ORDER_RANDOM_DINAMIC_POSTFIX_HTIQ,
        DATA_QUALITY_CLEAN_DINAMIC_POSTFIX_HTIQ,
        STAGE_THREE_DINAMIC_POSTFIX_HTIQ,
    ),
    PROFILE_EDGE_CASES_DINAMIC_POSTFIX_HTIQ: (
        DATA_VOLUME_SMALL_DINAMIC_POSTFIX_HTIQ,
        DATA_ORDER_RANDOM_DINAMIC_POSTFIX_HTIQ,
        DATA_QUALITY_DIRTY_DINAMIC_POSTFIX_HTIQ,
        None,
    ),
}
SURPRISE_DATA_VOLUMES: Final[tuple[str, ...]] = (
    DATA_VOLUME_SMALL_DINAMIC_POSTFIX_HTIQ,
    DATA_VOLUME_MEDIUM_DINAMIC_POSTFIX_HTIQ,
    DATA_VOLUME_LARGE_DINAMIC_POSTFIX_HTIQ,
)
SURPRISE_DATA_ORDERS: Final[tuple[str, ...]] = (
    DATA_ORDER_RANDOM_DINAMIC_POSTFIX_HTIQ,
    DATA_ORDER_SORTED_DINAMIC_POSTFIX_HTIQ,
    DATA_ORDER_GROUPED_DINAMIC_POSTFIX_HTIQ,
)
SURPRISE_DATA_QUALITIES: Final[tuple[str, ...]] = (
    DATA_QUALITY_CLEAN_DINAMIC_POSTFIX_HTIQ,
    DATA_QUALITY_DIRTY_DINAMIC_POSTFIX_HTIQ,
)
SURPRISE_STAGES: Final[tuple[str, ...]] = (
    STAGE_ONE_DINAMIC_POSTFIX_HTIQ,
    STAGE_TWO_DINAMIC_POSTFIX_HTIQ,
    STAGE_THREE_DINAMIC_POSTFIX_HTIQ,
    STAGE_MIXED_DINAMIC_POSTFIX_HTIQ,
)
SURPRISE_DOMAINS: Final[tuple[str, ...]] = (
    DOMAIN_ALL_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_ECOMMERCE_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_ANALYTICS_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_DEVOPS_DINAMIC_POSTFIX_HTIQ,
    DOMAIN_EDUCATION_DINAMIC_POSTFIX_HTIQ,
)
GENERATION_RETRY_LIMIT: Final[int] = 7
DEFAULT_DIFFICULTY_HINTS: Final[tuple[str, str]] = (
    DEFAULT_DIFFICULTY_HINT_1_DINAMIC_POSTFIX_HTIQ,
    DEFAULT_DIFFICULTY_HINT_2_DINAMIC_POSTFIX_HTIQ,
)
DEFAULT_COMMON_PITFALLS: Final[tuple[str, str]] = (
    DEFAULT_COMMON_PITFALL_1_DINAMIC_POSTFIX_HTIQ,
    DEFAULT_COMMON_PITFALL_2_DINAMIC_POSTFIX_HTIQ,
)
VARIANT_FACTORY_INDEX: Final[int] = 0
VARIANT_TOPICS_INDEX: Final[int] = 1
VARIANT_TASK_ID_INDEX: Final[int] = 2


class TaskGeneratorCore:
    """Core implementation for profile-aware task generation."""

    def __init__(
        self,
        seed: int | None = None,
        *,
        stage: str = DEFAULT_STAGE,
        data_volume: str = DEFAULT_DATA_VOLUME,
        data_order: str = DEFAULT_DATA_ORDER,
        data_quality: str = DEFAULT_DATA_QUALITY,
        profile: str = DEFAULT_PROFILE,
        domain: str = DEFAULT_DOMAIN,
        surprise_me: bool = DEFAULT_SURPRISE_ME,
        focus_tool: str = DEFAULT_FOCUS_TOOL,
        content_pack: str = DEFAULT_CONTENT_PACK,
    ) -> None:
        """Initialize a task generator core instance.

        Args:
            seed: Optional random seed for deterministic generation.
            stage: Stage selector.
            data_volume: Data volume profile.
            data_order: Data ordering profile.
            data_quality: Data quality profile.
            profile: Scenario profile preset.
            domain: Domain filter.
            surprise_me: Whether to randomize generation settings.
            focus_tool: Preferred optimal tool token.
            content_pack: Source content pack for variants.
        """
        self.seed = seed
        self.stage = stage
        self.data_volume = data_volume
        self.data_order = data_order
        self.data_quality = data_quality
        self.profile = profile
        self.domain = domain
        self.surprise_me = surprise_me
        self.focus_tool = focus_tool
        self.content_pack = content_pack
        self._apply_profile()

    def _apply_profile(self) -> None:
        """Apply profile presets to generation attributes.

        Returns:
            None.
        """
        preset = PROFILE_PRESET_BY_NAME.get(self.profile)
        if preset is None:
            return
        data_volume, data_order, data_quality, mixed_stage_target = preset
        self.data_volume = data_volume
        self.data_order = data_order
        self.data_quality = data_quality
        if (
            mixed_stage_target
            and self.stage == STAGE_MIXED_DINAMIC_POSTFIX_HTIQ
        ):
            self.stage = mixed_stage_target

    def _apply_surprise_profile(self, factory: FakeDataFactory) -> None:
        """Randomize profile-relevant fields using factory RNG.

        Args:
            factory: Fake data factory with an initialized RNG.

        Returns:
            None.
        """
        self.data_volume = factory.rng.choice(SURPRISE_DATA_VOLUMES)
        self.data_order = factory.rng.choice(SURPRISE_DATA_ORDERS)
        self.data_quality = factory.rng.choice(SURPRISE_DATA_QUALITIES)
        self.stage = factory.rng.choice(SURPRISE_STAGES)
        self.domain = factory.rng.choice(SURPRISE_DOMAINS)

    def _coerce_task(self, candidate_raw: TaskLike) -> GeneratedTask:
        """Convert a task-like object to a `Task` instance.

        Args:
            candidate_raw: Task-like payload from a variant callable.

        Returns:
            A normalized `Task` instance.
        """
        return (
            candidate_raw
            if isinstance(candidate_raw, GeneratedTask)
            else GeneratedTask.from_dict(dict(candidate_raw))
        )

    def _candidate_from_variant(
        self,
        *,
        factory: FakeDataFactory,
        variants: list[Variant],
    ) -> GeneratedTask:
        """Generate one candidate task from a random variant.

        Args:
            factory: Fake data factory with initialized RNG.
            variants: Available variants to sample from.

        Returns:
            Coerced task instance from sampled variant output.
        """
        variant = factory.rng.choice(variants)
        candidate_raw = variant[VARIANT_FACTORY_INDEX](factory)
        return self._coerce_task(candidate_raw)

    def _passes_candidate_filters(self, task: GeneratedTask) -> bool:
        """Return whether candidate task passes quality and tool
        filters.

        Args:
            task: Candidate task.

        Returns:
            ``True`` when task is reasonable and matches focus tool.
        """
        return self._is_task_reasonable(task) and self._matches_focus_tool(
            task
        )

    def generate(
        self,
        topic: str = DEFAULT_TOPIC,
        excluded_task_ids: set[str] | None = None,
        excluded_families: set[str] | None = None,
    ) -> GeneratedTask:
        """Generate a task using current profile and filtering settings.

        Args:
            topic: Optional topic filter.
            excluded_task_ids: Task IDs to exclude.
            excluded_families: Task families to exclude.

        Returns:
            A generated task adjusted by profile constraints.

        Raises:
            ValueError: If no valid task can be generated.
        """
        factory = FakeDataFactory(seed=self.seed)
        if self.surprise_me:
            self._apply_surprise_profile(factory)
        variants = self._filtered_variants(
            topic=topic,
            excluded_task_ids=excluded_task_ids,
            excluded_families=excluded_families,
        )
        if not variants:
            raise ValueError(
                ERROR_NO_VARIANTS_DINAMIC_POSTFIX_HTIQ.format(topic=topic)
            )
        last_task: GeneratedTask | None = None
        for _ in range(GENERATION_RETRY_LIMIT):
            candidate = self._candidate_from_variant(
                factory=factory,
                variants=variants,
            )
            if self._passes_candidate_filters(candidate):
                return self._with_profile_constraints(candidate)
            last_task = candidate
        if last_task is not None:
            return self._with_profile_constraints(last_task)
        raise ValueError(ERROR_GENERATION_FAILED_DINAMIC_POSTFIX_HTIQ)

    def _matches_focus_tool(self, task: GeneratedTask) -> bool:
        """Check whether a task matches the focus tool constraint.

        Args:
            task: Candidate task.

        Returns:
            True if the task satisfies the focus tool filter.
        """
        if self.focus_tool == DEFAULT_FOCUS_TOOL:
            return True
        if not task.optimal_tool:
            return False
        return (
            task.optimal_tool.split(TOOL_TOKEN_DELIMITER_DINAMIC_POSTFIX_HTIQ)[
                -1
            ].lower()
            == self.focus_tool.lower()
        )

    def _filtered_variants(
        self,
        *,
        topic: str,
        excluded_task_ids: set[str] | None,
        excluded_families: set[str] | None,
    ) -> list[Variant]:
        """Return variants filtered by topic and exclusion settings.

        Args:
            topic: Optional topic filter.
            excluded_task_ids: Task IDs to exclude.
            excluded_families: Task families to exclude.

        Returns:
            Filtered list of variants.
        """
        return [
            variant
            for variant in self._variants()
            if self._variant_matches_topic(variant=variant, topic=topic)
            and self._variant_not_excluded_id(
                variant=variant,
                excluded_task_ids=excluded_task_ids,
            )
            and self._variant_not_excluded_family(
                variant=variant,
                excluded_families=excluded_families,
            )
        ]

    def _variant_matches_topic(self, *, variant: Variant, topic: str) -> bool:
        """Return whether a variant matches the selected topic.

        Args:
            variant: Variant tuple to evaluate.
            topic: Topic filter value.

        Returns:
            ``True`` if topic is default or variant supports topic.
        """
        _, variant_topics, _ = variant
        return topic == DEFAULT_TOPIC or topic in variant_topics

    def _variant_not_excluded_id(
        self,
        *,
        variant: Variant,
        excluded_task_ids: set[str] | None,
    ) -> bool:
        """Return whether variant task ID is allowed.

        Args:
            variant: Variant tuple to evaluate.
            excluded_task_ids: Explicitly excluded task IDs.

        Returns:
            ``True`` when variant ID is not excluded.
        """
        _, _, variant_task_id = variant
        return (
            variant_task_id not in excluded_task_ids
            if excluded_task_ids
            else True
        )

    def _variant_not_excluded_family(
        self,
        *,
        variant: Variant,
        excluded_families: set[str] | None,
    ) -> bool:
        """Return whether variant family is allowed.

        Args:
            variant: Variant tuple to evaluate.
            excluded_families: Excluded family IDs.

        Returns:
            ``True`` when variant family is not excluded.
        """
        if not excluded_families:
            return True
        _, _, variant_task_id = variant
        family = task_family_from_id(variant_task_id)
        return family not in excluded_families

    def _profile_constraints(self) -> tuple[str, ...]:
        """Build additional constraints derived from profile settings.

        Returns:
            A tuple of profile-specific constraints.
        """
        constraints: list[str] = []
        if self.data_volume == DATA_VOLUME_LARGE_DINAMIC_POSTFIX_HTIQ:
            constraints.append(CONSTRAINT_LARGE_VOLUME_DINAMIC_POSTFIX_HTIQ)
        if self.data_order == DATA_ORDER_SORTED_DINAMIC_POSTFIX_HTIQ:
            constraints.append(CONSTRAINT_SORTED_ORDER_DINAMIC_POSTFIX_HTIQ)
        elif self.data_order == DATA_ORDER_GROUPED_DINAMIC_POSTFIX_HTIQ:
            constraints.append(CONSTRAINT_GROUPED_ORDER_DINAMIC_POSTFIX_HTIQ)
        if self.data_quality == DATA_QUALITY_DIRTY_DINAMIC_POSTFIX_HTIQ:
            constraints.append(CONSTRAINT_DIRTY_DATA_DINAMIC_POSTFIX_HTIQ)
        if self.stage == STAGE_THREE_DINAMIC_POSTFIX_HTIQ:
            constraints.append(CONSTRAINT_STAGE_THREE_DINAMIC_POSTFIX_HTIQ)
        return tuple(constraints)

    def _with_profile_constraints(self, task: GeneratedTask) -> GeneratedTask:
        """Merge profile constraints and fallback metadata into a task.

        Args:
            task: Original generated task.

        Returns:
            A task augmented with profile-aware metadata.
        """
        merged = list(task.constraints)
        for item in self._profile_constraints():
            if item not in merged:
                merged.append(item)
        difficulty_hints = task.difficulty_hints or DEFAULT_DIFFICULTY_HINTS
        common_pitfalls = task.common_pitfalls or DEFAULT_COMMON_PITFALLS
        analogy = (
            task.real_world_analogy
            or DEFAULT_REAL_WORLD_ANALOGY_DINAMIC_POSTFIX_HTIQ
        )
        complexity = (
            task.estimated_complexity
            or DEFAULT_ESTIMATED_COMPLEXITY_DINAMIC_POSTFIX_HTIQ
        )
        return replace(
            task,
            constraints=tuple(merged),
            difficulty_hints=tuple(difficulty_hints),
            common_pitfalls=tuple(common_pitfalls),
            real_world_analogy=analogy,
            estimated_complexity=complexity,
        )

    def _is_task_reasonable(self, task: GeneratedTask) -> bool:
        """Check basic validity and textual consistency of a task.

        Args:
            task: Candidate task.

        Returns:
            True if the task appears valid for output.
        """
        if not self._has_required_task_fields(task):
            return False
        text = task.description.lower()
        if self._mentions_group_or_dict(text) and not isinstance(
            task.expected_result, dict
        ):
            return False
        return self._matches_expected_shape_hint(
            text=text,
            expected=task.expected_result,
        )

    def _has_required_task_fields(self, task: GeneratedTask) -> bool:
        """Return whether task has mandatory non-empty fields.

        Args:
            task: Candidate task.

        Returns:
            ``True`` when title, description, input and expected exist.
        """
        return bool(
            task.title
            and task.description
            and task.input_data
            and task.expected_result is not None
        )

    def _mentions_group_or_dict(self, text: str) -> bool:
        """Return whether task description hints dict-like output.

        Args:
            text: Lower-cased task description.

        Returns:
            ``True`` when description mentions group or dict markers.
        """
        return (
            TEXT_MARKER_GROUP_DINAMIC_POSTFIX_HTIQ in text
            or TEXT_MARKER_DICT_DINAMIC_POSTFIX_HTIQ in text
        )

    def _matches_expected_shape_hint(
        self, *, text: str, expected: object
    ) -> bool:
        """Return whether expected result matches tuple/list hints.

        Args:
            text: Lower-cased task description.
            expected: Expected result value.

        Returns:
            ``True`` when shape hints are consistent with expected type.
        """
        mentions_seq = (
            TEXT_MARKER_TUPLE_DINAMIC_POSTFIX_HTIQ in text
            or TEXT_MARKER_LIST_DINAMIC_POSTFIX_HTIQ in text
        )
        return (
            isinstance(expected, (list, tuple, dict)) if mentions_seq else True
        )

    def _variants(self) -> list[Variant]:
        """Return all variants from the configured content pack.

        Returns:
            List of task variants for the active content pack.
        """
        return get_pack_variants(
            self.content_pack, self
        )  # pyright: ignore[reportReturnType]
