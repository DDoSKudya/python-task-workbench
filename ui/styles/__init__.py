"""
This module builds the complete Qt stylesheet (QSS) for the application
by aggregating style snippets from multiple UI areas into one string.

It works by defining a fixed-order tuple of style-builder callables,
each returning a QSS fragment, and joining their outputs with a
catalog-provided separator to form a single stylesheet suitable for
QApplication.setStyleSheet.

It contains the StyleBuilder type alias, the STYLE_SECTION_BUILDERS
constant listing section-specific functions like app_shell_styles,
header_styles, task_aside_styles, and others, and the public
app_stylesheet function that performs the concatenation.

Within the broader system, this module acts as the central styling entry
point, ensuring that all parts of the UI share a consistent, composable
stylesheet that can be regenerated or localized via the underlying
message catalog.
"""

from __future__ import annotations

from collections.abc import Callable

from typing import Final

from messages import EMPTY_STYLESHEET_DINAMIC_POSTFIX_0GY0

from .app_shell import app_shell_styles
from .center_editor import center_editor_styles
from .detail_text_dialog import detail_text_dialog_styles
from .forms_common import forms_common_styles
from .header import header_styles
from .history_dialog import history_dialog_styles
from .message_box import message_box_styles
from .right_panel import right_panel_styles
from .session_start_dialog import session_start_dialog_styles
from .session_summary import session_summary_styles
from .task_aside import task_aside_styles

type StyleBuilder = Callable[[], str]

STYLE_SECTION_BUILDERS: Final[tuple[StyleBuilder, ...]] = (
    app_shell_styles,
    header_styles,
    task_aside_styles,
    center_editor_styles,
    right_panel_styles,
    forms_common_styles,
    history_dialog_styles,
    session_summary_styles,
    detail_text_dialog_styles,
    session_start_dialog_styles,
    message_box_styles,
)


def app_stylesheet() -> str:
    """Concatenate every registered QSS section into one string.

    Sections run in fixed registration order. The catalog join token is
    empty, so blocks abut with no delimiter between them.

    Returns:
        Full application stylesheet for ``QApplication.setStyleSheet``.
    """
    return EMPTY_STYLESHEET_DINAMIC_POSTFIX_0GY0.join(
        builder() for builder in STYLE_SECTION_BUILDERS
    )


__all__ = ("app_stylesheet",)
