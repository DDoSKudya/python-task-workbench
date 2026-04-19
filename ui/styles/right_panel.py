"""
This module generates the QSS stylesheet fragment for the applications
fixed-width right column, covering tabs, sliders, collapsible settings
panels, and history cards.

It works by defining a _RightPanelStyleTokens TypedDict of all template
placeholders, populating it with selector names, colors, sizes,
paddings, and font settings taken from a message catalog, and
interpolating that mapping into RIGHT_PANEL_STYLE_TEMPLATE_….

It contains the token type, the _right_panel_style_tokens helper that
assembles a complete dictionary of right-panel style tokens, and the
public right_panel_styles function that formats and returns the final
stylesheet text.

Within the broader system, this QSS fragment is combined with other
style sections to ensure the right-hand settings/history column has a
consistent, themeable appearance aligned with the rest of the UI.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_ZOPG,
    BORDER_NONE_DINAMIC_POSTFIX_ZOPG,
    BORDER_WIDTH_1_PX_DINAMIC_POSTFIX_ZOPG,
    BORDER_WIDTH_2_PX_DINAMIC_POSTFIX_ZOPG,
    COLLAPSIBLE_HEAD_PADDING_DINAMIC_POSTFIX_ZOPG,
    COLOR_ACCENT_DINAMIC_POSTFIX_ZOPG,
    COLOR_ACCENT_LIGHT_DINAMIC_POSTFIX_ZOPG,
    COLOR_BORDER_SOFT_DINAMIC_POSTFIX_ZOPG,
    COLOR_SURFACE_ALT_DINAMIC_POSTFIX_ZOPG,
    COLOR_SURFACE_MUTED_DINAMIC_POSTFIX_ZOPG,
    COLOR_SURFACE_SOFT_DINAMIC_POSTFIX_ZOPG,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_ZOPG,
    COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_ZOPG,
    COLOR_WHITE_DINAMIC_POSTFIX_ZOPG,
    DIFF_BUTTON_CHECKED_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    DIFF_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    DIFF_BUTTON_PADDING_DINAMIC_POSTFIX_ZOPG,
    DIFF_BUTTON_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    DURATION_VALUE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    FIELD_LABEL_PADDING_RIGHT_DINAMIC_POSTFIX_ZOPG,
    FONT_FAMILY_MONO_DINAMIC_POSTFIX_ZOPG,
    FONT_SIZE_10_PX_DINAMIC_POSTFIX_ZOPG,
    FONT_SIZE_11_PX_DINAMIC_POSTFIX_ZOPG,
    FONT_SIZE_12_PX_DINAMIC_POSTFIX_ZOPG,
    FONT_SIZE_13_PX_DINAMIC_POSTFIX_ZOPG,
    FONT_WEIGHT_500_DINAMIC_POSTFIX_ZOPG,
    FONT_WEIGHT_600_DINAMIC_POSTFIX_ZOPG,
    HISTORY_CARD_META_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    HISTORY_CARD_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    HISTORY_CARD_TITLE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    HISTORY_EMPTY_HINT_PADDING_DINAMIC_POSTFIX_ZOPG,
    HISTORY_EMPTY_HINT_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    PACK_CHIP_CHECKED_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    PACK_CHIP_HOVER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    PACK_CHIP_RADIUS_DINAMIC_POSTFIX_ZOPG,
    PACK_CHIP_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    RIGHT_ASIDE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    RIGHT_INNER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    RIGHT_OUTER_DIVIDER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    RIGHT_PANEL_STYLE_TEMPLATE_DINAMIC_POSTFIX_ZOPG,
    RIGHT_SCROLL_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    RIGHT_TAB_CHECKED_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    RIGHT_TAB_HOVER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    RIGHT_TAB_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    RIGHT_TAB_STRIP_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SETTINGS_COLLAPSIBLE_BODY_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SETTINGS_COLLAPSIBLE_HEAD_HOVER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SETTINGS_COLLAPSIBLE_HEAD_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SETTINGS_COLLAPSIBLE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SETTINGS_DIVIDER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SETTINGS_FIELD_LABEL_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SETTINGS_LABEL_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SIZE_1_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_2_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_3_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_4_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_5_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_6_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_8_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_10_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_16_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_24_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_30_PX_DINAMIC_POSTFIX_ZOPG,
    SIZE_40_PX_DINAMIC_POSTFIX_ZOPG,
    SLIDER_GROOVE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SLIDER_HANDLE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    SLIDER_MARGIN_DINAMIC_POSTFIX_ZOPG,
    SLIDER_SUB_PAGE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
    TAB_PADDING_DINAMIC_POSTFIX_ZOPG,
    TEXT_ALIGN_LEFT_DINAMIC_POSTFIX_ZOPG,
    ZERO_SPACING_DINAMIC_POSTFIX_ZOPG,
)


class _RightPanelStyleTokens(TypedDict):
    """Keyword fields for :data:`RIGHT_PANEL_STYLE_TEMPLATE_…`."""

    right_aside_selector: str
    right_tab_strip_selector: str
    right_outer_divider_selector: str
    right_scroll_selector: str
    right_inner_selector: str
    right_tab_selector: str
    right_tab_checked_selector: str
    right_tab_hover_selector: str
    settings_label_selector: str
    settings_field_label_selector: str
    slider_groove_selector: str
    slider_handle_selector: str
    slider_sub_page_selector: str
    duration_value_selector: str
    diff_button_selector: str
    diff_button_checked_selector: str
    diff_button_hover_selector: str
    pack_chip_selector: str
    pack_chip_checked_selector: str
    pack_chip_hover_selector: str
    settings_divider_selector: str
    settings_collapsible_selector: str
    settings_collapsible_head_selector: str
    settings_collapsible_head_hover_selector: str
    settings_collapsible_body_selector: str
    history_card_selector: str
    history_card_title_selector: str
    history_card_meta_selector: str
    history_empty_hint_selector: str
    color_white: str
    color_text_primary: str
    color_text_secondary: str
    color_border_soft: str
    color_accent: str
    color_accent_light: str
    color_surface_muted: str
    color_surface_alt: str
    color_surface_soft: str
    font_family_mono: str
    border_none: str
    background_transparent: str
    text_align_left: str
    border_width_1_px: str
    border_width_2_px: str
    size_40_px: str
    size_30_px: str
    size_24_px: str
    size_16_px: str
    size_10_px: str
    size_8_px: str
    size_6_px: str
    size_5_px: str
    size_4_px: str
    size_3_px: str
    size_2_px: str
    size_1_px: str
    zero_spacing: str
    tab_padding: str
    field_label_padding_right: str
    slider_margin: str
    diff_button_padding: str
    collapsible_head_padding: str
    history_empty_hint_padding: str
    pack_chip_radius: str
    font_size_13_px: str
    font_size_12_px: str
    font_size_11_px: str
    font_size_10_px: str
    font_weight_600: str
    font_weight_500: str


def _right_panel_style_tokens() -> _RightPanelStyleTokens:
    """Map catalog strings onto the right-panel QSS template fields.

    Returns:
        Keyword bundle for
        ``RIGHT_PANEL_STYLE_TEMPLATE_DINAMIC_POSTFIX_ZOPG``.
    """
    return _RightPanelStyleTokens(
        right_aside_selector=RIGHT_ASIDE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        right_tab_strip_selector=(
            RIGHT_TAB_STRIP_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        right_outer_divider_selector=(
            RIGHT_OUTER_DIVIDER_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        right_scroll_selector=RIGHT_SCROLL_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        right_inner_selector=RIGHT_INNER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        right_tab_selector=RIGHT_TAB_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        right_tab_checked_selector=(
            RIGHT_TAB_CHECKED_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        right_tab_hover_selector=RIGHT_TAB_HOVER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        settings_label_selector=SETTINGS_LABEL_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        settings_field_label_selector=(
            SETTINGS_FIELD_LABEL_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        slider_groove_selector=SLIDER_GROOVE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        slider_handle_selector=SLIDER_HANDLE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        slider_sub_page_selector=SLIDER_SUB_PAGE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        duration_value_selector=DURATION_VALUE_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        diff_button_selector=DIFF_BUTTON_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        diff_button_checked_selector=(
            DIFF_BUTTON_CHECKED_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        diff_button_hover_selector=(
            DIFF_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        pack_chip_selector=PACK_CHIP_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        pack_chip_checked_selector=(
            PACK_CHIP_CHECKED_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        pack_chip_hover_selector=PACK_CHIP_HOVER_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        settings_divider_selector=(
            SETTINGS_DIVIDER_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        settings_collapsible_selector=(
            SETTINGS_COLLAPSIBLE_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        settings_collapsible_head_selector=(
            SETTINGS_COLLAPSIBLE_HEAD_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        settings_collapsible_head_hover_selector=(
            SETTINGS_COLLAPSIBLE_HEAD_HOVER_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        settings_collapsible_body_selector=(
            SETTINGS_COLLAPSIBLE_BODY_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        history_card_selector=HISTORY_CARD_SELECTOR_DINAMIC_POSTFIX_ZOPG,
        history_card_title_selector=(
            HISTORY_CARD_TITLE_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        history_card_meta_selector=(
            HISTORY_CARD_META_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        history_empty_hint_selector=(
            HISTORY_EMPTY_HINT_SELECTOR_DINAMIC_POSTFIX_ZOPG
        ),
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_ZOPG,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_ZOPG,
        color_text_secondary=COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_ZOPG,
        color_border_soft=COLOR_BORDER_SOFT_DINAMIC_POSTFIX_ZOPG,
        color_accent=COLOR_ACCENT_DINAMIC_POSTFIX_ZOPG,
        color_accent_light=COLOR_ACCENT_LIGHT_DINAMIC_POSTFIX_ZOPG,
        color_surface_muted=COLOR_SURFACE_MUTED_DINAMIC_POSTFIX_ZOPG,
        color_surface_alt=COLOR_SURFACE_ALT_DINAMIC_POSTFIX_ZOPG,
        color_surface_soft=COLOR_SURFACE_SOFT_DINAMIC_POSTFIX_ZOPG,
        font_family_mono=FONT_FAMILY_MONO_DINAMIC_POSTFIX_ZOPG,
        border_none=BORDER_NONE_DINAMIC_POSTFIX_ZOPG,
        background_transparent=BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_ZOPG,
        text_align_left=TEXT_ALIGN_LEFT_DINAMIC_POSTFIX_ZOPG,
        border_width_1_px=BORDER_WIDTH_1_PX_DINAMIC_POSTFIX_ZOPG,
        border_width_2_px=BORDER_WIDTH_2_PX_DINAMIC_POSTFIX_ZOPG,
        size_40_px=SIZE_40_PX_DINAMIC_POSTFIX_ZOPG,
        size_30_px=SIZE_30_PX_DINAMIC_POSTFIX_ZOPG,
        size_24_px=SIZE_24_PX_DINAMIC_POSTFIX_ZOPG,
        size_16_px=SIZE_16_PX_DINAMIC_POSTFIX_ZOPG,
        size_10_px=SIZE_10_PX_DINAMIC_POSTFIX_ZOPG,
        size_8_px=SIZE_8_PX_DINAMIC_POSTFIX_ZOPG,
        size_6_px=SIZE_6_PX_DINAMIC_POSTFIX_ZOPG,
        size_5_px=SIZE_5_PX_DINAMIC_POSTFIX_ZOPG,
        size_4_px=SIZE_4_PX_DINAMIC_POSTFIX_ZOPG,
        size_3_px=SIZE_3_PX_DINAMIC_POSTFIX_ZOPG,
        size_2_px=SIZE_2_PX_DINAMIC_POSTFIX_ZOPG,
        size_1_px=SIZE_1_PX_DINAMIC_POSTFIX_ZOPG,
        zero_spacing=ZERO_SPACING_DINAMIC_POSTFIX_ZOPG,
        tab_padding=TAB_PADDING_DINAMIC_POSTFIX_ZOPG,
        field_label_padding_right=(
            FIELD_LABEL_PADDING_RIGHT_DINAMIC_POSTFIX_ZOPG
        ),
        slider_margin=SLIDER_MARGIN_DINAMIC_POSTFIX_ZOPG,
        diff_button_padding=DIFF_BUTTON_PADDING_DINAMIC_POSTFIX_ZOPG,
        collapsible_head_padding=(
            COLLAPSIBLE_HEAD_PADDING_DINAMIC_POSTFIX_ZOPG
        ),
        history_empty_hint_padding=(
            HISTORY_EMPTY_HINT_PADDING_DINAMIC_POSTFIX_ZOPG
        ),
        pack_chip_radius=PACK_CHIP_RADIUS_DINAMIC_POSTFIX_ZOPG,
        font_size_13_px=FONT_SIZE_13_PX_DINAMIC_POSTFIX_ZOPG,
        font_size_12_px=FONT_SIZE_12_PX_DINAMIC_POSTFIX_ZOPG,
        font_size_11_px=FONT_SIZE_11_PX_DINAMIC_POSTFIX_ZOPG,
        font_size_10_px=FONT_SIZE_10_PX_DINAMIC_POSTFIX_ZOPG,
        font_weight_600=FONT_WEIGHT_600_DINAMIC_POSTFIX_ZOPG,
        font_weight_500=FONT_WEIGHT_500_DINAMIC_POSTFIX_ZOPG,
    )


def right_panel_styles() -> str:
    """Emit QSS for tabs, sliders, collapsible settings, and history
    cards.

    Returns:
        Stylesheet text for the fixed-width right column.
    """
    return RIGHT_PANEL_STYLE_TEMPLATE_DINAMIC_POSTFIX_ZOPG.format(
        **_right_panel_style_tokens()
    )
