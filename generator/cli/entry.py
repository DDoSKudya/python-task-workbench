"""
This module implements the main entry point for a CLI that runs in one
of several modes based on application configuration.

It works by rejecting any external argv content, resolving an AppConfig
via resolve_config, and dispatching to the appropriate mode handler.

It defines helper functions _ensure_argv_is_supported to enforce that no
command-line arguments are accepted and _run_mode to route execution to
run_solve_mode or run_check_mode with an optional coach flag.

The cli_main function is the public entry, performing validation,
loading the config, and delegating to _run_mode, making this module the
bridge between process startup and the rest of the CLI implementation.
"""

from __future__ import annotations

from generator.app_config import AppConfig
from messages import (
    INVALID_MODE_ERROR_DINAMIC_POSTFIX_FT6H,
    MODE_CHECK_DINAMIC_POSTFIX_FT6H,
    MODE_COACH_DINAMIC_POSTFIX_FT6H,
    MODE_SOLVE_DINAMIC_POSTFIX_FT6H,
    UNSUPPORTED_ARGV_ERROR_DINAMIC_POSTFIX_FT6H,
)

from .modes import run_check_mode, run_solve_mode
from .resolve import resolve_config


def _ensure_argv_is_supported(argv: list[str] | None) -> None:
    """Validate ``argv`` compatibility for this CLI entrypoint.

    Args:
        argv: Optional external argv value.

    Raises:
        ValueError: If a non-empty argv list is provided.
    """
    if argv:
        raise ValueError(UNSUPPORTED_ARGV_ERROR_DINAMIC_POSTFIX_FT6H)


def _run_mode(config: AppConfig) -> None:
    """Dispatch execution to the selected CLI mode.

    Args:
        config: Resolved application configuration.

    Raises:
        ValueError: If the configured mode is not supported.
    """
    if config.mode == MODE_SOLVE_DINAMIC_POSTFIX_FT6H:
        run_solve_mode(config)
    elif config.mode == MODE_CHECK_DINAMIC_POSTFIX_FT6H:
        run_check_mode(config, coach_mode=False)
    elif config.mode == MODE_COACH_DINAMIC_POSTFIX_FT6H:
        run_check_mode(config, coach_mode=True)
    else:
        raise ValueError(INVALID_MODE_ERROR_DINAMIC_POSTFIX_FT6H)


def cli_main(argv: list[str] | None = None) -> None:
    """Run the CLI based on the resolved configuration.

    Args:
        argv: Optional argv value. Passing a non-empty list is not
        supported.

    Raises:
        ValueError: If argv is provided or the config mode is
        unsupported.
    """
    _ensure_argv_is_supported(argv)
    config = resolve_config()
    _run_mode(config)
