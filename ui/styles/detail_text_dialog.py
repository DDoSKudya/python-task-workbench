"""
This module generates the QSS stylesheet fragment used to style a
“detail text” dialog, including its shell, header, footer, and body
areas.

It works by collecting selector names, colors, font sizes, padding, and
border metrics from a message catalog, packaging them into a token
dictionary, and interpolating them into a QSS template string.

It contains a _DetailTextDialogStyleTokens TypedDict that describes all
placeholders expected by the DETAIL_TEXT_DIALOG_STYLE_TEMPLATE_…, a
_detail_text_dialog_style_tokens helper that returns a populated token
mapping, and the public detail_text_dialog_styles function that formats
and returns the final QSS section.

Within the broader system, this module feeds its stylesheet fragment
into the overall app stylesheet builder so that the detail text
dialogs appearance and typography can be centrally configured and
themed.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    BORDER_WIDTH_PX_DINAMIC_POSTFIX_VAGN,
    CODE_BODY_FONT_SIZE_PX_DINAMIC_POSTFIX_VAGN,
    COLOR_CODE_BODY_BACKGROUND_DINAMIC_POSTFIX_VAGN,
    COLOR_FOOTER_BORDER_DINAMIC_POSTFIX_VAGN,
    COLOR_HEADER_BACKGROUND_DINAMIC_POSTFIX_VAGN,
    COLOR_HEADER_BORDER_DINAMIC_POSTFIX_VAGN,
    COLOR_SELECTION_BACKGROUND_DINAMIC_POSTFIX_VAGN,
    COLOR_TEXT_BODY_BACKGROUND_DINAMIC_POSTFIX_VAGN,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_VAGN,
    COLOR_WHITE_DINAMIC_POSTFIX_VAGN,
    DETAIL_DIALOG_SELECTOR_DINAMIC_POSTFIX_VAGN,
    DETAIL_FOOT_BAR_SELECTOR_DINAMIC_POSTFIX_VAGN,
    DETAIL_TEXT_BODY_CODE_SELECTOR_DINAMIC_POSTFIX_VAGN,
    DETAIL_TEXT_BODY_SELECTOR_DINAMIC_POSTFIX_VAGN,
    DETAIL_TEXT_DIALOG_STYLE_TEMPLATE_DINAMIC_POSTFIX_VAGN,
    DIALOG_HEADER_SELECTOR_DINAMIC_POSTFIX_VAGN,
    DIALOG_TITLE_SELECTOR_DINAMIC_POSTFIX_VAGN,
    MONOSPACE_FONT_FAMILY_DINAMIC_POSTFIX_VAGN,
    TEXT_BODY_FONT_SIZE_PX_DINAMIC_POSTFIX_VAGN,
    TEXT_BODY_PADDING_DINAMIC_POSTFIX_VAGN,
    TEXT_BODY_RADIUS_PX_DINAMIC_POSTFIX_VAGN,
)


class _DetailTextDialogStyleTokens(TypedDict):
    """
    Fields consumed by :data:`DETAIL_TEXT_DIALOG_STYLE_TEMPLATE_…`.
    """

    detail_dialog_selector: str
    dialog_header_selector: str
    dialog_title_selector: str
    detail_foot_bar_selector: str
    detail_text_body_selector: str
    detail_text_body_code_selector: str
    color_white: str
    color_text_primary: str
    color_header_background: str
    color_header_border: str
    color_footer_border: str
    color_text_body_background: str
    color_code_body_background: str
    color_selection_background: str
    monospace_font_family: str
    border_width_px: str
    text_body_radius_px: str
    text_body_padding: str
    text_body_font_size_px: str
    code_body_font_size_px: str


def _detail_text_dialog_style_tokens() -> _DetailTextDialogStyleTokens:
    """Map catalog strings to the detail-dialog QSS template
    placeholders.

    Returns:
        Keyword bundle for
        ``DETAIL_TEXT_DIALOG_STYLE_TEMPLATE_DINAMIC_POSTFIX_VAGN``.
    """
    return _DetailTextDialogStyleTokens(
        detail_dialog_selector=DETAIL_DIALOG_SELECTOR_DINAMIC_POSTFIX_VAGN,
        dialog_header_selector=DIALOG_HEADER_SELECTOR_DINAMIC_POSTFIX_VAGN,
        dialog_title_selector=DIALOG_TITLE_SELECTOR_DINAMIC_POSTFIX_VAGN,
        detail_foot_bar_selector=DETAIL_FOOT_BAR_SELECTOR_DINAMIC_POSTFIX_VAGN,
        detail_text_body_selector=(
            DETAIL_TEXT_BODY_SELECTOR_DINAMIC_POSTFIX_VAGN
        ),
        detail_text_body_code_selector=(
            DETAIL_TEXT_BODY_CODE_SELECTOR_DINAMIC_POSTFIX_VAGN
        ),
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_VAGN,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_VAGN,
        color_header_background=(COLOR_HEADER_BACKGROUND_DINAMIC_POSTFIX_VAGN),
        color_header_border=COLOR_HEADER_BORDER_DINAMIC_POSTFIX_VAGN,
        color_footer_border=COLOR_FOOTER_BORDER_DINAMIC_POSTFIX_VAGN,
        color_text_body_background=(
            COLOR_TEXT_BODY_BACKGROUND_DINAMIC_POSTFIX_VAGN
        ),
        color_code_body_background=(
            COLOR_CODE_BODY_BACKGROUND_DINAMIC_POSTFIX_VAGN
        ),
        color_selection_background=(
            COLOR_SELECTION_BACKGROUND_DINAMIC_POSTFIX_VAGN
        ),
        monospace_font_family=MONOSPACE_FONT_FAMILY_DINAMIC_POSTFIX_VAGN,
        border_width_px=BORDER_WIDTH_PX_DINAMIC_POSTFIX_VAGN,
        text_body_radius_px=TEXT_BODY_RADIUS_PX_DINAMIC_POSTFIX_VAGN,
        text_body_padding=TEXT_BODY_PADDING_DINAMIC_POSTFIX_VAGN,
        text_body_font_size_px=TEXT_BODY_FONT_SIZE_PX_DINAMIC_POSTFIX_VAGN,
        code_body_font_size_px=CODE_BODY_FONT_SIZE_PX_DINAMIC_POSTFIX_VAGN,
    )


def detail_text_dialog_styles() -> str:
    """Emit the QSS section for the detail text dialog chrome and panes.

    Returns:
        One stylesheet fragment: shell, header, footer, body, and code
        body.
    """
    return DETAIL_TEXT_DIALOG_STYLE_TEMPLATE_DINAMIC_POSTFIX_VAGN.format(
        **_detail_text_dialog_style_tokens()
    )
