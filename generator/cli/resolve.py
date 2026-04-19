"""
This module constructs the effective CLI configuration for the task
generator, resolving defaults and selecting an appropriate content
pack.

It works by combining constant defaults from generator.settings with a
content-pack resolver that inspects installed packs and applies
fallback rules when the configured pack is missing or mixed.

It defines a PackIds type alias and small helpers _available_pack_ids,
_fallback_pack_id, and _resolved_content_pack to encapsulate discovery
and selection of a usable pack ID, including handling the special
“mixed” pack and the “no packs installed” case.

The main function resolve_config returns an AppConfig instance populated
with default values for counts, seeding, display options, export
behavior, session parameters, and the resolved content_pack, acting as
the central configuration source for the rest of the CLI workflow.
"""

from __future__ import annotations

from collections.abc import Iterable

from generator.app_config import AppConfig
from generator.settings import (
    DEFAULT_CONTENT_PACK,
    DEFAULT_COUNT,
    DEFAULT_DATA_ORDER,
    DEFAULT_DATA_QUALITY,
    DEFAULT_DATA_VOLUME,
    DEFAULT_DOMAIN,
    DEFAULT_EXPORT_FILE,
    DEFAULT_EXPORT_FORMAT,
    DEFAULT_FOCUS_TOOL,
    DEFAULT_HINTS_STEP,
    DEFAULT_INVERSE_RATE,
    DEFAULT_MODE,
    DEFAULT_PROFILE,
    DEFAULT_SEED,
    DEFAULT_SESSION_SIZE,
    DEFAULT_SHOW_FULL_EXAMPLE,
    DEFAULT_SHOW_SOLUTION,
    DEFAULT_SOLUTION_FILE,
    DEFAULT_STAGE,
    DEFAULT_STATE_FILE,
    DEFAULT_STORY_MODE,
    DEFAULT_STRICT_TYPES,
    DEFAULT_SURPRISE_ME,
    DEFAULT_TOPIC,
)
from messages import (
    EMPTY_PACK_ID_DINAMIC_POSTFIX_DZXP,
    MIXED_PACK_ID_DINAMIC_POSTFIX_DZXP,
)
from task_packs import list_available_packs

type PackIds = frozenset[str]


def _available_pack_ids() -> PackIds:
    """Return all currently available pack identifiers.

    Returns:
        Immutable set of available pack IDs.
    """
    return frozenset(list_available_packs())


def _fallback_pack_id(pack_ids: Iterable[str]) -> str:
    """Pick deterministic fallback pack identifier.

    Args:
        pack_ids: Available pack IDs.

    Returns:
        First ID in lexicographic order.
    """
    return min(pack_ids)


def _resolved_content_pack(default_pack: str) -> str:
    """Pick a usable content pack name, falling back when needed.

    When no content packs are installed, returns an empty string.
    The virtual ``mixed`` pack is valid only while at least one regular
    pack exists. Otherwise the configured name is used when present;
    if it is missing, the first pack id in lexicographic order is used.

    Args:
        default_pack: Pack id from configuration.

    Returns:
        Resolved pack id, or ``""`` when nothing is available.
    """
    available = _available_pack_ids()
    if not available:
        return EMPTY_PACK_ID_DINAMIC_POSTFIX_DZXP
    if default_pack == MIXED_PACK_ID_DINAMIC_POSTFIX_DZXP:
        return default_pack
    if default_pack in available:
        return default_pack
    return _fallback_pack_id(available)


def resolve_config() -> AppConfig:
    """Construct CLI configuration from repository defaults.

    Returns:
        Immutable configuration populated from ``generator.settings``
        defaults and resolved content-pack selection.
    """
    return AppConfig(
        count=DEFAULT_COUNT,
        seed=DEFAULT_SEED,
        show_solution=DEFAULT_SHOW_SOLUTION,
        show_full_example=DEFAULT_SHOW_FULL_EXAMPLE,
        topic=DEFAULT_TOPIC,
        stage=DEFAULT_STAGE,
        data_volume=DEFAULT_DATA_VOLUME,
        data_order=DEFAULT_DATA_ORDER,
        data_quality=DEFAULT_DATA_QUALITY,
        profile=DEFAULT_PROFILE,
        domain=DEFAULT_DOMAIN,
        surprise_me=DEFAULT_SURPRISE_ME,
        focus_tool=DEFAULT_FOCUS_TOOL,
        mode=DEFAULT_MODE,
        solution_file=DEFAULT_SOLUTION_FILE,
        state_file=DEFAULT_STATE_FILE,
        export_format=DEFAULT_EXPORT_FORMAT,
        export_file=DEFAULT_EXPORT_FILE,
        story_mode=DEFAULT_STORY_MODE,
        session_size=DEFAULT_SESSION_SIZE,
        inverse_rate=DEFAULT_INVERSE_RATE,
        hints_step=DEFAULT_HINTS_STEP,
        strict_types=DEFAULT_STRICT_TYPES,
        content_pack=_resolved_content_pack(DEFAULT_CONTENT_PACK),
    )
