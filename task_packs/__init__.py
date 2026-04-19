"""
This module exposes the public API for task packs, providing discovery
helpers and a way to load task variants for a given content pack.

It works as a thin facade over an internal registry module, forwarding
calls to list packs, labels, and discovery issues, and to fetch
variants while ensuring registry descriptors are refreshed first.

It defines AVAILABLE_PACKS as the current tuple of discovered pack IDs
and re-exports key functions via __all__ for convenient import.

The functions list_available_pack_labels, list_available_packs,
list_discovery_issues, pack_label_by_id, and refresh_pack_descriptors
all delegate directly to corresponding registry functions, keeping the
caller insulated from the registry implementation.

The main function get_variants takes a content-pack ID and an optional
generator object, refreshes the pack descriptors, and then returns a
list of Variant tuples from registry.get_variants_for_pack, raising
ValueError if the pack ID is unknown.

Within the larger system, this module serves as the stable interface
through which task-generation logic discovers available content packs
and retrieves their task templates.
"""

from __future__ import annotations

from typing import Final

from . import registry
from .pack_types import Variant
from .registry import PackDiscoveryIssue, PackLabel

type PackGenerator = object | None

AVAILABLE_PACKS: Final[tuple[str, ...]] = registry.list_available_packs()

__all__: Final[tuple[str, ...]] = (
    "AVAILABLE_PACKS",
    "get_variants",
    "list_discovery_issues",
    "list_available_pack_labels",
    "list_available_packs",
    "pack_label_by_id",
    "refresh_pack_descriptors",
)


def list_available_pack_labels() -> tuple[PackLabel, ...]:
    """Return labels for all discovered non-mixed content packs.

    Returns:
        Tuple of pack id/label pairs used by selectors.
    """
    return registry.list_available_pack_labels()


def list_available_packs() -> tuple[str, ...]:
    """Return discovered regular content-pack identifiers.

    Returns:
        Stable tuple of pack ids excluding the virtual mixed pack.
    """
    return registry.list_available_packs()


def list_discovery_issues() -> tuple[PackDiscoveryIssue, ...]:
    """Return non-fatal pack discovery diagnostics.

    Returns:
        Tuple of issues produced during module discovery.
    """
    return registry.list_discovery_issues()


def pack_label_by_id(pack_id: str) -> str:
    """Resolve a human-readable label for one pack id.

    Args:
        pack_id: Pack identifier to resolve.

    Returns:
        Pack label when known, otherwise the original pack id.
    """
    return registry.pack_label_by_id(pack_id)


def refresh_pack_descriptors() -> None:
    """Clear cached discovery results for the task-pack registry."""
    registry.refresh_pack_descriptors()


def get_variants(
    content_pack: str,
    generator: PackGenerator,
) -> list[Variant]:
    """Load task variants for one discovered content pack.

    Args:
        content_pack: Pack id as returned by
        :func:`list_available_packs`.
        generator: Optional generator for packs whose ``get_variants``
            uses a one-argument signature.

    Returns:
        Variant tuples (factory, collection names, task id) for the
        pack.

    Raises:
        ValueError: If ``content_pack`` is not registered.
    """
    refresh_pack_descriptors()
    return registry.get_variants_for_pack(
        content_pack,
        generator=generator,
    )
