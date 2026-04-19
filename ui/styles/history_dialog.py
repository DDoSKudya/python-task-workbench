"""
This module generates the QSS stylesheet fragment used to style the
modal “history” dialog, including its chrome, toolbar, table, and
footer actions.

It works by defining a _HistoryDialogStyleTokens TypedDict of all
placeholders required by a history-dialog QSS template, populating that
mapping from catalog-provided selectors, colors, font sizes, and spacing
values, and then interpolating them into
HISTORY_DIALOG_STYLE_TEMPLATE_….

It contains the token type, the _history_dialog_style_tokens helper that
assembles a complete dictionary of style tokens, and the public
history_dialog_styles function that formats and returns the final QSS
string.

Within the broader system, this stylesheet fragment is combined with
other QSS sections to ensure the history browser dialog has a
consistent, themeable appearance aligned with the rest of the
application UI.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    ACCENT_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X,
    ACCENT_BUTTON_SELECTOR_DINAMIC_POSTFIX_SF3X,
    BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_SF3X,
    BORDER_NONE_DINAMIC_POSTFIX_SF3X,
    BORDER_WIDTH_PX_DINAMIC_POSTFIX_SF3X,
    CLOSE_TINY_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X,
    CLOSE_TINY_SELECTOR_DINAMIC_POSTFIX_SF3X,
    COLOR_ACCENT_DINAMIC_POSTFIX_SF3X,
    COLOR_ACCENT_HOVER_DINAMIC_POSTFIX_SF3X,
    COLOR_BACKGROUND_SOFT_DINAMIC_POSTFIX_SF3X,
    COLOR_BORDER_SOFT_DINAMIC_POSTFIX_SF3X,
    COLOR_DANGER_DINAMIC_POSTFIX_SF3X,
    COLOR_DANGER_HOVER_DINAMIC_POSTFIX_SF3X,
    COLOR_DANGER_TEXT_DINAMIC_POSTFIX_SF3X,
    COLOR_SURFACE_INPUT_DINAMIC_POSTFIX_SF3X,
    COLOR_SURFACE_MUTED_DINAMIC_POSTFIX_SF3X,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_SF3X,
    COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_SF3X,
    COLOR_WHITE_DINAMIC_POSTFIX_SF3X,
    DANGER_OUTLINE_BUTTON_SELECTOR_DINAMIC_POSTFIX_SF3X,
    DIALOG_DIVIDER_SELECTOR_DINAMIC_POSTFIX_SF3X,
    DIALOG_HEADER_BAR_SELECTOR_DINAMIC_POSTFIX_SF3X,
    DIALOG_SECTION_CAPS_SELECTOR_DINAMIC_POSTFIX_SF3X,
    DIALOG_SECTION_SELECTOR_DINAMIC_POSTFIX_SF3X,
    DIALOG_TITLE_SELECTOR_DINAMIC_POSTFIX_SF3X,
    FONT_SIZE_11_PX_DINAMIC_POSTFIX_SF3X,
    FONT_SIZE_12_PX_DINAMIC_POSTFIX_SF3X,
    FONT_SIZE_13_PX_DINAMIC_POSTFIX_SF3X,
    FONT_SIZE_14_PX_DINAMIC_POSTFIX_SF3X,
    FONT_SIZE_18_PX_DINAMIC_POSTFIX_SF3X,
    FONT_WEIGHT_600_DINAMIC_POSTFIX_SF3X,
    FONT_WEIGHT_700_DINAMIC_POSTFIX_SF3X,
    HEADER_SECTION_PADDING_DINAMIC_POSTFIX_SF3X,
    HISTORY_CLEAR_HEADER_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_CLEAR_HEADER_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_COUNT_LABEL_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_DIALOG_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_DIALOG_STYLE_TEMPLATE_DINAMIC_POSTFIX_SF3X,
    HISTORY_FOOT_BAR_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_PANEL_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_SEARCH_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_TABLE_HEADER_LAST_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_TABLE_HEADER_SECTION_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_TABLE_HEADER_SELECTOR_DINAMIC_POSTFIX_SF3X,
    HISTORY_TABLE_SELECTOR_DINAMIC_POSTFIX_SF3X,
    LETTER_SPACING_HALF_PX_DINAMIC_POSTFIX_SF3X,
    SECONDARY_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X,
    SECONDARY_BUTTON_SELECTOR_DINAMIC_POSTFIX_SF3X,
    SIZE_1_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_6_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_8_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_10_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_28_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_32_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_36_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_40_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_48_PX_DINAMIC_POSTFIX_SF3X,
    SIZE_56_PX_DINAMIC_POSTFIX_SF3X,
    TABLE_ICON_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X,
    TABLE_ICON_BUTTON_SELECTOR_DINAMIC_POSTFIX_SF3X,
    TEXT_TRANSFORM_UPPERCASE_DINAMIC_POSTFIX_SF3X,
    ZERO_SPACING_DINAMIC_POSTFIX_SF3X,
)


class _HistoryDialogStyleTokens(TypedDict):
    """Placeholders for :data:`HISTORY_DIALOG_STYLE_TEMPLATE_…`."""

    history_dialog_selector: str
    dialog_title_selector: str
    dialog_section_selector: str
    close_tiny_selector: str
    close_tiny_hover_selector: str
    history_clear_header_selector: str
    history_clear_header_hover_selector: str
    history_search_selector: str
    secondary_button_selector: str
    secondary_button_hover_selector: str
    accent_button_selector: str
    accent_button_hover_selector: str
    danger_outline_button_selector: str
    history_panel_selector: str
    history_count_label_selector: str
    history_table_selector: str
    history_table_header_selector: str
    history_table_header_section_selector: str
    history_table_header_last_selector: str
    table_icon_button_selector: str
    table_icon_button_hover_selector: str
    dialog_header_bar_selector: str
    dialog_divider_selector: str
    dialog_section_caps_selector: str
    history_foot_bar_selector: str
    color_white: str
    color_text_primary: str
    color_text_secondary: str
    color_border_soft: str
    color_background_soft: str
    color_surface_muted: str
    color_surface_input: str
    color_danger: str
    color_danger_hover: str
    color_accent: str
    color_accent_hover: str
    color_danger_text: str
    border_none: str
    background_transparent: str
    text_transform_uppercase: str
    border_width_px: str
    font_size_18_px: str
    font_size_14_px: str
    font_size_13_px: str
    font_size_12_px: str
    font_size_11_px: str
    font_weight_700: str
    font_weight_600: str
    size_40_px: str
    size_32_px: str
    size_28_px: str
    size_56_px: str
    size_48_px: str
    size_36_px: str
    size_10_px: str
    size_8_px: str
    size_6_px: str
    size_1_px: str
    letter_spacing_half_px: str
    header_section_padding: str
    zero_spacing: str


def _history_dialog_style_tokens() -> _HistoryDialogStyleTokens:
    """Build tokens for the history dialog QSS template.

    Returns:
        Keyword arguments for
        ``HISTORY_DIALOG_STYLE_TEMPLATE_DINAMIC_POSTFIX_SF3X``.
    """
    return _HistoryDialogStyleTokens(
        history_dialog_selector=HISTORY_DIALOG_SELECTOR_DINAMIC_POSTFIX_SF3X,
        dialog_title_selector=DIALOG_TITLE_SELECTOR_DINAMIC_POSTFIX_SF3X,
        dialog_section_selector=DIALOG_SECTION_SELECTOR_DINAMIC_POSTFIX_SF3X,
        close_tiny_selector=CLOSE_TINY_SELECTOR_DINAMIC_POSTFIX_SF3X,
        close_tiny_hover_selector=(
            CLOSE_TINY_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        history_clear_header_selector=(
            HISTORY_CLEAR_HEADER_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        history_clear_header_hover_selector=(
            HISTORY_CLEAR_HEADER_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        history_search_selector=HISTORY_SEARCH_SELECTOR_DINAMIC_POSTFIX_SF3X,
        secondary_button_selector=(
            SECONDARY_BUTTON_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        secondary_button_hover_selector=(
            SECONDARY_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        accent_button_selector=ACCENT_BUTTON_SELECTOR_DINAMIC_POSTFIX_SF3X,
        accent_button_hover_selector=(
            ACCENT_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        danger_outline_button_selector=(
            DANGER_OUTLINE_BUTTON_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        history_panel_selector=HISTORY_PANEL_SELECTOR_DINAMIC_POSTFIX_SF3X,
        history_count_label_selector=(
            HISTORY_COUNT_LABEL_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        history_table_selector=HISTORY_TABLE_SELECTOR_DINAMIC_POSTFIX_SF3X,
        history_table_header_selector=(
            HISTORY_TABLE_HEADER_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        history_table_header_section_selector=(
            HISTORY_TABLE_HEADER_SECTION_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        history_table_header_last_selector=(
            HISTORY_TABLE_HEADER_LAST_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        table_icon_button_selector=(
            TABLE_ICON_BUTTON_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        table_icon_button_hover_selector=(
            TABLE_ICON_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        dialog_header_bar_selector=(
            DIALOG_HEADER_BAR_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        dialog_divider_selector=DIALOG_DIVIDER_SELECTOR_DINAMIC_POSTFIX_SF3X,
        dialog_section_caps_selector=(
            DIALOG_SECTION_CAPS_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        history_foot_bar_selector=(
            HISTORY_FOOT_BAR_SELECTOR_DINAMIC_POSTFIX_SF3X
        ),
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_SF3X,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_SF3X,
        color_text_secondary=COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_SF3X,
        color_border_soft=COLOR_BORDER_SOFT_DINAMIC_POSTFIX_SF3X,
        color_background_soft=COLOR_BACKGROUND_SOFT_DINAMIC_POSTFIX_SF3X,
        color_surface_muted=COLOR_SURFACE_MUTED_DINAMIC_POSTFIX_SF3X,
        color_surface_input=COLOR_SURFACE_INPUT_DINAMIC_POSTFIX_SF3X,
        color_danger=COLOR_DANGER_DINAMIC_POSTFIX_SF3X,
        color_danger_hover=COLOR_DANGER_HOVER_DINAMIC_POSTFIX_SF3X,
        color_accent=COLOR_ACCENT_DINAMIC_POSTFIX_SF3X,
        color_accent_hover=COLOR_ACCENT_HOVER_DINAMIC_POSTFIX_SF3X,
        color_danger_text=COLOR_DANGER_TEXT_DINAMIC_POSTFIX_SF3X,
        border_none=BORDER_NONE_DINAMIC_POSTFIX_SF3X,
        background_transparent=BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_SF3X,
        text_transform_uppercase=(
            TEXT_TRANSFORM_UPPERCASE_DINAMIC_POSTFIX_SF3X
        ),
        border_width_px=BORDER_WIDTH_PX_DINAMIC_POSTFIX_SF3X,
        font_size_18_px=FONT_SIZE_18_PX_DINAMIC_POSTFIX_SF3X,
        font_size_14_px=FONT_SIZE_14_PX_DINAMIC_POSTFIX_SF3X,
        font_size_13_px=FONT_SIZE_13_PX_DINAMIC_POSTFIX_SF3X,
        font_size_12_px=FONT_SIZE_12_PX_DINAMIC_POSTFIX_SF3X,
        font_size_11_px=FONT_SIZE_11_PX_DINAMIC_POSTFIX_SF3X,
        font_weight_700=FONT_WEIGHT_700_DINAMIC_POSTFIX_SF3X,
        font_weight_600=FONT_WEIGHT_600_DINAMIC_POSTFIX_SF3X,
        size_40_px=SIZE_40_PX_DINAMIC_POSTFIX_SF3X,
        size_32_px=SIZE_32_PX_DINAMIC_POSTFIX_SF3X,
        size_28_px=SIZE_28_PX_DINAMIC_POSTFIX_SF3X,
        size_56_px=SIZE_56_PX_DINAMIC_POSTFIX_SF3X,
        size_48_px=SIZE_48_PX_DINAMIC_POSTFIX_SF3X,
        size_36_px=SIZE_36_PX_DINAMIC_POSTFIX_SF3X,
        size_10_px=SIZE_10_PX_DINAMIC_POSTFIX_SF3X,
        size_8_px=SIZE_8_PX_DINAMIC_POSTFIX_SF3X,
        size_6_px=SIZE_6_PX_DINAMIC_POSTFIX_SF3X,
        size_1_px=SIZE_1_PX_DINAMIC_POSTFIX_SF3X,
        letter_spacing_half_px=LETTER_SPACING_HALF_PX_DINAMIC_POSTFIX_SF3X,
        header_section_padding=HEADER_SECTION_PADDING_DINAMIC_POSTFIX_SF3X,
        zero_spacing=ZERO_SPACING_DINAMIC_POSTFIX_SF3X,
    )


def history_dialog_styles() -> str:
    """Render the QSS bundle for the modal history browser.

    Returns:
        Stylesheet text covering chrome, toolbar, table, and footer
        actions.
    """
    return HISTORY_DIALOG_STYLE_TEMPLATE_DINAMIC_POSTFIX_SF3X.format(
        **_history_dialog_style_tokens()
    )
