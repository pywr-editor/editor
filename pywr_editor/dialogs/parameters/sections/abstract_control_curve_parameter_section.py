from functools import partial
from typing import Any

from pywr_editor.form import (
    ControlCurvesValuesSourceWidget,
    ControlCurvesWidget,
    FormSection,
    ParametersListPickerWidget,
    StoragePickerWidget,
    Validation,
    ValuesAndExternalDataWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm

"""
 Abstract class used for ControlCurveParameter
 and ControlCurveInterpolatedParameter
"""


class AbstractControlCurveParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict[str, Any],
        log_name: str,
        values_size_increment: int,
        additional_help_text: str = "",
    ):
        """
        Initialises the form section.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param log_name: The name of the log instance.
        :param values_size_increment: The size increment of the "values" and
        "parameters" list compared to the size of the "control_curves" list.
        If one is given, the size of "values" and "parameters" must equal the
        size of the "control_curves" list plus one.
        :param additional_help_text: A string to append to the storage node help text.
        Default to empty.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(log_name)
        self.additional_help_text = additional_help_text

        if values_size_increment <= 0:
            raise ValueError("values_size_increment can only be > 0")
        self.values_size_increment = values_size_increment

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": [
                {
                    "name": "storage_node",
                    "field_type": StoragePickerWidget,
                    "value": self.form.get_param_dict_value("storage_node"),
                    "help_text": "Use the storage from the node specified above to "
                    f"derive the parameter value{self.additional_help_text}",
                },
                # this is always mandatory
                {
                    # widget always returns a list of parameters
                    "name": "control_curves",
                    "field_type": ControlCurvesWidget,
                    "value": {
                        "control_curve": self.form.get_param_dict_value(
                            "control_curve"
                        ),
                        "control_curves": self.form.get_param_dict_value(
                            "control_curves"
                        ),
                    },
                    "help_text": "Sort the control curves by the highest to the "
                    "lowest. The parameter returns one of the values below "
                    "corresponding to the first control curve that is above the "
                    "node storage. If the storage is below all control curves, "
                    "the latest value is used",
                },
                {
                    "name": "values_source",
                    "field_type": ControlCurvesValuesSourceWidget,
                    "value": {
                        "values": "values" in self.form.parameter_dict,
                        "parameters": "parameters" in self.form.parameter_dict,
                    },
                },
                {
                    "name": "values",
                    "label": "Constant values",
                    "field_type": ValuesAndExternalDataWidget,
                    "value": self.form.get_param_dict_value("values"),
                    # value (for example cost) may be negative
                    "field_args": {"lower_bound": -pow(10, 6)},
                    "validate_fun": partial(self._check_size, field_name="values"),
                    "help_text": "You must provide a number of values equal to the "
                    "number of control curves plus one",
                },
                {
                    "name": "parameters",
                    "label": "Parametric values",
                    "field_type": ParametersListPickerWidget,
                    # Default widget behaviour is always mandatory - but this can be
                    # skipped if "values" are provided. Make this optional. If source
                    # is "parameters", self._check_size will check the field is not
                    # empty
                    "field_args": {"is_mandatory": False},
                    "validate_fun": partial(self._check_size, field_name="parameters"),
                    "value": self.form.get_param_dict_value("parameters"),
                    "help_text": "You must provide a number of parameters equal to the "
                    "number of control curves plus one",
                },
            ],
            "Miscellaneous": [self.form.comment],
        }

        return data_dict

    def _check_size(
        self,
        name: str,
        label: str,
        value: list[str | dict | float | int],
        field_name: str,
    ) -> Validation:
        """
        Checks that the number of items in "field_name" equals the number of control
        curves plus one. Validation is ignored if the source is not set to
        "field_name".
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :param field_name: The name of the field ("values" or "parameters").
        :return: The validation instance.
        """
        # noinspection PyTypeChecker
        source_widget: ControlCurvesValuesSourceWidget = self.form.find_field_by_name(
            "values_source"
        ).widget
        # noinspection PyTypeChecker
        control_curves_widget: ControlCurvesWidget = self.form.find_field_by_name(
            "control_curves"
        ).widget
        curves_size = len(control_curves_widget.get_value())
        expected_size = curves_size + self.values_size_increment
        if (
            source_widget.get_value() == field_name
            and curves_size
            and len(value) != expected_size
        ):
            return Validation(
                f"The number of {field_name} must be {expected_size} "
                "(i.e. the number of control curves plus "
                f"{self.values_size_increment})"
            )

        return Validation()

    def filter(self, form_data):
        """
        Removes fields depending on the value set in source.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # set "control_curve" or "control_curves" key
        curves = form_data["control_curves"]
        if len(curves) == 1:
            form_data["control_curve"] = curves[0]
            del form_data["control_curves"]

        # handle values
        keys_to_delete = ["values_source"]
        if form_data["values_source"] == "values":
            keys_to_delete += ["parameters"]
        elif form_data["values_source"] == "parameters":
            keys_to_delete += ["values"]

        self.logger.debug(f"Deleting keys: {keys_to_delete}")
        for key in keys_to_delete:
            form_data.pop(key, None)
