"""
This module generates the QSS stylesheet fragment for the main code
editor column, including the editor shell, line numbers, and
check-status label.

It works by pulling selector names, colors, font metrics, and layout
values from a message catalog, packaging them into a typed token
mapping, and interpolating them into a QSS template string.

It contains a _CenterEditorStyleTokens TypedDict describing all
placeholders required by the center-editor style template, a
_center_editor_style_tokens helper that returns a populated token dict,
and the public center_editor_styles function that formats and returns
the final QSS section.

Within the broader system, this module feeds into the global app
stylesheet assembly, ensuring the editor columns appearance is
consistent, themed, and driven entirely by catalog-configurable style
tokens.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_T9SZ,
    BORDER_NONE_DINAMIC_POSTFIX_T9SZ,
    CENTER_COLUMN_SELECTOR_DINAMIC_POSTFIX_T9SZ,
    CENTER_EDITOR_STYLE_TEMPLATE_DINAMIC_POSTFIX_T9SZ,
    CHECK_STATUS_FONT_WEIGHT_DINAMIC_POSTFIX_T9SZ,
    CHECK_STATUS_MIN_HEIGHT_PX_DINAMIC_POSTFIX_T9SZ,
    CHECK_STATUS_SELECTOR_DINAMIC_POSTFIX_T9SZ,
    CODE_EDITOR_SELECTOR_DINAMIC_POSTFIX_T9SZ,
    COLOR_BORDER_FOCUS_DINAMIC_POSTFIX_T9SZ,
    COLOR_BORDER_SOFT_DINAMIC_POSTFIX_T9SZ,
    COLOR_LINE_NUMBER_BACKGROUND_DINAMIC_POSTFIX_T9SZ,
    COLOR_LINE_NUMBER_TEXT_DINAMIC_POSTFIX_T9SZ,
    COLOR_SELECTION_DINAMIC_POSTFIX_T9SZ,
    COLOR_STATUS_TEXT_DINAMIC_POSTFIX_T9SZ,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_T9SZ,
    COLOR_WHITE_DINAMIC_POSTFIX_T9SZ,
    EDITOR_BORDER_WIDTH_PX_DINAMIC_POSTFIX_T9SZ,
    EDITOR_FONT_FAMILY_DINAMIC_POSTFIX_T9SZ,
    EDITOR_FONT_SIZE_PX_DINAMIC_POSTFIX_T9SZ,
    EDITOR_PAD_SELECTOR_DINAMIC_POSTFIX_T9SZ,
    EDITOR_PADDING_PX_DINAMIC_POSTFIX_T9SZ,
    EDITOR_RADIUS_PX_DINAMIC_POSTFIX_T9SZ,
    EDITOR_SHELL_FOCUSED_SELECTOR_DINAMIC_POSTFIX_T9SZ,
    EDITOR_SHELL_SELECTOR_DINAMIC_POSTFIX_T9SZ,
    LINE_NUMBER_AREA_SELECTOR_DINAMIC_POSTFIX_T9SZ,
)


class _CenterEditorStyleTokens(TypedDict):
    """Keyword arguments for :data:`CENTER_EDITOR_STYLE_TEMPLATE_…`."""

    center_column_selector: str
    editor_pad_selector: str
    editor_shell_selector: str
    editor_shell_focused_selector: str
    code_editor_selector: str
    line_number_area_selector: str
    check_status_selector: str
    color_white: str
    color_text_primary: str
    color_border_soft: str
    color_border_focus: str
    color_selection: str
    color_line_number_background: str
    color_line_number_text: str
    color_status_text: str
    background_transparent: str
    border_none: str
    editor_font_family: str
    editor_font_size_px: str
    editor_padding_px: str
    check_status_font_weight: str
    check_status_min_height_px: str
    editor_radius_px: str
    editor_border_width_px: str


def _center_editor_style_tokens() -> _CenterEditorStyleTokens:
    """Collect catalog values keyed for the center-column QSS template.

    Returns:
        All named placeholders required by
        ``CENTER_EDITOR_STYLE_TEMPLATE_DINAMIC_POSTFIX_T9SZ``.
    """
    return _CenterEditorStyleTokens(
        center_column_selector=CENTER_COLUMN_SELECTOR_DINAMIC_POSTFIX_T9SZ,
        editor_pad_selector=EDITOR_PAD_SELECTOR_DINAMIC_POSTFIX_T9SZ,
        editor_shell_selector=EDITOR_SHELL_SELECTOR_DINAMIC_POSTFIX_T9SZ,
        editor_shell_focused_selector=(
            EDITOR_SHELL_FOCUSED_SELECTOR_DINAMIC_POSTFIX_T9SZ
        ),
        code_editor_selector=CODE_EDITOR_SELECTOR_DINAMIC_POSTFIX_T9SZ,
        line_number_area_selector=(
            LINE_NUMBER_AREA_SELECTOR_DINAMIC_POSTFIX_T9SZ
        ),
        check_status_selector=CHECK_STATUS_SELECTOR_DINAMIC_POSTFIX_T9SZ,
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_T9SZ,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_T9SZ,
        color_border_soft=COLOR_BORDER_SOFT_DINAMIC_POSTFIX_T9SZ,
        color_border_focus=COLOR_BORDER_FOCUS_DINAMIC_POSTFIX_T9SZ,
        color_selection=COLOR_SELECTION_DINAMIC_POSTFIX_T9SZ,
        color_line_number_background=(
            COLOR_LINE_NUMBER_BACKGROUND_DINAMIC_POSTFIX_T9SZ
        ),
        color_line_number_text=COLOR_LINE_NUMBER_TEXT_DINAMIC_POSTFIX_T9SZ,
        color_status_text=COLOR_STATUS_TEXT_DINAMIC_POSTFIX_T9SZ,
        background_transparent=BACKGROUND_TRANSPARENT_DINAMIC_POSTFIX_T9SZ,
        border_none=BORDER_NONE_DINAMIC_POSTFIX_T9SZ,
        editor_font_family=EDITOR_FONT_FAMILY_DINAMIC_POSTFIX_T9SZ,
        editor_font_size_px=EDITOR_FONT_SIZE_PX_DINAMIC_POSTFIX_T9SZ,
        editor_padding_px=EDITOR_PADDING_PX_DINAMIC_POSTFIX_T9SZ,
        check_status_font_weight=CHECK_STATUS_FONT_WEIGHT_DINAMIC_POSTFIX_T9SZ,
        check_status_min_height_px=(
            CHECK_STATUS_MIN_HEIGHT_PX_DINAMIC_POSTFIX_T9SZ
        ),
        editor_radius_px=EDITOR_RADIUS_PX_DINAMIC_POSTFIX_T9SZ,
        editor_border_width_px=EDITOR_BORDER_WIDTH_PX_DINAMIC_POSTFIX_T9SZ,
    )


def center_editor_styles() -> str:
    """Render the QSS fragment for the code editor column.

    Returns:
        A single QSS document section: column shell, line numbers,
        editor, and check-status label styling.
    """
    return CENTER_EDITOR_STYLE_TEMPLATE_DINAMIC_POSTFIX_T9SZ.format(
        **_center_editor_style_tokens()
    )
