"""
This module generates the QSS stylesheet fragment for the applications
top header bar, including branding, the timer pill, and action buttons
such as start, check, and stop.

It works by defining a _HeaderStyleTokens TypedDict that enumerates all
template placeholders, filling it from catalog-provided selectors and
style tokens in _header_style_tokens, and interpolating those values
into a HEADER_STYLE_TEMPLATE_… format string.

It contains only style-related data plumbing: the token type, the
_header_style_tokens helper that returns a fully populated mapping of
selectors, colors, fonts, paddings, and sizes, and the public
header_styles function that returns the final QSS string.

Within the broader system, this header stylesheet fragment is combined
with other QSS sections to form the overall application stylesheet,
ensuring the headers appearance is consistent and configurable via the
shared message catalog.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    ACTION_BUTTON_PADDING_DINAMIC_POSTFIX_QGVK,
    ALIGN_CENTER_DINAMIC_POSTFIX_QGVK,
    APP_SUBTITLE_SELECTOR_DINAMIC_POSTFIX_QGVK,
    APP_TITLE_SELECTOR_DINAMIC_POSTFIX_QGVK,
    BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_QGVK,
    BORDER_NONE_DINAMIC_POSTFIX_QGVK,
    BORDER_WIDTH_PX_DINAMIC_POSTFIX_QGVK,
    BUTTON_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
    BUTTON_FONT_WEIGHT_DINAMIC_POSTFIX_QGVK,
    COLOR_ACCENT_PRIMARY_DINAMIC_POSTFIX_QGVK,
    COLOR_ACCENT_PRIMARY_HOVER_DINAMIC_POSTFIX_QGVK,
    COLOR_ACCENT_PRIMARY_PRESSED_DINAMIC_POSTFIX_QGVK,
    COLOR_BORDER_SOFT_DINAMIC_POSTFIX_QGVK,
    COLOR_CHECK_BACKGROUND_DINAMIC_POSTFIX_QGVK,
    COLOR_CHECK_HOVER_DINAMIC_POSTFIX_QGVK,
    COLOR_STOP_HOVER_DINAMIC_POSTFIX_QGVK,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_QGVK,
    COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_QGVK,
    COLOR_TIMER_BACKGROUND_DINAMIC_POSTFIX_QGVK,
    COLOR_TIMER_WARN_DINAMIC_POSTFIX_QGVK,
    COLOR_WHITE_DINAMIC_POSTFIX_QGVK,
    DISABLED_OPACITY_DINAMIC_POSTFIX_QGVK,
    FONT_FAMILY_MONO_DINAMIC_POSTFIX_QGVK,
    FONT_FAMILY_TITLE_DINAMIC_POSTFIX_QGVK,
    HEADER_CHECK_DISABLED_SELECTOR_DINAMIC_POSTFIX_QGVK,
    HEADER_CHECK_HOVER_SELECTOR_DINAMIC_POSTFIX_QGVK,
    HEADER_CHECK_SELECTOR_DINAMIC_POSTFIX_QGVK,
    HEADER_MIN_HEIGHT_PX_DINAMIC_POSTFIX_QGVK,
    HEADER_START_HOVER_SELECTOR_DINAMIC_POSTFIX_QGVK,
    HEADER_START_PRESSED_SELECTOR_DINAMIC_POSTFIX_QGVK,
    HEADER_START_SELECTOR_DINAMIC_POSTFIX_QGVK,
    HEADER_STOP_HOVER_SELECTOR_DINAMIC_POSTFIX_QGVK,
    HEADER_STOP_SELECTOR_DINAMIC_POSTFIX_QGVK,
    HEADER_STYLE_TEMPLATE_DINAMIC_POSTFIX_QGVK,
    LIGHT_HEADER_SELECTOR_DINAMIC_POSTFIX_QGVK,
    LINK_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
    LINK_PADDING_DINAMIC_POSTFIX_QGVK,
    LINK_SMALL_HOVER_SELECTOR_DINAMIC_POSTFIX_QGVK,
    LINK_SMALL_SELECTOR_DINAMIC_POSTFIX_QGVK,
    LOGO_BADGE_SELECTOR_DINAMIC_POSTFIX_QGVK,
    LOGO_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
    LOGO_FONT_WEIGHT_DINAMIC_POSTFIX_QGVK,
    LOGO_RADIUS_PX_DINAMIC_POSTFIX_QGVK,
    LOGO_SIZE_PX_DINAMIC_POSTFIX_QGVK,
    START_BUTTON_PADDING_DINAMIC_POSTFIX_QGVK,
    SUBTITLE_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
    TEXT_ALIGN_LEFT_DINAMIC_POSTFIX_QGVK,
    TIMER_PADDING_DINAMIC_POSTFIX_QGVK,
    TIMER_PILL_SELECTOR_DINAMIC_POSTFIX_QGVK,
    TIMER_PILL_TEXT_SELECTOR_DINAMIC_POSTFIX_QGVK,
    TIMER_PILL_TEXT_WARN_SELECTOR_DINAMIC_POSTFIX_QGVK,
    TIMER_RADIUS_PX_DINAMIC_POSTFIX_QGVK,
    TITLE_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
    TITLE_FONT_WEIGHT_DINAMIC_POSTFIX_QGVK,
    TITLE_PADDING_DINAMIC_POSTFIX_QGVK,
    ZERO_SPACING_DINAMIC_POSTFIX_QGVK,
)


class _HeaderStyleTokens(TypedDict):
    """Keyword fields for :data:`HEADER_STYLE_TEMPLATE_…`."""

    light_header_selector: str
    logo_badge_selector: str
    app_title_selector: str
    app_subtitle_selector: str
    timer_pill_selector: str
    timer_pill_text_selector: str
    timer_pill_text_warn_selector: str
    header_start_selector: str
    header_start_hover_selector: str
    header_start_pressed_selector: str
    header_check_selector: str
    header_check_hover_selector: str
    header_check_disabled_selector: str
    header_stop_selector: str
    header_stop_hover_selector: str
    link_small_selector: str
    link_small_hover_selector: str
    color_white: str
    color_text_primary: str
    color_text_secondary: str
    color_border_soft: str
    color_accent_primary: str
    color_accent_primary_hover: str
    color_accent_primary_pressed: str
    color_timer_background: str
    color_timer_warn: str
    color_check_background: str
    color_check_hover: str
    color_stop_hover: str
    font_family_title: str
    font_family_mono: str
    border_none: str
    background_transparent: str
    text_align_left: str
    align_center: str
    border_width_px: str
    header_min_height_px: str
    logo_size_px: str
    logo_radius_px: str
    title_font_size_px: str
    title_font_weight: str
    title_padding: str
    subtitle_font_size_px: str
    timer_radius_px: str
    timer_padding: str
    button_font_size_px: str
    button_font_weight: str
    start_button_padding: str
    action_button_padding: str
    link_font_size_px: str
    link_padding: str
    logo_font_size_px: str
    logo_font_weight: str
    disabled_opacity: str
    zero_spacing: str


def _header_style_tokens() -> _HeaderStyleTokens:
    """Fill the header QSS template from the message catalog.

    Returns:
        Keyword bundle for
        ``HEADER_STYLE_TEMPLATE_DINAMIC_POSTFIX_QGVK``.
    """
    return _HeaderStyleTokens(
        light_header_selector=LIGHT_HEADER_SELECTOR_DINAMIC_POSTFIX_QGVK,
        logo_badge_selector=LOGO_BADGE_SELECTOR_DINAMIC_POSTFIX_QGVK,
        app_title_selector=APP_TITLE_SELECTOR_DINAMIC_POSTFIX_QGVK,
        app_subtitle_selector=APP_SUBTITLE_SELECTOR_DINAMIC_POSTFIX_QGVK,
        timer_pill_selector=TIMER_PILL_SELECTOR_DINAMIC_POSTFIX_QGVK,
        timer_pill_text_selector=(
            TIMER_PILL_TEXT_SELECTOR_DINAMIC_POSTFIX_QGVK
        ),
        timer_pill_text_warn_selector=(
            TIMER_PILL_TEXT_WARN_SELECTOR_DINAMIC_POSTFIX_QGVK
        ),
        header_start_selector=HEADER_START_SELECTOR_DINAMIC_POSTFIX_QGVK,
        header_start_hover_selector=(
            HEADER_START_HOVER_SELECTOR_DINAMIC_POSTFIX_QGVK
        ),
        header_start_pressed_selector=(
            HEADER_START_PRESSED_SELECTOR_DINAMIC_POSTFIX_QGVK
        ),
        header_check_selector=HEADER_CHECK_SELECTOR_DINAMIC_POSTFIX_QGVK,
        header_check_hover_selector=(
            HEADER_CHECK_HOVER_SELECTOR_DINAMIC_POSTFIX_QGVK
        ),
        header_check_disabled_selector=(
            HEADER_CHECK_DISABLED_SELECTOR_DINAMIC_POSTFIX_QGVK
        ),
        header_stop_selector=HEADER_STOP_SELECTOR_DINAMIC_POSTFIX_QGVK,
        header_stop_hover_selector=(
            HEADER_STOP_HOVER_SELECTOR_DINAMIC_POSTFIX_QGVK
        ),
        link_small_selector=LINK_SMALL_SELECTOR_DINAMIC_POSTFIX_QGVK,
        link_small_hover_selector=(
            LINK_SMALL_HOVER_SELECTOR_DINAMIC_POSTFIX_QGVK
        ),
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_QGVK,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_QGVK,
        color_text_secondary=COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_QGVK,
        color_border_soft=COLOR_BORDER_SOFT_DINAMIC_POSTFIX_QGVK,
        color_accent_primary=COLOR_ACCENT_PRIMARY_DINAMIC_POSTFIX_QGVK,
        color_accent_primary_hover=(
            COLOR_ACCENT_PRIMARY_HOVER_DINAMIC_POSTFIX_QGVK
        ),
        color_accent_primary_pressed=(
            COLOR_ACCENT_PRIMARY_PRESSED_DINAMIC_POSTFIX_QGVK
        ),
        color_timer_background=COLOR_TIMER_BACKGROUND_DINAMIC_POSTFIX_QGVK,
        color_timer_warn=COLOR_TIMER_WARN_DINAMIC_POSTFIX_QGVK,
        color_check_background=COLOR_CHECK_BACKGROUND_DINAMIC_POSTFIX_QGVK,
        color_check_hover=COLOR_CHECK_HOVER_DINAMIC_POSTFIX_QGVK,
        color_stop_hover=COLOR_STOP_HOVER_DINAMIC_POSTFIX_QGVK,
        font_family_title=FONT_FAMILY_TITLE_DINAMIC_POSTFIX_QGVK,
        font_family_mono=FONT_FAMILY_MONO_DINAMIC_POSTFIX_QGVK,
        border_none=BORDER_NONE_DINAMIC_POSTFIX_QGVK,
        background_transparent=BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_QGVK,
        text_align_left=TEXT_ALIGN_LEFT_DINAMIC_POSTFIX_QGVK,
        align_center=ALIGN_CENTER_DINAMIC_POSTFIX_QGVK,
        border_width_px=BORDER_WIDTH_PX_DINAMIC_POSTFIX_QGVK,
        header_min_height_px=HEADER_MIN_HEIGHT_PX_DINAMIC_POSTFIX_QGVK,
        logo_size_px=LOGO_SIZE_PX_DINAMIC_POSTFIX_QGVK,
        logo_radius_px=LOGO_RADIUS_PX_DINAMIC_POSTFIX_QGVK,
        title_font_size_px=TITLE_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
        title_font_weight=TITLE_FONT_WEIGHT_DINAMIC_POSTFIX_QGVK,
        title_padding=TITLE_PADDING_DINAMIC_POSTFIX_QGVK,
        subtitle_font_size_px=SUBTITLE_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
        timer_radius_px=TIMER_RADIUS_PX_DINAMIC_POSTFIX_QGVK,
        timer_padding=TIMER_PADDING_DINAMIC_POSTFIX_QGVK,
        button_font_size_px=BUTTON_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
        button_font_weight=BUTTON_FONT_WEIGHT_DINAMIC_POSTFIX_QGVK,
        start_button_padding=START_BUTTON_PADDING_DINAMIC_POSTFIX_QGVK,
        action_button_padding=ACTION_BUTTON_PADDING_DINAMIC_POSTFIX_QGVK,
        link_font_size_px=LINK_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
        link_padding=LINK_PADDING_DINAMIC_POSTFIX_QGVK,
        logo_font_size_px=LOGO_FONT_SIZE_PX_DINAMIC_POSTFIX_QGVK,
        logo_font_weight=LOGO_FONT_WEIGHT_DINAMIC_POSTFIX_QGVK,
        disabled_opacity=DISABLED_OPACITY_DINAMIC_POSTFIX_QGVK,
        zero_spacing=ZERO_SPACING_DINAMIC_POSTFIX_QGVK,
    )


def header_styles() -> str:
    """Emit QSS for the top bar: branding, timer pill, and action
    buttons.

    Returns:
        One stylesheet fragment for the light header chrome.
    """
    return HEADER_STYLE_TEMPLATE_DINAMIC_POSTFIX_QGVK.format(
        **_header_style_tokens()
    )
