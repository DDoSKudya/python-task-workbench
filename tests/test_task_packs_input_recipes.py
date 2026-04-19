"""Tests for :mod:`task_packs.input_recipes`."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Final

import pytest

from generator.fake_data import FakeDataFactory
from messages import RECIPE_SUM_NUMS_DINAMIC_POSTFIX_KZLL
from task_packs.input_recipes import INPUT_RECIPES, run_input_recipe

_UNKNOWN_RECIPE: Final[str] = "no_such_recipe_xyz"


def test_run_input_recipe_rejects_non_factory() -> None:
    """First argument must be a :class:`FakeDataFactory`.

    Returns:
        None.
    """
    spec = SimpleNamespace(input_recipe=RECIPE_SUM_NUMS_DINAMIC_POSTFIX_KZLL)
    with pytest.raises(TypeError):
        run_input_recipe(object(), spec)  # type: ignore[arg-type]


def test_run_input_recipe_unknown_recipe() -> None:
    """Unknown recipe names raise :exc:`KeyError`.

    Returns:
        None.
    """
    factory = FakeDataFactory(seed=1)
    spec = SimpleNamespace(input_recipe=_UNKNOWN_RECIPE)
    with pytest.raises(KeyError):
        run_input_recipe(factory, spec)  # type: ignore[arg-type]


def test_input_recipes_registry_has_core_recipes() -> None:
    """Built-in sum recipe is registered.

    Returns:
        None.
    """
    assert RECIPE_SUM_NUMS_DINAMIC_POSTFIX_KZLL in INPUT_RECIPES
