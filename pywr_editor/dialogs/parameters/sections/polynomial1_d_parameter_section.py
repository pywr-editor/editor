from pywr_editor.form import (
    FloatWidget,
    FormSection,
    NodePickerWidget,
    ParameterLineEditWidget,
    StoragePickerWidget,
    TableValuesWidget,
    Validation,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class Polynomial1DParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a Polynomial1DParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")

        return {
            "Configuration": [
                {
                    "name": "coefficients",
                    "field_type": TableValuesWidget,
                    "field_args": {
                        "show_row_numbers": True,
                        "row_number_from_zero": True,
                        "row_number_label": "Degree",
                        "min_total_values": 1,
                        "scientific_notation": True,
                        "lower_bound": -pow(10, 30),
                        "upper_bound": pow(10, 30),
                        "precision": 9,
                    },
                    "value": {
                        "coefficient": self.form.get_param_dict_value("coefficients")
                    },
                    "help_text": "Define the coefficients. You can set, as the "
                    "polynomial independent variable, the flow from a node, the volume "
                    "from a storage node or a parameter value",
                },
                {
                    "name": "storage_node",
                    "label": "Storage from node",
                    "field_type": StoragePickerWidget,
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_param_dict_value("storage_node"),
                    "help_text": "Use the storage from the node specified above "
                    "as independent variable for the polynomial",
                },
                {
                    "name": "use_proportional_volume",
                    "field_type": "boolean",
                    "default_value": False,
                    "value": self.form.get_param_dict_value("use_proportional_volume"),
                    "help_text": "If Yes the independent variable is the proportional "
                    "volume (between 0 and 1) of the Storage node",
                },
                {
                    "name": "node",
                    "label": "Flow from node",
                    "field_type": NodePickerWidget,
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_param_dict_value("node"),
                    "help_text": "Use the flow from the node specified above "
                    "as independent variable for the polynomial",
                },
                {
                    "name": "parameter",
                    "label": "Value from parameter",
                    "field_type": ParameterLineEditWidget,
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_param_dict_value("parameter"),
                    "help_text": "Use the value from the parameter specified above "
                    "as independent variable for the polynomial",
                },
            ],
            "Miscellaneous": [
                {
                    "name": "offset",
                    "value": self.form.get_param_dict_value("offset"),
                    "field_type": FloatWidget,
                    "default_value": None,
                    "help_text": "Offset the independent variable by the provided "
                    "amount. Default to empty to ignore",
                },
                {
                    "name": "scale",
                    "field_type": FloatWidget,
                    "default_value": None,
                    "value": self.form.get_param_dict_value("scale"),
                    "help_text": "Scale the independent variable by the provided "
                    "amount before applying the offset. Default to empty to ignore",
                },
                self.form.comment,
            ],
        }

    def filter(self, form_data: dict) -> None:
        """
        Splits the data points dictionary.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # convert dictionary to list
        form_data["coefficients"] = form_data["coefficients"]["coefficient"]

        # remove proportional volume if storage node is not set
        if (
            "use_proportional_volume" in form_data
            and form_data["use_proportional_volume"]
            and "storage_node" not in form_data
        ):
            del form_data["use_proportional_volume"]

    def validate(self, form_data: dict) -> Validation:
        """
        Checks that only one field for the independent variable is provided.
        :param form_data: The form data dictionary when the form validation is
        successful.
        :return: The Validation instance.
        """
        self.form: ParameterDialogForm

        field_check = []
        for field_name in ["parameter", "node", "storage_node"]:
            value = self.form.find_field_by_name(field_name).value()
            # node combo box returns a string
            field_check.append(value is None)

        # more than independent variable was provided
        if all(field_check):
            return Validation(
                "You must provide the independent variable for the "
                "polynomial. You can select a node, to use its storage or flow, or "
                "a parameter to use its value",
            )
        elif field_check.count(False) > 1:
            return Validation(
                "You can provide only one type of independent variable "
                "for the polynomial. You can only select a node, for its storage or "
                "flow, or a parameter for its value",
            )

        return Validation()
