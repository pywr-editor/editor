from math import pi

from pywr_editor.form import FieldConfig, FloatWidget, FormSection, TableValuesWidget

from ..parameter_dialog_form import ParameterDialogForm


class AnnualHarmonicSeriesParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a AnnualHarmonicSeriesParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="mean",
                        field_type=FloatWidget,
                        value=self.form.field_value("mean"),
                        allow_empty=False,
                        help_text="The mean value of the series corresponding to the "
                        "zeroth harmonic",
                    ),
                    FieldConfig(
                        name="amplitudes_phases",
                        field_type=TableValuesWidget,
                        value={
                            "amplitudes": self.form.field_value("amplitudes"),
                            "phases": self.form.field_value("phases"),
                        },
                        field_args={
                            "min_total_values": 1,
                            "scientific_notation": True,
                        },
                        help_text="A list of amplitudes and phases to use for the "
                        "harmonic cosine functions",
                    ),
                ],
                self.form.optimisation_config_group_name: [
                    self.form.is_variable_field,
                    FieldConfig(
                        name="mean_lower_bounds",
                        field_type=FloatWidget,
                        value=self.form.field_value("mean_lower_bounds"),
                        help_text="The lower bound for the mean during optimisation",
                    ),
                    FieldConfig(
                        name="mean_upper_bounds",
                        field_type=FloatWidget,
                        value=self.form.field_value("mean_upper_bounds"),
                        help_text="The upper bound for the mean during optimisation",
                    ),
                    FieldConfig(
                        name="amplitude_lower_bounds",
                        field_type=FloatWidget,
                        field_args={"min_value": 0},
                        value=self.form.field_value("amplitude_lower_bounds"),
                        help_text="The lower bound for the amplitude during "
                        "optimisation. The constrain is the same for all harmonic "
                        "cosine function",
                    ),
                    FieldConfig(
                        name="amplitude_upper_bounds",
                        field_type=FloatWidget,
                        field_args={"min_value": 0},
                        value=self.form.field_value("amplitude_upper_bounds"),
                        help_text="The upper bound for the amplitude during "
                        "optimisation. The constrain is the same for all harmonic "
                        "cosine function",
                    ),
                    FieldConfig(
                        name="phase_lower_bounds",
                        field_type=FloatWidget,
                        field_args={"min_value": 0},
                        value=self.form.field_value("phase_lower_bounds"),
                        help_text="The lower bound for the phase during optimisation. "
                        "The constrain is the same for all harmonic cosine function",
                    ),
                    FieldConfig(
                        name="phase_upper_bounds",
                        field_type=FloatWidget,
                        field_args={"max_value": 2 * pi},
                        value=self.form.field_value("phase_upper_bounds"),
                        help_text="The upper bound for the phase during optimisation. "
                        "The constrain is the same for all harmonic cosine function",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del self.fields_[self.form.optimisation_config_group_name]

    def filter(self, form_data):
        """
        Unpacks the "amplitudes_phases" field.
        :param form_data: The form data.
        :return: None
        """
        # field is mandatory
        for var_name, var_values in form_data["amplitudes_phases"].items():
            form_data[var_name] = var_values
        del form_data["amplitudes_phases"]
