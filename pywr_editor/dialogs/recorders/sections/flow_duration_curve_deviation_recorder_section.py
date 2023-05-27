from pywr_editor.form import FieldConfig, Validation, ValuesAndExternalDataWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_flow_duration_curve_recorder_section import (
    AbstractFlowDurationCurveRecorderSection,
)

"""
 NOTES:
 1) the recorder accepts the scenario name as argument, but this
    is not used in the load() function with JSON models, therefore
    the field is not added to the section.
 2) the target FDC can be a NxM array where N is the number of percentiles
    and M the number of scenario combinations. However for simplicity
    only a single target is supported for all scenarios (size Nx1).
 3) the size of the FDC targets must match the number of percentiles.
    This is not checked, because the targets may come from an external
    file.
"""


class FlowDurationCurveDeviationRecorderSection(
    AbstractFlowDurationCurveRecorderSection
):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a FlowDurationCurveDeviationRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        lower_fdc = form.field_value("lower_target_fdc")
        upper_fdc = form.field_value("upper_target_fdc")
        # multi dimensional array not supported when targets are lists
        if (
            lower_fdc
            and isinstance(lower_fdc, list)  # target may be a dict for external data
            and isinstance(lower_fdc[0], list)
        ):
            lower_fdc = None
        if upper_fdc and isinstance(upper_fdc, list) and isinstance(upper_fdc[0], list):
            lower_fdc = None
        section_fields = [
            FieldConfig(
                name="lower_target_fdc",
                label="Lower target FDC",
                value=lower_fdc,
                field_type=ValuesAndExternalDataWidget,
                field_args={
                    "show_row_numbers": True,
                    "row_number_label": "Percentile index",
                    "variable_names": "Value",
                },
                validate_fun=self.check_fdc_targets,
                help_text="The FDC to use as lower target. If omitted, the "
                "deviation from the this target is recorded as zero",
            ),
            FieldConfig(
                name="upper_target_fdc",
                label="Upper Upper FDC",
                value=upper_fdc,
                field_type=ValuesAndExternalDataWidget,
                field_args={
                    "show_row_numbers": True,
                    "row_number_label": "Percentile index",
                    "variable_names": "Value",
                },
                validate_fun=self.check_fdc_targets,
                help_text="The FDC to use as upper target. If omitted, the "
                "deviation from the this target is recorded as zero",
            ),
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=section_fields,
            additional_fdc_help_text=". The recorder then stores the deviation "
            "of the FDC from the lower and upper target FDCs provided below. "
            "The deviation is defined as the worst (or max) deviation of the "
            "upper and lower targets. "
            "The deviation is positive when the FDC is above the upper target, "
            "negative when below the lower target and zero when in-between both "
            "the target FDCs",
        )

    def check_fdc_targets(
        self, name: str, label: str, target_values: dict[str, float]
    ) -> Validation:
        """
        Checks that, if the FDC target is provided as values, the number of values
        must match the number of percentiles.
        :param name: The form name.
        :param label: The form label.
        :param target_values:The values of the FDC target.
        :return: The validation instance.
        """
        percentiles = self.form.find_field("percentiles").value()["values"]
        target = self.form.find_field(name).widget
        if (
            percentiles
            and len(target_values) > 0  # target is optional
            and target.combo_box.currentText() == target.labels_map["values"]
            and len(target_values) != len(percentiles)
        ):
            return Validation(
                "The number of target values must match the number of percentiles"
            )

        return Validation()
