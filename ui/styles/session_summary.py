"""
This module generates the QSS stylesheet fragment used to style the
session summary dialog, including stats chips, per-task rows, and the
dialog chrome.

It works by defining a _SessionSummaryStyleTokens TypedDict that lists
all placeholders expected by a QSS template, populating that mapping
with selectors, colors, font metrics, and spacing values from a message
catalog, and interpolating them into SESSION_SUMMARY_STYLE_TEMPLATE_….

It contains the token type, the _session_summary_style_tokens helper
that assembles a complete dictionary of style tokens, and the public
session_summary_styles function that formats and returns the final
stylesheet text.

Within the broader system, this fragment is combined with other QSS
sections so that the session-results modal has a consistent, themeable
appearance for success banners, status chips, icons, and action buttons
aligned with the rest of the UI.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_GXXL,
    BORDER_NONE_DINAMIC_POSTFIX_GXXL,
    BORDER_WIDTH_1_PX_DINAMIC_POSTFIX_GXXL,
    COLOR_ACCENT_DINAMIC_POSTFIX_GXXL,
    COLOR_ACCENT_HOVER_DINAMIC_POSTFIX_GXXL,
    COLOR_BORDER_SOFT_DINAMIC_POSTFIX_GXXL,
    COLOR_DANGER_BORDER_DINAMIC_POSTFIX_GXXL,
    COLOR_DANGER_CHIP_BACKGROUND_DINAMIC_POSTFIX_GXXL,
    COLOR_DANGER_TEXT_DINAMIC_POSTFIX_GXXL,
    COLOR_HEADER_BACKGROUND_DINAMIC_POSTFIX_GXXL,
    COLOR_HEADER_BORDER_DINAMIC_POSTFIX_GXXL,
    COLOR_ICON_BUTTON_HOVER_DINAMIC_POSTFIX_GXXL,
    COLOR_IDLE_TEXT_DINAMIC_POSTFIX_GXXL,
    COLOR_NEUTRAL_BACKGROUND_DINAMIC_POSTFIX_GXXL,
    COLOR_SCROLL_BACKGROUND_DINAMIC_POSTFIX_GXXL,
    COLOR_SUCCESS_BANNER_BACKGROUND_DINAMIC_POSTFIX_GXXL,
    COLOR_SUCCESS_BORDER_DINAMIC_POSTFIX_GXXL,
    COLOR_SUCCESS_CHIP_BACKGROUND_DINAMIC_POSTFIX_GXXL,
    COLOR_SUCCESS_TEXT_DINAMIC_POSTFIX_GXXL,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_GXXL,
    COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_GXXL,
    COLOR_WARN_CHIP_BACKGROUND_DINAMIC_POSTFIX_GXXL,
    COLOR_WARN_CHIP_BORDER_DINAMIC_POSTFIX_GXXL,
    COLOR_WARN_TEXT_DINAMIC_POSTFIX_GXXL,
    COLOR_WHITE_DINAMIC_POSTFIX_GXXL,
    FONT_FAMILY_MONO_DINAMIC_POSTFIX_GXXL,
    FONT_SIZE_11_PX_DINAMIC_POSTFIX_GXXL,
    FONT_SIZE_12_PX_DINAMIC_POSTFIX_GXXL,
    FONT_SIZE_13_PX_DINAMIC_POSTFIX_GXXL,
    FONT_SIZE_14_PX_DINAMIC_POSTFIX_GXXL,
    FONT_SIZE_16_PX_DINAMIC_POSTFIX_GXXL,
    FONT_SIZE_22_PX_DINAMIC_POSTFIX_GXXL,
    FONT_WEIGHT_600_DINAMIC_POSTFIX_GXXL,
    FONT_WEIGHT_700_DINAMIC_POSTFIX_GXXL,
    OK_BUTTON_DIALOG_PADDING_DINAMIC_POSTFIX_GXXL,
    OK_BUTTON_PADDING_DINAMIC_POSTFIX_GXXL,
    SESSION_SUMMARY_DIALOG_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SESSION_SUMMARY_HEADER_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SESSION_SUMMARY_STYLE_TEMPLATE_DINAMIC_POSTFIX_GXXL,
    SESSION_SUMMARY_TITLE_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SIZE_8_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_10_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_11_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_12_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_34_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_36_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_40_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_44_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_72_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_168_PX_DINAMIC_POSTFIX_GXXL,
    SIZE_200_PX_DINAMIC_POSTFIX_GXXL,
    SUMMARY_CHIP_BAD_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_CHIP_LABEL_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_CHIP_NEUTRAL_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_CHIP_OK_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_CHIP_VALUE_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_CHIP_WARN_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_DIALOG_OK_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_DIALOG_OK_BUTTON_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_FOOT_BAR_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_ICON_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_ICON_BUTTON_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_LIST_HOST_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_MARK_BAD_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_MARK_IDLE_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_MARK_OK_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_MARK_PENDING_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_OK_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_OK_BUTTON_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_ROW_ACTIONS_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_SCROLL_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_SCROLL_VIEWPORT_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_STATS_ROW_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_SUCCESS_BANNER_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_SUCCESS_TEXT_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_TASK_NUM_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_TASK_ROW_SELECTOR_DINAMIC_POSTFIX_GXXL,
    SUMMARY_TASK_TITLE_SELECTOR_DINAMIC_POSTFIX_GXXL,
)


class _SessionSummaryStyleTokens(TypedDict):
    """Keyword fields for :data:`SESSION_SUMMARY_STYLE_TEMPLATE_…`."""

    session_summary_dialog_selector: str
    session_summary_header_selector: str
    session_summary_title_selector: str
    summary_stats_row_selector: str
    summary_chip_ok_selector: str
    summary_chip_bad_selector: str
    summary_chip_neutral_selector: str
    summary_chip_warn_selector: str
    summary_chip_value_selector: str
    summary_chip_label_selector: str
    summary_success_banner_selector: str
    summary_success_text_selector: str
    summary_scroll_selector: str
    summary_scroll_viewport_selector: str
    summary_list_host_selector: str
    summary_task_row_selector: str
    summary_mark_ok_selector: str
    summary_mark_bad_selector: str
    summary_mark_pending_selector: str
    summary_mark_idle_selector: str
    summary_task_num_selector: str
    summary_task_title_selector: str
    summary_row_actions_selector: str
    summary_icon_button_selector: str
    summary_icon_button_hover_selector: str
    summary_foot_bar_selector: str
    summary_dialog_ok_button_selector: str
    summary_dialog_ok_button_hover_selector: str
    summary_ok_button_selector: str
    summary_ok_button_hover_selector: str
    color_white: str
    color_text_primary: str
    color_text_secondary: str
    color_border_soft: str
    color_header_background: str
    color_header_border: str
    color_success_border: str
    color_success_chip_background: str
    color_success_banner_background: str
    color_success_text: str
    color_danger_border: str
    color_danger_chip_background: str
    color_danger_text: str
    color_neutral_background: str
    color_warn_chip_background: str
    color_warn_chip_border: str
    color_warn_text: str
    color_idle_text: str
    color_scroll_background: str
    color_icon_button_hover: str
    color_accent: str
    color_accent_hover: str
    font_family_mono: str
    background_transparent: str
    border_none: str
    border_width_1_px: str
    font_size_22_px: str
    font_size_16_px: str
    font_size_14_px: str
    font_size_13_px: str
    font_size_12_px: str
    font_size_11_px: str
    font_weight_700: str
    font_weight_600: str
    size_200_px: str
    size_168_px: str
    size_72_px: str
    size_44_px: str
    size_40_px: str
    size_36_px: str
    size_34_px: str
    size_12_px: str
    size_11_px: str
    size_10_px: str
    size_8_px: str
    ok_button_dialog_padding: str
    ok_button_padding: str


def _session_summary_style_tokens() -> _SessionSummaryStyleTokens:
    """Assemble catalog strings for the session-summary QSS template.

    Returns:
        Keyword bundle for
        ``SESSION_SUMMARY_STYLE_TEMPLATE_DINAMIC_POSTFIX_GXXL``.
    """
    return _SessionSummaryStyleTokens(
        session_summary_dialog_selector=(
            SESSION_SUMMARY_DIALOG_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        session_summary_header_selector=(
            SESSION_SUMMARY_HEADER_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        session_summary_title_selector=(
            SESSION_SUMMARY_TITLE_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_stats_row_selector=(
            SUMMARY_STATS_ROW_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_chip_ok_selector=SUMMARY_CHIP_OK_SELECTOR_DINAMIC_POSTFIX_GXXL,
        summary_chip_bad_selector=(
            SUMMARY_CHIP_BAD_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_chip_neutral_selector=(
            SUMMARY_CHIP_NEUTRAL_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_chip_warn_selector=(
            SUMMARY_CHIP_WARN_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_chip_value_selector=(
            SUMMARY_CHIP_VALUE_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_chip_label_selector=(
            SUMMARY_CHIP_LABEL_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_success_banner_selector=(
            SUMMARY_SUCCESS_BANNER_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_success_text_selector=(
            SUMMARY_SUCCESS_TEXT_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_scroll_selector=SUMMARY_SCROLL_SELECTOR_DINAMIC_POSTFIX_GXXL,
        summary_scroll_viewport_selector=(
            SUMMARY_SCROLL_VIEWPORT_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_list_host_selector=(
            SUMMARY_LIST_HOST_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_task_row_selector=(
            SUMMARY_TASK_ROW_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_mark_ok_selector=SUMMARY_MARK_OK_SELECTOR_DINAMIC_POSTFIX_GXXL,
        summary_mark_bad_selector=(
            SUMMARY_MARK_BAD_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_mark_pending_selector=(
            SUMMARY_MARK_PENDING_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_mark_idle_selector=(
            SUMMARY_MARK_IDLE_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_task_num_selector=(
            SUMMARY_TASK_NUM_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_task_title_selector=(
            SUMMARY_TASK_TITLE_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_row_actions_selector=(
            SUMMARY_ROW_ACTIONS_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_icon_button_selector=(
            SUMMARY_ICON_BUTTON_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_icon_button_hover_selector=(
            SUMMARY_ICON_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_foot_bar_selector=(
            SUMMARY_FOOT_BAR_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_dialog_ok_button_selector=(
            SUMMARY_DIALOG_OK_BUTTON_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_dialog_ok_button_hover_selector=(
            SUMMARY_DIALOG_OK_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_ok_button_selector=(
            SUMMARY_OK_BUTTON_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        summary_ok_button_hover_selector=(
            SUMMARY_OK_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_GXXL
        ),
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_GXXL,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_GXXL,
        color_text_secondary=COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_GXXL,
        color_border_soft=COLOR_BORDER_SOFT_DINAMIC_POSTFIX_GXXL,
        color_header_background=COLOR_HEADER_BACKGROUND_DINAMIC_POSTFIX_GXXL,
        color_header_border=COLOR_HEADER_BORDER_DINAMIC_POSTFIX_GXXL,
        color_success_border=COLOR_SUCCESS_BORDER_DINAMIC_POSTFIX_GXXL,
        color_success_chip_background=(
            COLOR_SUCCESS_CHIP_BACKGROUND_DINAMIC_POSTFIX_GXXL
        ),
        color_success_banner_background=(
            COLOR_SUCCESS_BANNER_BACKGROUND_DINAMIC_POSTFIX_GXXL
        ),
        color_success_text=COLOR_SUCCESS_TEXT_DINAMIC_POSTFIX_GXXL,
        color_danger_border=COLOR_DANGER_BORDER_DINAMIC_POSTFIX_GXXL,
        color_danger_chip_background=(
            COLOR_DANGER_CHIP_BACKGROUND_DINAMIC_POSTFIX_GXXL
        ),
        color_danger_text=COLOR_DANGER_TEXT_DINAMIC_POSTFIX_GXXL,
        color_neutral_background=(
            COLOR_NEUTRAL_BACKGROUND_DINAMIC_POSTFIX_GXXL
        ),
        color_warn_chip_background=(
            COLOR_WARN_CHIP_BACKGROUND_DINAMIC_POSTFIX_GXXL
        ),
        color_warn_chip_border=COLOR_WARN_CHIP_BORDER_DINAMIC_POSTFIX_GXXL,
        color_warn_text=COLOR_WARN_TEXT_DINAMIC_POSTFIX_GXXL,
        color_idle_text=COLOR_IDLE_TEXT_DINAMIC_POSTFIX_GXXL,
        color_scroll_background=COLOR_SCROLL_BACKGROUND_DINAMIC_POSTFIX_GXXL,
        color_icon_button_hover=COLOR_ICON_BUTTON_HOVER_DINAMIC_POSTFIX_GXXL,
        color_accent=COLOR_ACCENT_DINAMIC_POSTFIX_GXXL,
        color_accent_hover=COLOR_ACCENT_HOVER_DINAMIC_POSTFIX_GXXL,
        font_family_mono=FONT_FAMILY_MONO_DINAMIC_POSTFIX_GXXL,
        background_transparent=BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_GXXL,
        border_none=BORDER_NONE_DINAMIC_POSTFIX_GXXL,
        border_width_1_px=BORDER_WIDTH_1_PX_DINAMIC_POSTFIX_GXXL,
        font_size_22_px=FONT_SIZE_22_PX_DINAMIC_POSTFIX_GXXL,
        font_size_16_px=FONT_SIZE_16_PX_DINAMIC_POSTFIX_GXXL,
        font_size_14_px=FONT_SIZE_14_PX_DINAMIC_POSTFIX_GXXL,
        font_size_13_px=FONT_SIZE_13_PX_DINAMIC_POSTFIX_GXXL,
        font_size_12_px=FONT_SIZE_12_PX_DINAMIC_POSTFIX_GXXL,
        font_size_11_px=FONT_SIZE_11_PX_DINAMIC_POSTFIX_GXXL,
        font_weight_700=FONT_WEIGHT_700_DINAMIC_POSTFIX_GXXL,
        font_weight_600=FONT_WEIGHT_600_DINAMIC_POSTFIX_GXXL,
        size_200_px=SIZE_200_PX_DINAMIC_POSTFIX_GXXL,
        size_168_px=SIZE_168_PX_DINAMIC_POSTFIX_GXXL,
        size_72_px=SIZE_72_PX_DINAMIC_POSTFIX_GXXL,
        size_44_px=SIZE_44_PX_DINAMIC_POSTFIX_GXXL,
        size_40_px=SIZE_40_PX_DINAMIC_POSTFIX_GXXL,
        size_36_px=SIZE_36_PX_DINAMIC_POSTFIX_GXXL,
        size_34_px=SIZE_34_PX_DINAMIC_POSTFIX_GXXL,
        size_12_px=SIZE_12_PX_DINAMIC_POSTFIX_GXXL,
        size_11_px=SIZE_11_PX_DINAMIC_POSTFIX_GXXL,
        size_10_px=SIZE_10_PX_DINAMIC_POSTFIX_GXXL,
        size_8_px=SIZE_8_PX_DINAMIC_POSTFIX_GXXL,
        ok_button_dialog_padding=(
            OK_BUTTON_DIALOG_PADDING_DINAMIC_POSTFIX_GXXL
        ),
        ok_button_padding=OK_BUTTON_PADDING_DINAMIC_POSTFIX_GXXL,
    )


def session_summary_styles() -> str:
    """Render QSS for stats chips, task rows, and summary dialog chrome.

    Returns:
        Stylesheet fragment for the modal that shows session results.
    """
    return SESSION_SUMMARY_STYLE_TEMPLATE_DINAMIC_POSTFIX_GXXL.format(
        **_session_summary_style_tokens()
    )
