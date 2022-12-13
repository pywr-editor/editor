from .form_validation import FormValidation


def validate_percentile_field_section(
    name: str, label: str, value: float | list[float]
) -> FormValidation:
    """
    Checks that the percentiles are between 0 and 100.
    :param name: The field name.
    :param label: The field label.
    :param value: The field label.
    :return: The FormValidation instance.
    """
    # check that all numbers are between 0 and 100
    if isinstance(value, (int, float)) and not (0 <= value <= 100):
        return FormValidation(
            error_message="The percentile must be a number between 0 and 100",
            validation=False,
        )
    elif isinstance(value, list) and not all([0 <= p <= 100 for p in value]):
        return FormValidation(
            error_message="The percentiles must be numbers between 0 and 100",
            validation=False,
        )

    return FormValidation(validation=True)
