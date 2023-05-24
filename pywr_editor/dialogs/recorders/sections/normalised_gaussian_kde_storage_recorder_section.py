from pywr_editor.form import (
    FieldConfig,
    ResampleAggFrequencyWidget,
    ResampleAggFunctionWidget,
    StoragePickerWidget,
    Validation,
)

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class NormalisedGaussianKDEStorageRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a NormalisedGaussianKDEStorageRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            FieldConfig(
                name="node",
                label="Storage node",
                field_type=StoragePickerWidget,
                value=form.field_value("node"),
                help_text="The recorder calculates the normalised kernel density "
                "estimation (KDE) (between -1 and 1) of the storage node using "
                "the values from all scenarios. The recorder then estimates and "
                "stores the probability of being at or below zero",
            ),
            FieldConfig(
                name="num_pdf",
                label="Number of PDF points",
                field_type="integer",
                default_value=101,
                value=form.field_value("num_pdf"),
                help_text="The number of points to use in the PDF estimate. Default "
                "to 101",
            ),
            FieldConfig(
                name="use_reflection",
                label="Reflection",
                field_type="boolean",
                default_value=True,
                value=form.field_value("use_reflection"),
                help_text="Apply reflection at the border. This prevents the "
                "kernel density from being underestimated in the proximity of "
                "the lower and upper bound (i.e. -1 and 1)",
            ),
        ]
        additional_sections = {
            "Resampling": [
                FieldConfig(
                    name="resample_freq",
                    label="Aggregating frequency",
                    field_type=ResampleAggFrequencyWidget,
                    value=form.field_value("resample_freq"),
                    validate_fun=self.check_resample_freq,
                    help_text="Group the storage timeseries using the Pandas' "
                    "frequency function. This is optional and must used in "
                    "conjunction with the field below",
                ),
                FieldConfig(
                    name="resample_func",
                    label="Aggregating function",
                    field_type=ResampleAggFunctionWidget,
                    value=form.field_value("resample_func"),
                    validate_fun=self.check_resample_func,
                    help_text="Apply the aggregation function to each group of "
                    "data before calculating the KDE. Optional",
                ),
            ]
        }
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            additional_sections=additional_sections,
        )

    def check_resample_freq(
        self, name: str, label: str, resample_freq: str | None
    ) -> Validation:
        """
        Checks that "resample_freq" field is set if the "resample_func" is provided.
        :param name: The field name.
        :param label: The field name.
        :param resample_freq: The aggregation frequency value.
        :return: The form validation instance.
        :return:
        """
        resample_func = self.form.find_field("resample_func").value()
        if resample_func is not None and resample_freq is None:
            return Validation(
                "You must provided a value when you set the "
                "'Aggregating function' field below",
            )

        return Validation()

    def check_resample_func(
        self, name: str, label: str, resample_func: str | None
    ) -> Validation:
        """
        Checks that "resample_func" field is set if the "resample_freq" is provided.
        :param name: The field name.
        :param label: The field name.
        :param resample_func: The aggregation function value.
        :return: The form validation instance.
        :return:
        """
        resample_freq = self.form.find_field("resample_freq").value()
        if resample_freq is not None and resample_func is None:
            return Validation(
                "You must provided a value when you set the "
                "'Aggregating frequency' field above",
            )

        return Validation()
