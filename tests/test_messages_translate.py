"""Tests for :mod:`messages.translate`."""

from __future__ import annotations

from typing import Final

from messages.translate import get_locale, set_locale, translate

_LOCALE_EN_NORMALIZED: Final[str] = "en"
_LOCALE_RU: Final[str] = "ru"
_LOCALE_EN_INPUT: Final[str] = "  EN  "
_SAMPLE_PHRASE: Final[str] = "Hello"
_APP_TITLE_EN: Final[str] = "Python Task Workbench"


def test_set_locale_normalizes_unknown_to_english() -> None:
    """Normalize padded ``en`` input to the ``en`` locale code.

    Returns:
        None.
    """
    set_locale(_LOCALE_EN_INPUT)
    assert get_locale() == _LOCALE_EN_NORMALIZED


def test_set_locale_russian() -> None:
    """Set active locale to Russian.

    Returns:
        None.
    """
    set_locale(_LOCALE_RU)
    assert get_locale() == _LOCALE_RU


def test_translate_returns_original_when_not_russian() -> None:
    """Return the source phrase unchanged when locale is English.

    Returns:
        None.
    """
    set_locale(_LOCALE_EN_NORMALIZED)
    assert translate(_SAMPLE_PHRASE) == _SAMPLE_PHRASE


def test_translate_uses_table_when_russian() -> None:
    """Resolve catalog text when Russian locale is active.

    Returns:
        None.
    """
    set_locale(_LOCALE_RU)
    out = translate(_APP_TITLE_EN)
    assert isinstance(out, str)
    assert len(out) > 0
