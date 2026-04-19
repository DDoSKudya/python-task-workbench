"""Tests for :mod:`app` entrypoint routing."""

from __future__ import annotations

from typing import Final
from unittest.mock import MagicMock, patch

import app as app_module
from messages import CLI_COMMAND_DINAMIC_POSTFIX_P8SU

_EXIT_SUCCESS: Final[int] = 0
_PROG_NAME: Final[str] = "prog"


def test_main_invokes_cli_when_second_token_is_cli() -> None:
    """Dispatch to CLI when the second argv token is the CLI keyword.

    Returns:
        None.
    """
    called: list[object] = []

    def _fake_cli() -> None:
        called.append(True)

    with patch("core.paths.ensure_data_directories", lambda: None):
        with patch("generator.cli.entry.cli_main", _fake_cli):
            code = app_module.main(
                [_PROG_NAME, CLI_COMMAND_DINAMIC_POSTFIX_P8SU],
            )
    assert code == _EXIT_SUCCESS
    assert called == [True]


def test_main_invokes_gui_when_not_cli_mode() -> None:
    """Dispatch to GUI when argv does not request CLI mode.

    Returns:
        None.
    """
    mock_gui = MagicMock(return_value=_EXIT_SUCCESS)
    with patch("core.paths.ensure_data_directories", lambda: None):
        with patch.object(app_module, "_run_gui", mock_gui):
            code = app_module.main([_PROG_NAME])
    assert code == _EXIT_SUCCESS
    mock_gui.assert_called_once()
