from pywr_editor.form import (
    FieldConfig,
    StoragePickerWidget,
    ValuesAndExternalDataWidget,
)

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_interpolation_section import AbstractInterpolationSection


class InterpolatedVolumeParameterSection(AbstractInterpolationSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a InterpolatedVolumeParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="node",
                        label="Storage node",
                        field_type=StoragePickerWidget,
                        value=self.form.field_value("node"),
                        help_text="This parameter returns an interpolated value using "
                        "the volume from the storage node provided above",
                    ),
                    FieldConfig(
                        name="volumes",
                        label="Known volumes",
                        field_type=ValuesAndExternalDataWidget,
                        field_args={"min_total_values": 2},
                        value=self.form.field_value("volumes"),
                        help_text="Provide the volumes or x coordinates of the data "
                        "points to use for the interpolation",
                    ),
                    FieldConfig(
                        name="values",
                        label="Known values",
                        field_type=ValuesAndExternalDataWidget,
                        field_args={"min_total_values": 2},
                        value=self.form.field_value("values"),
                        help_text="Provide the values or y coordinates of the data "
                        "points to use for the interpolation",
                    ),
                ],
                "Interpolation settings": self.interp_settings,
                "Miscellaneous": [self.form.comment],
            }
        )
