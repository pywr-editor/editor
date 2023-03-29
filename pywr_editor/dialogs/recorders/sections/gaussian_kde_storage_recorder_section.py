from pywr_editor.form import (
    FloatWidget,
    FormValidation,
    ResampleAggFrequencyWidget,
    ResampleAggFunctionWidget,
    StoragePickerWidget,
)

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class GaussianKDEStorageRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a GaussianKDEStorageRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "node",
                "label": "Storage node",
                "field_type": StoragePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "The recorder calculates the kernel density estimation "
                + "(KDE) of the storage node using the values from all scenarios. "
                + "The recorder then estimates and stores the probability of being at "
                + "or below the target volume provided below",
            },
            {
                "name": "target_volume_pc",
                "label": "Target volume",
                "field_type": FloatWidget,
                "field_args": {"min_value": 0, "max_value": 1},
                "allow_empty": False,
                "validate_fun": self.check_volume_pc,
                "value": form.get_recorder_dict_value("target_volume_pc"),
                "help_text": "The target volume (between 0 and 1) to use to calculate "
                + "the storage probability",
            },
            {
                "name": "num_pdf",
                "label": "Number of PDF points",
                "field_type": "integer",
                "default_value": 101,
                "value": form.get_recorder_dict_value("num_pdf"),
                "help_text": "The number of points to use in the PDF estimate. Default "
                + "to 101",
            },
            {
                "name": "use_reflection",
                "label": "Reflection",
                "field_type": "boolean",
                "default_value": True,
                "value": form.get_recorder_dict_value("use_reflection"),
                "help_text": "Apply reflection at the border. This prevents the "
                + "kernel density from being underestimated in the proximity of "
                "the lower and upper bound (i.e. 0% and 100% volume)",
            },
        ]
        additional_sections = {
            "Resampling": [
                {
                    "name": "resample_freq",
                    "label": "Aggregating frequency",
                    "field_type": ResampleAggFrequencyWidget,
                    "value": form.get_recorder_dict_value("resample_freq"),
                    "validate_fun": self.check_resample_freq,
                    "help_text": "Group the storage timeseries using the Pandas' "
                    + "frequency function. This is optional and must used in "
                    + "conjunction with the field below",
                },
                {
                    "name": "resample_func",
                    "label": "Aggregating function",
                    "field_type": ResampleAggFunctionWidget,
                    "value": form.get_recorder_dict_value("resample_func"),
                    "validate_fun": self.check_resample_func,
                    "help_text": "Apply the aggregation function to each group of "
                    + "data before calculating the KDE. Optional",
                },
            ]
        }
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            additional_sections=additional_sections,
            log_name=self.__class__.__name__,
        )

    @staticmethod
    def check_volume_pc(
        name: str, label: str, value: float | None
    ) -> FormValidation:
        """
        Checks that the storage is between 0 and 1.
        :param name: The field name.
        :param label: The field name.
        :param value: The storage.
        :return: The form validation instance.
        :return:
        """
        if value and not (0 <= value <= 1):
            return FormValidation(
                validation=False,
                error_message="The storage must be a number between 0 and 1",
            )
        return FormValidation(validation=True)

    def check_resample_freq(
        self, name: str, label: str, resample_freq: str | None
    ) -> FormValidation:
        """
        Checks that "resample_freq" field is set if the "resample_func" is provided.
        :param name: The field name.
        :param label: The field name.
        :param resample_freq: The aggregation frequency value.
        :return: The form validation instance.
        :return:
        """
        resample_func = self.form.find_field_by_name("resample_func").value()
        if resample_func is not None and resample_freq is None:
            return FormValidation(
                validation=False,
                error_message="You must provided a value when you set the "
                + "'Aggregating function' field below",
            )

        return FormValidation(validation=True)

    def check_resample_func(
        self, name: str, label: str, resample_func: str | None
    ) -> FormValidation:
        """
        Checks that "resample_func" field is set if the "resample_freq" is provided.
        :param name: The field name.
        :param label: The field name.
        :param resample_func: The aggregation function value.
        :return: The form validation instance.
        :return:
        """
        resample_freq = self.form.find_field_by_name("resample_freq").value()
        if resample_freq is not None and resample_func is None:
            return FormValidation(
                validation=False,
                error_message="You must provided a value when you set the "
                + "'Aggregating frequency' field above",
            )

        return FormValidation(validation=True)
