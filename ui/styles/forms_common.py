"""
This module produces a reusable QSS stylesheet fragment that
standardizes the look of forms, inputs, checkboxes, radio buttons,
apply buttons, and scrollbars across the application.

It works by gathering selector names, colors, sizes, radii, and spacing
values from a message catalog into a token dictionary, then
interpolating those tokens into a shared QSS template.

It contains a _FormsCommonStyleTokens TypedDict describing all template
placeholders, a _forms_common_style_tokens helper that returns a fully
populated mapping, and the public forms_common_styles function that
formats and returns the final stylesheet string.

Within the broader system, this fragment is included in the global app
stylesheet so that dialogs and settings panes share consistent form
styling and can be themed or localized via the underlying catalog
values.
"""

from __future__ import annotations

from typing import TypedDict

from messages import (
    APPLY_BUTTON_FONT_WEIGHT_DINAMIC_POSTFIX_BDOT,
    APPLY_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_BDOT,
    APPLY_BUTTON_MIN_HEIGHT_PX_DINAMIC_POSTFIX_BDOT,
    APPLY_BUTTON_RADIUS_PX_DINAMIC_POSTFIX_BDOT,
    APPLY_BUTTON_SELECTOR_DINAMIC_POSTFIX_BDOT,
    BORDER_WIDTH_PX_DINAMIC_POSTFIX_BDOT,
    CHECKBOX_CHECKED_SELECTOR_DINAMIC_POSTFIX_BDOT,
    CHECKBOX_INDICATOR_RADIUS_PX_DINAMIC_POSTFIX_BDOT,
    CHECKBOX_INDICATOR_SELECTOR_DINAMIC_POSTFIX_BDOT,
    CHECKBOX_SELECTOR_DINAMIC_POSTFIX_BDOT,
    COLOR_BORDER_ACCENT_DINAMIC_POSTFIX_BDOT,
    COLOR_BORDER_SOFT_DINAMIC_POSTFIX_BDOT,
    COLOR_BUTTON_HOVER_DINAMIC_POSTFIX_BDOT,
    COLOR_FORM_BACKGROUND_DINAMIC_POSTFIX_BDOT,
    COLOR_SCROLLBAR_HANDLE_DINAMIC_POSTFIX_BDOT,
    COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_BDOT,
    COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_BDOT,
    COLOR_WHITE_DINAMIC_POSTFIX_BDOT,
    CONTROL_SPACING_PX_DINAMIC_POSTFIX_BDOT,
    FONT_SIZE_12_PX_DINAMIC_POSTFIX_BDOT,
    FORMS_COMMON_STYLE_TEMPLATE_DINAMIC_POSTFIX_BDOT,
    INPUT_MIN_HEIGHT_PX_DINAMIC_POSTFIX_BDOT,
    INPUT_PADDING_SIDE_PX_DINAMIC_POSTFIX_BDOT,
    INPUT_RADIUS_PX_DINAMIC_POSTFIX_BDOT,
    MODE_RADIO_CHECKED_SELECTOR_DINAMIC_POSTFIX_BDOT,
    MODE_RADIO_INDICATOR_SELECTOR_DINAMIC_POSTFIX_BDOT,
    MODE_RADIO_SELECTOR_DINAMIC_POSTFIX_BDOT,
    PARAM_INPUT_FOCUS_SELECTOR_DINAMIC_POSTFIX_BDOT,
    PARAM_INPUT_SELECTOR_DINAMIC_POSTFIX_BDOT,
    PARAM_LABEL_LIGHT_SELECTOR_DINAMIC_POSTFIX_BDOT,
    PARAM_LABEL_SELECTOR_DINAMIC_POSTFIX_BDOT,
    RADIAL_GRADIENT_BACKGROUND_DINAMIC_POSTFIX_BDOT,
    RADIO_CHECKED_BORDER_WIDTH_PX_DINAMIC_POSTFIX_BDOT,
    RADIO_INDICATOR_RADIUS_PX_DINAMIC_POSTFIX_BDOT,
    RADIO_INDICATOR_SIZE_PX_DINAMIC_POSTFIX_BDOT,
    SCROLLBAR_HANDLE_MIN_HEIGHT_PX_DINAMIC_POSTFIX_BDOT,
    SCROLLBAR_HANDLE_VERTICAL_SELECTOR_DINAMIC_POSTFIX_BDOT,
    SCROLLBAR_RADIUS_PX_DINAMIC_POSTFIX_BDOT,
    SCROLLBAR_VERTICAL_SELECTOR_DINAMIC_POSTFIX_BDOT,
    SCROLLBAR_WIDTH_PX_DINAMIC_POSTFIX_BDOT,
)


class _FormsCommonStyleTokens(TypedDict):
    """Placeholders for :data:`FORMS_COMMON_STYLE_TEMPLATE_…`."""

    param_label_light_selector: str
    param_label_selector: str
    param_input_selector: str
    param_input_focus_selector: str
    mode_radio_selector: str
    mode_radio_indicator_selector: str
    mode_radio_checked_selector: str
    checkbox_selector: str
    checkbox_indicator_selector: str
    checkbox_checked_selector: str
    apply_button_selector: str
    apply_button_hover_selector: str
    scrollbar_vertical_selector: str
    scrollbar_handle_vertical_selector: str
    color_white: str
    color_text_primary: str
    color_text_secondary: str
    color_border_soft: str
    color_border_accent: str
    color_form_background: str
    color_button_hover: str
    color_scrollbar_handle: str
    font_size_12_px: str
    input_min_height_px: str
    input_radius_px: str
    input_padding_side_px: str
    radio_indicator_size_px: str
    radio_indicator_radius_px: str
    checkbox_indicator_radius_px: str
    apply_button_min_height_px: str
    apply_button_radius_px: str
    scrollbar_width_px: str
    scrollbar_radius_px: str
    scrollbar_handle_min_height_px: str
    radio_checked_border_width_px: str
    border_width_px: str
    apply_button_font_weight: str
    control_spacing_px: str
    radial_gradient_background: str


