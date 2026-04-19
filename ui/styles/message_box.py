"""
This module generates the QSS stylesheet fragment used to style standard
message dialogs in the application.

It works by collecting selector names, colors, and a minimum label width
from a message catalog, packaging them into a token dictionary, and
interpolating them into a message-box QSS template string.

It contains a _MessageBoxStyleTokens TypedDict describing the templates
placeholders, a _message_box_style_tokens helper that returns a
populated mapping of catalog values, and the public message_box_styles
function that formats and returns the final stylesheet text.

Within the broader system, this fragment is combined with other QSS
sections to ensure that all message boxes share consistent colors,
layout, and label sizing aligned with the apps theme.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_BQVU,
    COLOR_WHITE_DINAMIC_POSTFIX_BQVU,
    MESSAGE_BOX_LABEL_MIN_WIDTH_PX_DINAMIC_POSTFIX_BQVU,
    MESSAGE_BOX_LABEL_SELECTOR_DINAMIC_POSTFIX_BQVU,
    MESSAGE_BOX_SELECTOR_DINAMIC_POSTFIX_BQVU,
    MESSAGE_BOX_STYLE_TEMPLATE_DINAMIC_POSTFIX_BQVU,
)


class _MessageBoxStyleTokens(TypedDict):
    """Keyword fields for :data:`MESSAGE_BOX_STYLE_TEMPLATE_…`."""

    message_box_selector: str
    message_box_label_selector: str
    color_white: str
    color_text_primary: str
    message_box_label_min_width_px: str


def _message_box_style_tokens() -> _MessageBoxStyleTokens:
    """Collect catalog values for the message-box QSS template.

    Returns:
        Keyword bundle for
        ``MESSAGE_BOX_STYLE_TEMPLATE_DINAMIC_POSTFIX_BQVU``.
    """
    return _MessageBoxStyleTokens(
        message_box_selector=MESSAGE_BOX_SELECTOR_DINAMIC_POSTFIX_BQVU,
        message_box_label_selector=(
            MESSAGE_BOX_LABEL_SELECTOR_DINAMIC_POSTFIX_BQVU
        ),
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_BQVU,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_BQVU,
        message_box_label_min_width_px=(
            MESSAGE_BOX_LABEL_MIN_WIDTH_PX_DINAMIC_POSTFIX_BQVU
        ),
    )


def message_box_styles() -> str:
    """Render the QSS fragment applied to standard message dialogs.

    Returns:
        Stylesheet text for the dialog surface and primary label column.
    """
    return MESSAGE_BOX_STYLE_TEMPLATE_DINAMIC_POSTFIX_BQVU.format(
        **_message_box_style_tokens()
    )
