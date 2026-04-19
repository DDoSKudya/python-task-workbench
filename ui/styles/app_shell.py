"""Build base QSS styles for the application shell."""

from __future__ import annotations

from messages import (
    APP_BACKGROUND_COLOR_DINAMIC_POSTFIX_UVDS,
    APP_FONT_FAMILY_DINAMIC_POSTFIX_UVDS,
    APP_FONT_SIZE_PT_DINAMIC_POSTFIX_UVDS,
    APP_ROOT_SELECTOR_DINAMIC_POSTFIX_UVDS,
    APP_SHELL_STYLE_TEMPLATE_DINAMIC_POSTFIX_UVDS,
    APP_TEXT_COLOR_DINAMIC_POSTFIX_UVDS,
    MAIN_WINDOW_SELECTOR_DINAMIC_POSTFIX_UVDS,
)


def app_shell_styles() -> str:
    """Return QSS styles for base shell widgets.

    Returns:
        Formatted QSS block for app root and main window widgets.
    """
    return APP_SHELL_STYLE_TEMPLATE_DINAMIC_POSTFIX_UVDS.format(
        app_root_selector=APP_ROOT_SELECTOR_DINAMIC_POSTFIX_UVDS,
        background_color=APP_BACKGROUND_COLOR_DINAMIC_POSTFIX_UVDS,
        text_color=APP_TEXT_COLOR_DINAMIC_POSTFIX_UVDS,
        font_family=APP_FONT_FAMILY_DINAMIC_POSTFIX_UVDS,
        font_size_pt=APP_FONT_SIZE_PT_DINAMIC_POSTFIX_UVDS,
        main_window_selector=MAIN_WINDOW_SELECTOR_DINAMIC_POSTFIX_UVDS,
    )