def _forms_common_style_tokens() -> _FormsCommonStyleTokens:
    """Build the token map for the shared forms QSS template.

    Returns:
        Keyword arguments for
        ``FORMS_COMMON_STYLE_TEMPLATE_DINAMIC_POSTFIX_BDOT``.
    """
    return _FormsCommonStyleTokens(
        param_label_light_selector=(
            PARAM_LABEL_LIGHT_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        param_label_selector=PARAM_LABEL_SELECTOR_DINAMIC_POSTFIX_BDOT,
        param_input_selector=PARAM_INPUT_SELECTOR_DINAMIC_POSTFIX_BDOT,
        param_input_focus_selector=(
            PARAM_INPUT_FOCUS_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        mode_radio_selector=MODE_RADIO_SELECTOR_DINAMIC_POSTFIX_BDOT,
        mode_radio_indicator_selector=(
            MODE_RADIO_INDICATOR_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        mode_radio_checked_selector=(
            MODE_RADIO_CHECKED_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        checkbox_selector=CHECKBOX_SELECTOR_DINAMIC_POSTFIX_BDOT,
        checkbox_indicator_selector=(
            CHECKBOX_INDICATOR_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        checkbox_checked_selector=(
            CHECKBOX_CHECKED_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        apply_button_selector=APPLY_BUTTON_SELECTOR_DINAMIC_POSTFIX_BDOT,
        apply_button_hover_selector=(
            APPLY_BUTTON_HOVER_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        scrollbar_vertical_selector=(
            SCROLLBAR_VERTICAL_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        scrollbar_handle_vertical_selector=(
            SCROLLBAR_HANDLE_VERTICAL_SELECTOR_DINAMIC_POSTFIX_BDOT
        ),
        color_white=COLOR_WHITE_DINAMIC_POSTFIX_BDOT,
        color_text_primary=COLOR_TEXT_PRIMARY_DINAMIC_POSTFIX_BDOT,
        color_text_secondary=COLOR_TEXT_SECONDARY_DINAMIC_POSTFIX_BDOT,
        color_border_soft=COLOR_BORDER_SOFT_DINAMIC_POSTFIX_BDOT,
        color_border_accent=COLOR_BORDER_ACCENT_DINAMIC_POSTFIX_BDOT,
        color_form_background=COLOR_FORM_BACKGROUND_DINAMIC_POSTFIX_BDOT,
        color_button_hover=COLOR_BUTTON_HOVER_DINAMIC_POSTFIX_BDOT,
        color_scrollbar_handle=COLOR_SCROLLBAR_HANDLE_DINAMIC_POSTFIX_BDOT,
        font_size_12_px=FONT_SIZE_12_PX_DINAMIC_POSTFIX_BDOT,
        input_min_height_px=INPUT_MIN_HEIGHT_PX_DINAMIC_POSTFIX_BDOT,
        input_radius_px=INPUT_RADIUS_PX_DINAMIC_POSTFIX_BDOT,
        input_padding_side_px=INPUT_PADDING_SIDE_PX_DINAMIC_POSTFIX_BDOT,
        radio_indicator_size_px=RADIO_INDICATOR_SIZE_PX_DINAMIC_POSTFIX_BDOT,
        radio_indicator_radius_px=(
            RADIO_INDICATOR_RADIUS_PX_DINAMIC_POSTFIX_BDOT
        ),
        checkbox_indicator_radius_px=(
            CHECKBOX_INDICATOR_RADIUS_PX_DINAMIC_POSTFIX_BDOT
        ),
        apply_button_min_height_px=(
            APPLY_BUTTON_MIN_HEIGHT_PX_DINAMIC_POSTFIX_BDOT
        ),
        apply_button_radius_px=APPLY_BUTTON_RADIUS_PX_DINAMIC_POSTFIX_BDOT,
        scrollbar_width_px=SCROLLBAR_WIDTH_PX_DINAMIC_POSTFIX_BDOT,
        scrollbar_radius_px=SCROLLBAR_RADIUS_PX_DINAMIC_POSTFIX_BDOT,
        scrollbar_handle_min_height_px=(
            SCROLLBAR_HANDLE_MIN_HEIGHT_PX_DINAMIC_POSTFIX_BDOT
        ),
        radio_checked_border_width_px=(
            RADIO_CHECKED_BORDER_WIDTH_PX_DINAMIC_POSTFIX_BDOT
        ),
        border_width_px=BORDER_WIDTH_PX_DINAMIC_POSTFIX_BDOT,
        apply_button_font_weight=(
            APPLY_BUTTON_FONT_WEIGHT_DINAMIC_POSTFIX_BDOT
        ),
        control_spacing_px=CONTROL_SPACING_PX_DINAMIC_POSTFIX_BDOT,
        radial_gradient_background=(
            RADIAL_GRADIENT_BACKGROUND_DINAMIC_POSTFIX_BDOT
        ),
    )


def forms_common_styles() -> str:
    """Render shared form, checkbox, radio, apply button, and scrollbar
    QSS.

    Returns:
        One stylesheet fragment reused by settings and modal dialogs.
    """
    return FORMS_COMMON_STYLE_TEMPLATE_DINAMIC_POSTFIX_BDOT.format(
        **_forms_common_style_tokens()
    )
