"""Shared pytest fixtures for Python Task Workbench."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from messages.translate import set_locale


@pytest.fixture(autouse=True)
def _reset_locale_after_test() -> (  # pyright: ignore[reportUnusedFunction]
    Iterator[None]
):
    """Reset locale to English after each test.

    Yields:
        Control to the test body, then restore ``en`` locale.
    """
    yield
    set_locale("en")
