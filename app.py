"""
This module is the main entrypoint for the application, deciding whether
to run a command-line tool or launch the PyQt GUI based on the
command-line arguments.

It works by inspecting argv for a specific CLI command token, ensuring
data  directories exist, and either dispatching to
generator.cli.entry.cli_main or constructing and running a QApplication
with the main window.

It defines constants for argument positions and exit codes, a main
function that orchestrates mode selection, a helper _is_cli_mode that
checks the first user argument against a catalog keyword, and _run_gui
which sets locale, loads defaults, applies the Fusion style and app-wide
stylesheet, and centers the main window on the primary screen via
_center_window_on_primary_screen.

Within the broader system, this module provides the unified startup path
so the same executable can be used both as a non-interactive generator
CLI and as a fully styled Qt desktop application, returning an
appropriate process exit status when run as a script.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence

from typing import TYPE_CHECKING, Final, cast

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QApplication, QMainWindow

from messages import (
    CLI_COMMAND_DINAMIC_POSTFIX_P8SU,
    FUSION_STYLE_NAME_DINAMIC_POSTFIX_P8SU,
)

MODE_ARGUMENT_INDEX: Final[int] = 1
MIN_ARGUMENT_COUNT_FOR_MODE: Final[int] = 2
EXIT_SUCCESS: Final[int] = 0


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch to the CLI entrypoint or the Qt GUI event loop.

    Args:
        argv: Command-line tokens. Defaults to ``sys.argv`` when
        omitted.

    Returns:
        Process exit status (``0`` after a normal CLI run; GUI uses Qt).
    """
    from core.paths import ensure_data_directories

    arguments: Sequence[str] = argv if argv is not None else sys.argv
    ensure_data_directories()
    if _is_cli_mode(arguments):
        from generator.cli.entry import cli_main

        cli_main()
        return EXIT_SUCCESS
    return _run_gui(arguments)


def _is_cli_mode(arguments: Sequence[str]) -> bool:
    """Return whether ``arguments`` select the non-interactive CLI.

    Args:
        arguments: Raw ``argv`` sequence (program name at index ``0``).

    Returns:
        ``True`` when the first user token equals the catalog CLI
        keyword.
    """
    return (
        len(arguments) >= MIN_ARGUMENT_COUNT_FOR_MODE
        and arguments[MODE_ARGUMENT_INDEX] == CLI_COMMAND_DINAMIC_POSTFIX_P8SU
    )


def _center_window_on_primary_screen(
    *,
    app: QApplication,
    window: QMainWindow,
) -> None:
    """Center ``window`` on the primary screen, if one exists.

    Args:
        app: Active Qt application (provides screen geometry).
        window: Top-level window to reposition.
    """
    screen = app.primaryScreen()
    if screen is None:
        return
    center_pt = screen.availableGeometry().center()
    frame = window.frameGeometry()
    frame.moveCenter(center_pt)
    window.move(frame.topLeft())


def _run_gui(arguments: Sequence[str]) -> int:
    """Build defaults, locale, stylesheet, main window, and run the
    loop.

    Locale must be applied before importing UI modules: code that does
    ``from messages import …`` binds translated strings at import time.

    Args:
        arguments: Arguments forwarded to ``QApplication`` (includes
            ``argv[0]``).

    Returns:
        Integer status from ``QApplication.exec()``.
    """
    from core.config import AppDefaults, load_defaults
    from messages.translate import set_locale

    defaults: AppDefaults = load_defaults()
    set_locale(defaults.ui.ui_language)

    from PyQt6.QtWidgets import QApplication

    from ui.main_window import MainWindow
    from ui.styles import app_stylesheet

    app = QApplication(list(arguments))
    app.setStyle(FUSION_STYLE_NAME_DINAMIC_POSTFIX_P8SU)
    app.setStyleSheet(app_stylesheet())
    main_window_ctor = cast(
        Callable[[AppDefaults], MainWindow],
        MainWindow,
    )
    window = main_window_ctor(defaults)
    window.show()
    _center_window_on_primary_screen(app=app, window=window)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
