"""
This module generates the QSS stylesheet fragment used to style the
“start session” dialog, including its header, pack list, parameter
fields, and footer.

It works by defining a _SessionStartDialogStyleTokens TypedDict of all
placeholders required by a QSS template, filling that mapping with
selector names, colors, sizes, paddings, and border settings from a
message catalog, and interpolating them into
SESSION_START_DIALOG_TEMPLATE_….

It contains the token type, the _session_start_dialog_style_tokens
helper that assembles a complete dictionary of style tokens, and the
public session_start_dialog_styles function that formats and returns the
final stylesheet fragment.

Within the broader system, this fragment is combined with other QSS
sections so that the session-start modal has a consistent, themeable
appearance aligned with the applications overall look and feel.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    BORDER_NONE_DINAMIC_POSTFIX_GFL1,
    BORDER_WIDTH_1_PX_DINAMIC_POSTFIX_GFL1,
    COLOR_ACCENT_DINAMIC_POSTFIX_GFL1,
    COLOR_BORDER_SOFT_DINAMIC_POSTFIX_GFL1,
    COLOR_DISABLED_SURFACE_DINAMIC_POSTFIX_GFL1,
    COLOR_DISABLED_TEXT_DINAMIC_POSTFIX_GFL1,
    COLOR_HEADER_BACKGROUND_DINAMIC_POSTFIX_GFL1,
    COLOR_HEADER_BORDER_DINAMIC_POSTFIX_GFL1,
    COLOR_HOVER_BORDER_DINAMIC_POSTFIX_GFL1,
    COLOR_HOVER_SURFACE_DINAMIC_POSTFIX_GFL1,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_GFL1,
    COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_GFL1,
    COLOR_WHITE_DINAMIC_POSTFIX_GFL1,
    FONT_SIZE_11_PX_DINAMIC_POSTFIX_GFL1,
    FONT_SIZE_13_PX_DINAMIC_POSTFIX_GFL1,
    NEGATIVE_4_PX_DINAMIC_POSTFIX_GFL1,
    OUTLINE_NONE_DINAMIC_POSTFIX_GFL1,
    PACK_ITEM_MARGIN_DINAMIC_POSTFIX_GFL1,
    PACK_ITEM_PADDING_DINAMIC_POSTFIX_GFL1,
    PACK_SELECT_PADDING_DINAMIC_POSTFIX_GFL1,
    SESSION_START_BODY_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_DIALOG_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_DIALOG_TEMPLATE_DINAMIC_POSTFIX_GFL1,
    SESSION_START_FOOT_BAR_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_HEADER_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_HINT_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_LABEL_DISABLED_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_PACK_ITEM_HOVER_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_PACK_ITEM_SELECTED_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_PACK_ITEM_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_PACK_SELECT_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_PARAM_FIELDS_DISABLED_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_PARAM_FIELDS_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_SCROLL_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_SCROLL_VIEWPORT_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_SETTINGS_LABEL_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_SUMMARY_OK_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SESSION_START_TITLE_SELECTOR_DINAMIC_POSTFIX_GFL1,
    SIZE_2_PX_DINAMIC_POSTFIX_GFL1,
    SIZE_4_PX_DINAMIC_POSTFIX_GFL1,
    SIZE_6_PX_DINAMIC_POSTFIX_GFL1,
    SIZE_8_PX_DINAMIC_POSTFIX_GFL1,
    SIZE_10_PX_DINAMIC_POSTFIX_GFL1,
    SIZE_11_PX_DINAMIC_POSTFIX_GFL1,
    SIZE_44_PX_DINAMIC_POSTFIX_GFL1,
    SIZE_220_PX_DINAMIC_POSTFIX_GFL1,
)


class _SessionStartDialogStyleTokens(TypedDict):
    """Keyword fields for :data:`SESSION_START_DIALOG_TEMPLATE_…`."""

    session_start_dialog_selector: str
    session_start_header_selector: str
    session_start_title_selector: str
    session_start_scroll_selector: str
    session_start_scroll_viewport_selector: str
    session_start_body_selector: str
    session_start_settings_label_selector: str
    session_start_hint_selector: str
    session_start_param_fields_selector: str
    session_start_pack_select_selector: str
    session_start_pack_item_selector: str
    session_start_pack_item_selected_selector: str
    session_start_pack_item_hover_selector: str
    session_start_param_fields_disabled_selector: str
    session_start_label_disabled_selector: str
    session_start_foot_bar_selector: str
    session_start_summary_ok_selector: str
    color_white: str
    color_text_primary: str
    color_text_secondary: str
    color_border_soft: str
    color_header_background: str
    color_header_border: str
    color_accent: str
    color_hover_surface: str
    color_hover_border: str
    color_disabled_surface: str
    color_disabled_text: str
    border_none: str
    outline_none: str
    border_width_1_px: str
    font_size_13_px: str
    font_size_11_px: str
    size_220_px: str
    size_44_px: str
    size_11_px: str
    size_10_px: str
    size_8_px: str
    size_6_px: str
    size_4_px: str
    size_2_px: str
    negative_4_px: str
    pack_select_padding: str
    pack_item_padding: str
    pack_item_margin: str


def _session_start_dialog_style_tokens() -> _SessionStartDialogStyleTokens:
    """Assemble catalog strings for the session-start QSS template.

    Returns:
        Keyword bundle for
        ``SESSION_START_DIALOG_TEMPLATE_DINAMIC_POSTFIX_GFL1``.
    """
    return _SessionStartDialogStyleTokens(
        session_start_dialog_selector=(
            SESSION_START_DIALOG_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_header_selector=(
            SESSION_START_HEADER_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_title_selector=(
            SESSION_START_TITLE_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_scroll_selector=(
            SESSION_START_SCROLL_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_scroll_viewport_selector=(
            SESSION_START_SCROLL_VIEWPORT_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_body_selector=(
            SESSION_START_BODY_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_settings_label_selector=(
            SESSION_START_SETTINGS_LABEL_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_hint_selector=(
            SESSION_START_HINT_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_param_fields_selector=(
            SESSION_START_PARAM_FIELDS_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_pack_select_selector=(
            SESSION_START_PACK_SELECT_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_pack_item_selector=(
            SESSION_START_PACK_ITEM_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_pack_item_selected_selector=(
            SESSION_START_PACK_ITEM_SELECTED_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_pack_item_hover_selector=(
            SESSION_START_PACK_ITEM_HOVER_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_param_fields_disabled_selector=(
            SESSION_START_PARAM_FIELDS_DISABLED_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_label_disabled_selector=(
            SESSION_START_LABEL_DISABLED_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_foot_bar_selector=(
            SESSION_START_FOOT_BAR_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        session_start_summary_ok_selector=(
            SESSION_START_SUMMARY_OK_SELECTOR_DINAMIC_POSTFIX_GFL1
        ),
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_GFL1,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_GFL1,
        color_text_secondary=COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_GFL1,
        color_border_soft=COLOR_BORDER_SOFT_DINAMIC_POSTFIX_GFL1,
        color_header_background=COLOR_HEADER_BACKGROUND_DINAMIC_POSTFIX_GFL1,
        color_header_border=COLOR_HEADER_BORDER_DINAMIC_POSTFIX_GFL1,
        color_accent=COLOR_ACCENT_DINAMIC_POSTFIX_GFL1,
        color_hover_surface=COLOR_HOVER_SURFACE_DINAMIC_POSTFIX_GFL1,
        color_hover_border=COLOR_HOVER_BORDER_DINAMIC_POSTFIX_GFL1,
        color_disabled_surface=COLOR_DISABLED_SURFACE_DINAMIC_POSTFIX_GFL1,
        color_disabled_text=COLOR_DISABLED_TEXT_DINAMIC_POSTFIX_GFL1,
        border_none=BORDER_NONE_DINAMIC_POSTFIX_GFL1,
        outline_none=OUTLINE_NONE_DINAMIC_POSTFIX_GFL1,
        border_width_1_px=BORDER_WIDTH_1_PX_DINAMIC_POSTFIX_GFL1,
        font_size_13_px=FONT_SIZE_13_PX_DINAMIC_POSTFIX_GFL1,
        font_size_11_px=FONT_SIZE_11_PX_DINAMIC_POSTFIX_GFL1,
        size_220_px=SIZE_220_PX_DINAMIC_POSTFIX_GFL1,
        size_44_px=SIZE_44_PX_DINAMIC_POSTFIX_GFL1,
        size_11_px=SIZE_11_PX_DINAMIC_POSTFIX_GFL1,
        size_10_px=SIZE_10_PX_DINAMIC_POSTFIX_GFL1,
        size_8_px=SIZE_8_PX_DINAMIC_POSTFIX_GFL1,
        size_6_px=SIZE_6_PX_DINAMIC_POSTFIX_GFL1,
        size_4_px=SIZE_4_PX_DINAMIC_POSTFIX_GFL1,
        size_2_px=SIZE_2_PX_DINAMIC_POSTFIX_GFL1,
        negative_4_px=NEGATIVE_4_PX_DINAMIC_POSTFIX_GFL1,
        pack_select_padding=PACK_SELECT_PADDING_DINAMIC_POSTFIX_GFL1,
        pack_item_padding=PACK_ITEM_PADDING_DINAMIC_POSTFIX_GFL1,
        pack_item_margin=PACK_ITEM_MARGIN_DINAMIC_POSTFIX_GFL1,
    )


def session_start_dialog_styles() -> str:
    """Render QSS for pack list, numeric fields, and dialog chrome.

    Returns:
        Stylesheet fragment for the modal that starts a training
        session.
    """
    return SESSION_START_DIALOG_TEMPLATE_DINAMIC_POSTFIX_GFL1.format(
        **_session_start_dialog_style_tokens()
    )
