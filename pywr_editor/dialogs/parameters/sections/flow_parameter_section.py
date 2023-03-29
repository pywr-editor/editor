from pywr_editor.form import FloatWidget, FormSection, NodePickerWidget
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class FlowParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a FlowParameter.
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

        data_dict = {
            "Configuration": [
                {
                    "name": "node",
                    "field_type": NodePickerWidget,
                    "value": self.form.get_param_dict_value("node"),
                    "allow_empty": False,
                    "help_text": "The parameter provides the flow at the previous time "
                    "step for the specified node",
                },
                {
                    "name": "initial_value",
                    "field_type": FloatWidget,
                    "default_value": 0,
                    "field_args": {"min_value": 0},
                    "value": self.form.get_param_dict_value("initial_value"),
                    "allow_empty": False,
                    "help_text": "The value to return on the first time step when the "
                    "node does not have any past flow. Default to 0",
                },
            ],
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        return data_dict
