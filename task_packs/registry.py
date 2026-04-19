"""
This module discovers content packs on disk, loads their manifests and
code, and exposes a unified way to list packs and obtain their task
variants.

It works by scanning a configured content-modules directory, validating
module.json manifests, dynamically importing optional module.py and
generator.py, and building PackDescriptor objects that know how to
produce Variant lists for each pack.

It defines dataclasses PackDescriptor, PackLabel, and PackDiscoveryIssue
to represent pack metadata, UI labels, and non-fatal discovery
diagnostics.

Helper functions _content_modules_root, _load_module_file,
_load_entry_module, and _load_pack_generator_module resolve paths and
import entry and generator modules using importlib.

The module supports two pack styles: declarative JSON-based packs
handled via load_task_specs_with_issues and
variants_from_specs_with_builders, and classic code-based packs that
expose a get_variants function in module.py.

_adapt_pack_input_generator and _adapt_pack_payload_generator wrap
optional build_input and build_payload callbacks from generator.py,
enforcing contracts for generated input and payload structures.

_coerce_variant_item, _normalize_variants_list, _invoke_get_variants,
and _adapt_get_variants normalize arbitrary get_variants outputs into
typed Variant triples and adapt both zero-arg and generator-arg
signatures.

_declarative_variants_getter and _fallback_module_getter construct
VariantsGetter callables for declarative or classic packs, while
_try_pack_descriptor ties together manifest validation, module loading,
getter selection, and issue collection for a single pack directory.

_discover_regular_packs_with_issues walks the content root, skips
ignored directories, accumulates descriptors and issues, and
_mixed_descriptor constructs a virtual “mixed” pack that concatenates
variants from all regular packs.

discover_pack_descriptors caches the full descriptor mapping (including
the mixed pack) with lru_cache, and refresh_pack_descriptors clears
this cache after code or data changes.

Public functions list_discovery_issues, list_available_packs,
list_available_pack_labels, and pack_label_by_id provide diagnostics,
pack IDs, id/label pairs, and label resolution for UI and configuration.

The main API get_variants_for_pack looks up a PackDescriptor by ID and
delegates to its get_variants callable, raising a descriptive error if
the requested pack is not supported, thus serving as the bridge between
the generator core and the pluggable pack ecosystem.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from functools import lru_cache
from types import ModuleType

from dataclasses import dataclass
from pathlib import Path
from typing import TypeGuard, cast

from messages import (
    ATTR_BUILD_INPUT_DINAMIC_POSTFIX_O8XF,
    ATTR_BUILD_PAYLOAD_DINAMIC_POSTFIX_O8XF,
    ATTR_GET_VARIANTS_DINAMIC_POSTFIX_O8XF,
    CONTENT_MODULES_DIR_NAME_DINAMIC_POSTFIX_O8XF,
    ENTRY_MODULE_FILE_NAME_DINAMIC_POSTFIX_O8XF,
    ENTRY_MODULE_QUALNAME_TEMPLATE_DINAMIC_POSTFIX_O8XF,
    ERR_INVALID_GENERATED_INPUT_DINAMIC_POSTFIX_US41,
    ERR_INVALID_GENERATED_PAYLOAD_DINAMIC_POSTFIX_US41,
    ERR_INVALID_VARIANTS_CALL_DINAMIC_POSTFIX_O8XF,
    ERR_UNSUPPORTED_PACK_DINAMIC_POSTFIX_O8XF,
    MANIFEST_FILE_NAME_DINAMIC_POSTFIX_O8XF,
    MIXED_PACK_ID_DINAMIC_POSTFIX_O8XF,
    MIXED_PACK_LABEL_DINAMIC_POSTFIX_O8XF,
    MSG_DECLARATIVE_ISSUES_TEMPLATE_DINAMIC_POSTFIX_O8XF,
    MSG_INVALID_MANIFEST_DINAMIC_POSTFIX_O8XF,
    MSG_NO_VARIANT_SOURCE_DINAMIC_POSTFIX_O8XF,
    PACK_GENERATOR_FILE_NAME_DINAMIC_POSTFIX_O8XF,
    PACK_GENERATOR_QUALNAME_TEMPLATE_DINAMIC_POSTFIX_O8XF,
)

from .declarative_tasks import (
    DeclarativeTaskSpec,
    PackInputGenerator,
    PackPayloadGenerator,
    load_task_specs_with_issues,
    variants_from_specs_with_builders,
)
from .module_manifest import ModuleManifest, load_manifest
from .pack_types import Variant, VariantFactory

IGNORED_DIRECTORY_NAMES: frozenset[str] = frozenset(
    {
        "schemas",
        "__pycache__",
    }
)

DISCOVERY_CACHE_SIZE: int = 1
VARIANT_TUPLE_LENGTH: int = 3
GENERATED_INPUT_TUPLE_LENGTH: int = 2


type VariantsGetter = Callable[[object | None], list[Variant]]
type DiscoveryResult = tuple[PackDescriptor | None, list[PackDiscoveryIssue]]


@dataclass(frozen=True, slots=True)
class PackDescriptor:
    """Runtime binding for one discovered content pack.

    Attributes:
        pack_id: Stable identifier from manifest.
        label: Human-readable name shown in selectors.
        get_variants: Callable returning task variants for the pack.
    """

    pack_id: str
    label: str
    get_variants: VariantsGetter


@dataclass(frozen=True, slots=True)
class PackLabel:
    """Identifier and human-readable label for UI lists.

    Attributes:
        pack_id: Pack key used in APIs and settings.
        label: Resolved display label for the pack.
    """

    pack_id: str
    label: str


@dataclass(frozen=True, slots=True)
class PackDiscoveryIssue:
    """Non-fatal discovery diagnostic for one module directory.

    Attributes:
        module_dir: Directory name under content modules root.
        message: Explanation suitable for logs or developer UI.
    """

    module_dir: str
    message: str


def _is_callable_object(value: object) -> TypeGuard[Callable[..., object]]:
    """Narrow object to a callable for static typing.

    Args:
        value: Arbitrary object, often from ``getattr``.

    Returns:
        ``True`` when ``value`` is callable.
    """
    return callable(value)


def _issue(module_dir: Path, message: str) -> PackDiscoveryIssue:
    """Create one discovery issue for a module directory.

    Args:
        module_dir: Pack directory that caused the issue.
        message: Human-readable issue text.

    Returns:
        Frozen issue payload.
    """
    return PackDiscoveryIssue(module_dir=module_dir.name, message=message)


def _content_modules_root() -> Path:
    """Resolve content modules directory next to package root.

    Returns:
        Absolute path to content modules directory.
    """
    project_root: Path = Path(__file__).resolve().parent.parent
    return project_root / CONTENT_MODULES_DIR_NAME_DINAMIC_POSTFIX_O8XF


def _load_module_file(
    module_dir: Path,
    *,
    file_name: str,
    qualname: str,
) -> ModuleType | None:
    """Import one module file from a pack directory.

    Args:
        module_dir: Pack directory that owns the module file.
        file_name: Relative module file name to load.
        qualname: Unique runtime module name.

    Returns:
        Loaded module object, or ``None`` on failure.
    """
    module_path: Path = module_dir / file_name
    if not module_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location(qualname, module_path)
    if spec is None or spec.loader is None:
        return None

    module: ModuleType = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _load_entry_module(module_dir: Path, pack_id: str) -> ModuleType | None:
    """Import ``module.py`` from a pack directory when present.

    Args:
        module_dir: Candidate pack directory.
        pack_id: Pack identifier for unique qualname.

    Returns:
        Loaded module or ``None``.
    """
    return _load_module_file(
        module_dir,
        file_name=ENTRY_MODULE_FILE_NAME_DINAMIC_POSTFIX_O8XF,
        qualname=ENTRY_MODULE_QUALNAME_TEMPLATE_DINAMIC_POSTFIX_O8XF.format(
            pack_id=pack_id,
        ),
    )


def _load_pack_generator_module(
    module_dir: Path,
    pack_id: str,
) -> ModuleType | None:
    """Import ``generator.py`` from a pack directory when present.

    Args:
        module_dir: Candidate pack directory.
        pack_id: Pack identifier for unique qualname.

    Returns:
        Loaded module or ``None``.
    """
    return _load_module_file(
        module_dir,
        file_name=PACK_GENERATOR_FILE_NAME_DINAMIC_POSTFIX_O8XF,
        qualname=(
            PACK_GENERATOR_QUALNAME_TEMPLATE_DINAMIC_POSTFIX_O8XF.format(
                pack_id=pack_id,
            )
        ),
    )


def _adapt_pack_input_generator(
    raw_builder: object,
) -> PackInputGenerator | None:
    """Wrap optional pack ``build_input`` callback.

    Args:
        raw_builder: Attribute read from ``generator.py``.

    Returns:
        Typed callback or ``None`` when attribute is not callable.
    """
    if not _is_callable_object(raw_builder):
        return None

    builder: Callable[..., object] = raw_builder

    def wrapper(
        factory_obj: object,
        spec: DeclarativeTaskSpec,
    ) -> tuple[dict[str, object], object]:
        """Run pack input generator callback.

        Args:
            factory_obj: Runtime fake-data factory object.
            spec: Declarative task specification.

        Returns:
            Pair of generated input payload and expected result.

        Raises:
            TypeError: If callback contract is invalid.
        """
        generated: object = builder(factory_obj, spec)
        if (
            not isinstance(generated, tuple)
            or len(generated) != GENERATED_INPUT_TUPLE_LENGTH
            or not isinstance(generated[0], dict)
        ):
            raise TypeError(ERR_INVALID_GENERATED_INPUT_DINAMIC_POSTFIX_US41)
        return generated[0], generated[1]

    return wrapper


def _adapt_pack_payload_generator(
    raw_builder: object,
) -> PackPayloadGenerator | None:
    """Wrap optional pack ``build_payload`` callback.

    Args:
        raw_builder: Attribute read from ``generator.py``.

    Returns:
        Typed callback or ``None`` when attribute is not callable.
    """
    if not _is_callable_object(raw_builder):
        return None

    builder: Callable[..., object] = raw_builder

    def wrapper(
        factory_obj: object,
        spec: DeclarativeTaskSpec,
    ) -> dict[str, object]:
        """Run pack payload generator callback.

        Args:
            factory_obj: Runtime fake-data factory object.
            spec: Declarative task specification.

        Returns:
            Payload mapping with optional field overrides.

        Raises:
            TypeError: If callback returns non-dictionary payload.
        """
        generated: object = builder(factory_obj, spec)
        if not isinstance(generated, dict):
            raise TypeError(ERR_INVALID_GENERATED_PAYLOAD_DINAMIC_POSTFIX_US41)
        return generated

    return wrapper


def _coerce_variant_item(item: object) -> Variant | None:
    """Validate one variant item from dynamic list.

    Args:
        item: Candidate element from ``get_variants`` return value.

    Returns:
        Valid variant triple or ``None``.
    """
    if not isinstance(item, tuple) or len(item) != VARIANT_TUPLE_LENGTH:
        return None

    factory, collections, task_id = item
    if not _is_callable_object(factory):
        return None
    if not isinstance(collections, tuple):
        return None
    if not all(isinstance(name, str) for name in collections):
        return None
    if not isinstance(task_id, str):
        return None

    typed_factory: VariantFactory = cast(VariantFactory, factory)
    return typed_factory, collections, task_id


def _normalize_variants_list(raw: object) -> list[Variant]:
    """Convert dynamic ``get_variants`` output into typed list.

    Args:
        raw: Return value from a pack ``get_variants`` implementation.

    Returns:
        List of valid variants.
    """
    if not isinstance(raw, list):
        return []

    variants: list[Variant] = []
    for item in raw:
        variant: Variant | None = _coerce_variant_item(item)
        if variant is not None:
            variants.append(variant)
    return variants


def _invoke_get_variants(
    raw_fn: Callable[..., object],
    *,
    generator: object | None,
    pack_id: str,
) -> object:
    """Call ``get_variants`` with zero- or one-argument form.

    Args:
        raw_fn: Callable bound from content module.
        generator: Optional generator object for one-argument form.
        pack_id: Pack id for diagnostics.

    Returns:
        Raw value returned by the provider.

    Raises:
        ValueError: If provider requires argument and no generator
        given.
    """
    try:
        return raw_fn()
    except TypeError:
        if generator is None:
            raise ValueError(
                ERR_INVALID_VARIANTS_CALL_DINAMIC_POSTFIX_O8XF.format(
                    pack_id=pack_id,
                )
            ) from None
        return raw_fn(generator)


def _adapt_get_variants(
    raw_get_variants: object,
    *,
    pack_id: str,
) -> VariantsGetter | None:
    """Wrap a module ``get_variants`` into unified getter shape.

    Args:
        raw_get_variants: Attribute from pack module.
        pack_id: Pack id for diagnostics.

    Returns:
        Adapter or ``None``.
    """
    if not _is_callable_object(raw_get_variants):
        return None

    callback: Callable[..., object] = raw_get_variants

    def wrapper(generator: object | None) -> list[Variant]:
        """Dispatch to pack ``get_variants`` implementation.

        Args:
            generator: Optional task generator instance.

        Returns:
            Normalized list of task variants.
        """
        payload: object = _invoke_get_variants(
            callback,
            generator=generator,
            pack_id=pack_id,
        )
        return _normalize_variants_list(payload)

    return wrapper


def _declarative_get_variants_factory(
    specs: tuple[DeclarativeTaskSpec, ...],
    *,
    input_generator: PackInputGenerator | None,
    payload_generator: PackPayloadGenerator | None,
) -> VariantsGetter:
    """Build getter that serves declarative task specifications.

    Args:
        specs: Parsed declarative rows for one pack.
        input_generator: Optional pack input generator callback.
        payload_generator: Optional full payload override callback.

    Returns:
        Callable compatible with pack descriptor contract.
    """

    def get_variants(_generator: object | None) -> list[Variant]:
        """Build variants from stored declarative specs.

        Args:
            _generator: Unused parameter for shared getter protocol.

        Returns:
            Variants derived from declarative specs.
        """
        return variants_from_specs_with_builders(
            specs=specs,
            input_generator=input_generator,
            payload_generator=payload_generator,
        )

    return get_variants


def _pack_generator_callbacks(
    module: ModuleType | None,
) -> tuple[PackInputGenerator | None, PackPayloadGenerator | None]:
    """Extract optional callbacks from pack ``generator.py`` module.

    Args:
        module: Imported generator module.

    Returns:
        Pair of input generator and payload generator callbacks.
    """
    if module is None:
        return None, None

    input_builder: object = getattr(
        module,
        ATTR_BUILD_INPUT_DINAMIC_POSTFIX_O8XF,
        None,
    )
    payload_builder: object = getattr(
        module,
        ATTR_BUILD_PAYLOAD_DINAMIC_POSTFIX_O8XF,
        None,
    )
    return (
        _adapt_pack_input_generator(input_builder),
        _adapt_pack_payload_generator(payload_builder),
    )


def _declarative_variants_getter(
    *,
    module_dir: Path,
    manifest: ModuleManifest,
    input_generator: PackInputGenerator | None,
    payload_generator: PackPayloadGenerator | None,
) -> tuple[VariantsGetter | None, list[PackDiscoveryIssue]]:
    """Build getter from declarative task files listed in manifest.

    Args:
        module_dir: Pack directory.
        manifest: Validated module manifest.
        input_generator: Optional pack input callback.
        payload_generator: Optional pack payload callback.

    Returns:
        Pair of getter (if any specs resolved) and issues list.
    """
    if not manifest.task_files:
        return None, []

    task_paths: tuple[Path, ...] = tuple(
        module_dir / rel_path for rel_path in manifest.task_files
    )
    specs, task_issues = load_task_specs_with_issues(task_paths)

    issues: list[PackDiscoveryIssue] = []
    if task_issues:
        issues.append(
            _issue(
                module_dir,
                MSG_DECLARATIVE_ISSUES_TEMPLATE_DINAMIC_POSTFIX_O8XF.format(
                    count=len(task_issues),
                ),
            )
        )

    if not specs:
        return None, issues

    return (
        _declarative_get_variants_factory(
            specs,
            input_generator=input_generator,
            payload_generator=payload_generator,
        ),
        issues,
    )


def _fallback_module_getter(
    *,
    module: ModuleType | None,
    pack_id: str,
) -> VariantsGetter | None:
    """Build fallback getter from classic ``module.py`` contract.

    Args:
        module: Imported entry module.
        pack_id: Current pack identifier.

    Returns:
        Adapted getter or ``None``.
    """
    if module is None:
        return None

    raw_getter: object = getattr(
        module,
        ATTR_GET_VARIANTS_DINAMIC_POSTFIX_O8XF,
        None,
    )
    return _adapt_get_variants(raw_getter, pack_id=pack_id)


def _try_pack_descriptor(module_dir: Path) -> DiscoveryResult:
    """Resolve one module directory into descriptor or issues.

    Args:
        module_dir: Candidate directory under content modules root.

    Returns:
        Pair ``(descriptor, issues)``.
    """
    manifest_path: Path = module_dir / MANIFEST_FILE_NAME_DINAMIC_POSTFIX_O8XF
    if not manifest_path.is_file():
        return None, []

    manifest: ModuleManifest | None = load_manifest(manifest_path)
    if manifest is None:
        return None, [
            _issue(module_dir, MSG_INVALID_MANIFEST_DINAMIC_POSTFIX_O8XF)
        ]
    if not manifest.enabled:
        return None, []

    module: ModuleType | None = _load_entry_module(
        module_dir,
        manifest.module_id,
    )
    generator_module: ModuleType | None = _load_pack_generator_module(
        module_dir,
        manifest.module_id,
    )
    input_generator, payload_generator = _pack_generator_callbacks(
        generator_module,
    )

    getter, issues = _declarative_variants_getter(
        module_dir=module_dir,
        manifest=manifest,
        input_generator=input_generator,
        payload_generator=payload_generator,
    )
    if getter is None:
        getter = _fallback_module_getter(
            module=module,
            pack_id=manifest.module_id,
        )

    if getter is None:
        issues.append(
            _issue(module_dir, MSG_NO_VARIANT_SOURCE_DINAMIC_POSTFIX_O8XF)
        )
        return None, issues

    descriptor = PackDescriptor(
        pack_id=manifest.module_id,
        label=manifest.label,
        get_variants=getter,
    )
    return descriptor, issues


def _discover_regular_packs_with_issues() -> tuple[
    dict[str, PackDescriptor],
    tuple[PackDiscoveryIssue, ...],
]:
    """Scan content modules directory for pack descriptors.

    Returns:
        Mapping of pack id to descriptor and tuple of issues.
    """
    root: Path = _content_modules_root()
    if not root.is_dir():
        return {}, ()

    descriptors: dict[str, PackDescriptor] = {}
    issues: list[PackDiscoveryIssue] = []

    module_dirs: list[Path] = sorted(
        path for path in root.iterdir() if path.is_dir()
    )
    for module_dir in module_dirs:
        if module_dir.name in IGNORED_DIRECTORY_NAMES:
            continue

        descriptor, batch = _try_pack_descriptor(module_dir)
        issues.extend(batch)
        if descriptor is not None:
            descriptors[descriptor.pack_id] = descriptor

    return descriptors, tuple(issues)


def _mixed_descriptor(
    regular_packs: dict[str, PackDescriptor],
) -> PackDescriptor | None:
    """Build virtual pack that merges all regular packs.

    Args:
        regular_packs: Non-mixed descriptors keyed by pack id.

    Returns:
        Descriptor for mixed pack, or ``None``.
    """
    ordered_pack_ids: tuple[str, ...] = tuple(regular_packs)
    if not ordered_pack_ids:
        return None

    def mixed_get_variants(generator: object | None) -> list[Variant]:
        """Concatenate variants from regular packs.

        Args:
            generator: Optional task generator instance.

        Returns:
            Combined variant list in stable pack order.
        """
        combined: list[Variant] = []
        for pack_id in ordered_pack_ids:
            descriptor: PackDescriptor = regular_packs[pack_id]
            combined.extend(descriptor.get_variants(generator))
        return combined

    return PackDescriptor(
        pack_id=MIXED_PACK_ID_DINAMIC_POSTFIX_O8XF,
        label=MIXED_PACK_LABEL_DINAMIC_POSTFIX_O8XF,
        get_variants=mixed_get_variants,
    )


@lru_cache(maxsize=DISCOVERY_CACHE_SIZE)
def discover_pack_descriptors() -> dict[str, PackDescriptor]:
    """Load and cache all pack descriptors including mixed.

    Returns:
        Mutable mapping of pack id to descriptor.
    """
    regular, _issues = _discover_regular_packs_with_issues()
    mixed: PackDescriptor | None = _mixed_descriptor(regular)
    if mixed is not None:
        regular[mixed.pack_id] = mixed
    return regular


def refresh_pack_descriptors() -> None:
    """Clear cached descriptors after code or data reload."""
    discover_pack_descriptors.cache_clear()


def list_discovery_issues() -> tuple[PackDiscoveryIssue, ...]:
    """Run discovery and return diagnostic issues only.

    Returns:
        Tuple of issues for modules with validation problems.
    """
    _, issues = _discover_regular_packs_with_issues()
    return issues


def list_available_packs() -> tuple[str, ...]:
    """List regular pack identifiers excluding mixed.

    Returns:
        Stable tuple of regular pack identifiers.
    """
    descriptors: dict[str, PackDescriptor] = discover_pack_descriptors()
    return tuple(
        pack_id
        for pack_id in descriptors
        if pack_id != MIXED_PACK_ID_DINAMIC_POSTFIX_O8XF
    )


def list_available_pack_labels() -> tuple[PackLabel, ...]:
    """List id/label pairs for UI selectors.

    Returns:
        One label entry per non-mixed pack.
    """
    descriptors: dict[str, PackDescriptor] = discover_pack_descriptors()
    return tuple(
        PackLabel(pack_id=pack_id, label=descriptor.label)
        for pack_id, descriptor in descriptors.items()
        if pack_id != MIXED_PACK_ID_DINAMIC_POSTFIX_O8XF
    )


def pack_label_by_id(pack_id: str) -> str:
    """Resolve pack label with fallback to raw id.

    Args:
        pack_id: Pack identifier to resolve.

    Returns:
        Descriptor label when known, otherwise input id.
    """
    descriptor: PackDescriptor | None = discover_pack_descriptors().get(
        pack_id
    )
    return descriptor.label if descriptor is not None else pack_id


def get_variants_for_pack(
    pack_id: str,
    *,
    generator: object | None,
) -> list[Variant]:
    """Return task variants for one pack.

    Args:
        pack_id: Target pack id.
        generator: Optional generator passed to pack getter.

    Returns:
        Variant list from pack descriptor.

    Raises:
        ValueError: If pack id is unknown.
    """
    descriptor: PackDescriptor | None = discover_pack_descriptors().get(
        pack_id
    )
    if descriptor is None:
        raise ValueError(
            ERR_UNSUPPORTED_PACK_DINAMIC_POSTFIX_O8XF.format(
                pack_id=pack_id,
            )
        )
    return descriptor.get_variants(generator)
