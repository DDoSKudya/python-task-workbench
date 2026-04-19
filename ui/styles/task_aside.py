"""
This module generates the QSS stylesheet fragment used to style the task
description sidebar, including its scroll area, status banner, section
headers, and monospace code blocks.

It works by defining a _TaskAsideStyleTokens TypedDict listing all
placeholders required by a QSS template, filling that mapping with
selectors, colors, font settings, spacings, and other metrics from a
message catalog, and interpolating them into
TASK_ASIDE_STYLE_TEMPLATE_….

It contains the token type, the _task_aside_style_tokens helper that
assembles a complete dictionary of sidebar style tokens, and the public
task_aside_styles function that formats and returns the final stylesheet
text.

Within the broader system, this fragment is combined with other QSS
sections so that the task-aside column has a consistent, themeable
appearance for titles, constraints, code previews, and pass/fail banners
aligned with the rest of the UI.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    ACCENT_BAR_MUTED_SELECTOR_DINAMIC_POSTFIX_NMVA,
    ACCENT_BAR_SELECTOR_DINAMIC_POSTFIX_NMVA,
    BORDER_NONE_DINAMIC_POSTFIX_NMVA,
    BORDER_WIDTH_1_PX_DINAMIC_POSTFIX_NMVA,
    COLOR_ACCENT_DINAMIC_POSTFIX_NMVA,
    COLOR_BORDER_SOFT_DINAMIC_POSTFIX_NMVA,
    COLOR_SELECTION_DINAMIC_POSTFIX_NMVA,
    COLOR_STATUS_BAD_DINAMIC_POSTFIX_NMVA,
    COLOR_STATUS_OK_DINAMIC_POSTFIX_NMVA,
    COLOR_SURFACE_MUTED_DINAMIC_POSTFIX_NMVA,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_NMVA,
    COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_NMVA,
    COLOR_WHITE_DINAMIC_POSTFIX_NMVA,
    CONSTRAINTS_SELECTOR_DINAMIC_POSTFIX_NMVA,
    FONT_FAMILY_MONO_DINAMIC_POSTFIX_NMVA,
    FONT_SIZE_11_PX_DINAMIC_POSTFIX_NMVA,
    FONT_SIZE_12_PX_DINAMIC_POSTFIX_NMVA,
    FONT_SIZE_13_PX_DINAMIC_POSTFIX_NMVA,
    FONT_WEIGHT_500_DINAMIC_POSTFIX_NMVA,
    FONT_WEIGHT_600_DINAMIC_POSTFIX_NMVA,
    LETTER_SPACING_EM_DINAMIC_POSTFIX_NMVA,
    LINE_HEIGHT_STANDARD_DINAMIC_POSTFIX_NMVA,
    MONO_BLOCK_SELECTOR_DINAMIC_POSTFIX_NMVA,
    SECTION_ACCENT_TITLE_SELECTOR_DINAMIC_POSTFIX_NMVA,
    SIZE_2_PX_DINAMIC_POSTFIX_NMVA,
    SIZE_4_PX_DINAMIC_POSTFIX_NMVA,
    SIZE_6_PX_DINAMIC_POSTFIX_NMVA,
    SIZE_10_PX_DINAMIC_POSTFIX_NMVA,
    SIZE_12_PX_DINAMIC_POSTFIX_NMVA,
    SIZE_16_PX_DINAMIC_POSTFIX_NMVA,
    STATUS_BANNER_BAD_SELECTOR_DINAMIC_POSTFIX_NMVA,
    STATUS_BANNER_OK_SELECTOR_DINAMIC_POSTFIX_NMVA,
    STATUS_BANNER_PADDING_DINAMIC_POSTFIX_NMVA,
    STATUS_BANNER_SELECTOR_DINAMIC_POSTFIX_NMVA,
    STATUS_BANNER_TEXT_SELECTOR_DINAMIC_POSTFIX_NMVA,
    TASK_ASIDE_INNER_SELECTOR_DINAMIC_POSTFIX_NMVA,
    TASK_ASIDE_SCROLL_SELECTOR_DINAMIC_POSTFIX_NMVA,
    TASK_ASIDE_STYLE_TEMPLATE_DINAMIC_POSTFIX_NMVA,
    TASK_BODY_SELECTOR_DINAMIC_POSTFIX_NMVA,
    TEXT_TRANSFORM_UPPERCASE_DINAMIC_POSTFIX_NMVA,
)


class _TaskAsideStyleTokens(TypedDict):
    """Keyword fields for :data:`TASK_ASIDE_STYLE_TEMPLATE_…`."""

    task_aside_scroll_selector: str
    task_aside_inner_selector: str
    section_accent_title_selector: str
    accent_bar_selector: str
    accent_bar_muted_selector: str
    task_body_selector: str
    status_banner_selector: str
    status_banner_ok_selector: str
    status_banner_bad_selector: str
    status_banner_text_selector: str
    mono_block_selector: str
    constraints_selector: str
    color_white: str
    color_text_primary: str
    color_text_secondary: str
    color_border_soft: str
    color_accent: str
    color_status_ok: str
    color_status_bad: str
    color_surface_muted: str
    color_selection: str
    font_family_mono: str
    border_none: str
    text_transform_uppercase: str
    border_width_1_px: str
    font_size_13_px: str
    font_size_12_px: str
    font_size_11_px: str
    font_weight_600: str
    font_weight_500: str
    size_16_px: str
    size_12_px: str
    size_10_px: str
    size_6_px: str
    size_4_px: str
    size_2_px: str
    line_height_standard: str
    letter_spacing_em: str
    status_banner_padding: str


def _task_aside_style_tokens() -> _TaskAsideStyleTokens:
    """Assemble catalog strings for the task-aside QSS template.

    Returns:
        Keyword bundle for
        ``TASK_ASIDE_STYLE_TEMPLATE_DINAMIC_POSTFIX_NMVA``.
    """
    return _TaskAsideStyleTokens(
        task_aside_scroll_selector=(
            TASK_ASIDE_SCROLL_SELECTOR_DINAMIC_POSTFIX_NMVA
        ),
        task_aside_inner_selector=(
            TASK_ASIDE_INNER_SELECTOR_DINAMIC_POSTFIX_NMVA
        ),
        section_accent_title_selector=(
            SECTION_ACCENT_TITLE_SELECTOR_DINAMIC_POSTFIX_NMVA
        ),
        accent_bar_selector=ACCENT_BAR_SELECTOR_DINAMIC_POSTFIX_NMVA,
        accent_bar_muted_selector=(
            ACCENT_BAR_MUTED_SELECTOR_DINAMIC_POSTFIX_NMVA
        ),
        task_body_selector=TASK_BODY_SELECTOR_DINAMIC_POSTFIX_NMVA,
        status_banner_selector=STATUS_BANNER_SELECTOR_DINAMIC_POSTFIX_NMVA,
        status_banner_ok_selector=(
            STATUS_BANNER_OK_SELECTOR_DINAMIC_POSTFIX_NMVA
        ),
        status_banner_bad_selector=(
            STATUS_BANNER_BAD_SELECTOR_DINAMIC_POSTFIX_NMVA
        ),
        status_banner_text_selector=(
            STATUS_BANNER_TEXT_SELECTOR_DINAMIC_POSTFIX_NMVA
        ),
        mono_block_selector=MONO_BLOCK_SELECTOR_DINAMIC_POSTFIX_NMVA,
        constraints_selector=CONSTRAINTS_SELECTOR_DINAMIC_POSTFIX_NMVA,
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_NMVA,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_NMVA,
        color_text_secondary=COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_NMVA,
        color_border_soft=COLOR_BORDER_SOFT_DINAMIC_POSTFIX_NMVA,
        color_accent=COLOR_ACCENT_DINAMIC_POSTFIX_NMVA,
        color_status_ok=COLOR_STATUS_OK_DINAMIC_POSTFIX_NMVA,
        color_status_bad=COLOR_STATUS_BAD_DINAMIC_POSTFIX_NMVA,
        color_surface_muted=COLOR_SURFACE_MUTED_DINAMIC_POSTFIX_NMVA,
        color_selection=COLOR_SELECTION_DINAMIC_POSTFIX_NMVA,
        font_family_mono=FONT_FAMILY_MONO_DINAMIC_POSTFIX_NMVA,
        border_none=BORDER_NONE_DINAMIC_POSTFIX_NMVA,
        text_transform_uppercase=(
            TEXT_TRANSFORM_UPPERCASE_DINAMIC_POSTFIX_NMVA
        ),
        border_width_1_px=BORDER_WIDTH_1_PX_DINAMIC_POSTFIX_NMVA,
        font_size_13_px=FONT_SIZE_13_PX_DINAMIC_POSTFIX_NMVA,
        font_size_12_px=FONT_SIZE_12_PX_DINAMIC_POSTFIX_NMVA,
        font_size_11_px=FONT_SIZE_11_PX_DINAMIC_POSTFIX_NMVA,
        font_weight_600=FONT_WEIGHT_600_DINAMIC_POSTFIX_NMVA,
        font_weight_500=FONT_WEIGHT_500_DINAMIC_POSTFIX_NMVA,
        size_16_px=SIZE_16_PX_DINAMIC_POSTFIX_NMVA,
        size_12_px=SIZE_12_PX_DINAMIC_POSTFIX_NMVA,
        size_10_px=SIZE_10_PX_DINAMIC_POSTFIX_NMVA,
        size_6_px=SIZE_6_PX_DINAMIC_POSTFIX_NMVA,
        size_4_px=SIZE_4_PX_DINAMIC_POSTFIX_NMVA,
        size_2_px=SIZE_2_PX_DINAMIC_POSTFIX_NMVA,
        line_height_standard=LINE_HEIGHT_STANDARD_DINAMIC_POSTFIX_NMVA,
        letter_spacing_em=LETTER_SPACING_EM_DINAMIC_POSTFIX_NMVA,
        status_banner_padding=STATUS_BANNER_PADDING_DINAMIC_POSTFIX_NMVA,
    )


def task_aside_styles() -> str:
    """Render QSS for scroll host, status banner, and mono blocks.

    Returns:
        Stylesheet fragment for the task description aside column.
    """
    return TASK_ASIDE_STYLE_TEMPLATE_DINAMIC_POSTFIX_NMVA.format(
        **_task_aside_style_tokens()
    )
