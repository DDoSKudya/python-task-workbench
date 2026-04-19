"""Shared type aliases for task pack variant contracts.

Type Aliases:
    VariantPayload: Generated payload dictionary for one task variant.
    VariantFactory: Callable that builds payload from runtime factory.
    Variant: Tuple describing callable, collections, and task id.
"""

from __future__ import annotations

from collections.abc import Callable

type VariantPayload = dict[str, object]
type VariantFactory = Callable[[object], VariantPayload]
type Variant = tuple[VariantFactory, tuple[str, ...], str]
