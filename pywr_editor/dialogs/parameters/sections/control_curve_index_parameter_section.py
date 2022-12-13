from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import (
    ControlCurvesWidget,
    StoragePickerWidget,
    FormSection,
)
from pywr_editor.utils import Logging


class ControlCurveIndexParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
    ):
        """
        Initialises the form section for ControlCurveIndexParameter.
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
                    "name": "storage_node",
                    "field_type": StoragePickerWidget,
                    "value": self.form.get_param_dict_value("storage_node"),
                    "help_text": "Use the storage from the node specified above to "
                    "return a zero-based index",
                },
                # this is always mandatory
                {
                    # widget always returns a list of parameters
                    "name": "control_curves",
                    "field_type": ControlCurvesWidget,
                    "value": {
                        # parameter only supports "control_curves" key
                        "control_curve": None,
                        "control_curves": self.form.get_param_dict_value(
                            "control_curves"
                        ),
                    },
                    "help_text": "Sort the control curves by the highest to the "
                    "lowest. The parameter returns the zero-based index "
                    "corresponding to the first control curve that is above the "
                    "node storage. For example, if only one control curve is "
                    "provided, the index is either 0 (above) or 1 (below). For two "
                    "curves, the index is either 0 (above both), 1 (in between), or "
                    "2 (below both) depending on the node storage",
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
