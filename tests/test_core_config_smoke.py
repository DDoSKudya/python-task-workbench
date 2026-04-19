"""Smoke tests for :mod:`core.config`."""

from __future__ import annotations

from typing import Final

from core.config import AppDefaults, load_defaults

_MIN_SESSION_COUNT: Final[int] = 1
_SPLITTER_PARTS: Final[int] = 4


def test_load_defaults_returns_structured_defaults() -> None:
    """Load defaults and assert shape and allowed enum-like fields.

    Returns:
        None.
    """
    defaults = load_defaults()
    assert isinstance(defaults, AppDefaults)
    assert defaults.session.count >= _MIN_SESSION_COUNT
    assert defaults.session.checker_entry_mode in (
        "strict",
        "hybrid",
    )
    assert defaults.ui.ui_language in ("en", "ru")
    assert len(defaults.ui.splitter_sizes) == _SPLITTER_PARTS
