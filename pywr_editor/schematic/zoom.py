from typing import Literal


def units_to_factor(units: float) -> float:
    """
    Converts the scaling units to a scaling factor. Most mouse types work in steps of
    15 deg, in which the delta value is a multiple of 120 units (i.e. 120 units/8 = 15
    deg).
    :param units: The scaling unit.
    :return: The scaling factor.
    """
    return pow(2, -units / 240)


def get_scaling_factor(
    scroll_type: Literal["zoom-in", "zoom-out"], scroll_count: int = 1
) -> float:
    """
    Returns the scaling factor corresponding to one scroll motion. This corresponds to
    15 deg or 120 units.
    :param scroll_type: The scroll type (zoom_in or zoom_out). When zooming out the
    returned number is < 0, otherwise > 0.
    :param scroll_count: The number of scroll gestures. This is multiplied by the
    scroll angle or units.
    :return: The delta scaling factor.
    """
    if scroll_type == "zoom-out":
        sign = 1
    elif scroll_type == "zoom-in":
        sign = -1
    else:
        raise ValueError('scroll_type can only be "zoom-in" or "zoom-out"')

    return round(units_to_factor(scroll_count * sign * 120), 4)
