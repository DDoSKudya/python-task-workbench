"""
This module acts as the public façade of the core package, re-exporting
key models, configuration types, and helper functions to consumers.
"""

from __future__ import annotations

from collections.abc import Callable

from typing import TYPE_CHECKING, Final, Literal, overload

from .config import AVAILABLE_PACKS, AppDefaults, UiDefaults, load_defaults
from .models import (
    CheckResult,
    SessionConfig,
    Task,
    TaskSession,
    TaskState,
    TaskViewModel,
    all_task_view_models,
    task_view_model,
)

__all__: Final[tuple[str, ...]] = (
    "AVAILABLE_PACKS",
    "AppDefaults",
    "CheckResult",
    "SessionConfig",
    "Task",
    "TaskSession",
    "TaskState",
    "TaskViewModel",
    "UiDefaults",
    "all_task_view_models",
    "build_session",
    "load_defaults",
    "task_view_model",
)

if TYPE_CHECKING:
    from .session import build_session

_ATTR_BUILD_SESSION: Final[str] = "build_session"
_ERR_MODULE_NO_ATTR: Final[str] = (
    "module {module_name!r} has no attribute {attr_name!r}"
)


@overload
def __getattr__(
    name: Literal["build_session"],
) -> Callable[[SessionConfig], TaskSession]: ...


@overload
def __getattr__(name: str) -> object: ...


def __getattr__(name: str) -> object:
    """Return a lazily exported package attribute.

    Resolving ``build_session`` loads ``core.session`` only on first
    use, so heavy dependencies (e.g. ``generator``) stay unloaded until
    needed.

    Args:
        name: Attribute name requested on this package.

    Returns:
        The requested export object.

    Raises:
        AttributeError: If ``name`` is not a supported lazy export.
    """
    if name == _ATTR_BUILD_SESSION:
        from .session import build_session

        return build_session
    raise AttributeError(
        _ERR_MODULE_NO_ATTR.format(module_name=__name__, attr_name=name)
    )
