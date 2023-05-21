from pywr_editor.form import (
    CSVCompressionLibWidget,
    CSVDialectWidget,
    FileBrowserWidget,
    FormSection,
    FormValidation,
    MultiNodePickerWidget,
)
from pywr_editor.utils import Logging

from ..recorder_dialog_form import RecorderDialogForm


class CSVRecorderSection(FormSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for CSVRecorder.
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
        self.form: RecorderDialogForm
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": [
                {
                    "name": "url",
                    "label": "File",
                    "field_type": FileBrowserWidget,
                    "field_args": {"file_extension": "csv"},
                    "value": self.form.get_recorder_dict_value("url"),
                    "help_text": "The path where the recorder saves the CSV file",
                },
                {
                    "name": "nodes",
                    "value": self.form.get_recorder_dict_value("nodes"),
                    "field_type": MultiNodePickerWidget,
                    "help_text": "A list of nodes to export. The recorder exports "
                    + "all nodes, when no node is selected",
                },
                {
                    "name": "scenario_index",
                    "label": "Scenario/combination index",
                    "value": self.form.get_recorder_dict_value("scenario_index"),
                    "field_type": "integer",
                    "min_value": 0,
                    "default_value": 0,
                    "help_text": "A number starting from 0 indicating the index of "
                    + "scenario or combination to export. Set it to 0, when no "
                    + "scenario is configured",
                },
                self.form.comment,
            ],
            "Advanced": [
                {
                    "name": "complib",
                    "label": "Compression algorithm",
                    "field_type": CSVCompressionLibWidget,
                    "value": self.form.get_recorder_dict_value("complib"),
                },
                {
                    "name": "complevel",
                    "label": "Compression level",
                    "field_type": "integer",
                    "default_value": 9,
                    "min_value": 0,
                    "max_value": 9,
                    "validate_fun": self.check_complevel,
                    "value": self.form.get_recorder_dict_value("complevel"),
                },
                {
                    "name": "dialect",
                    "label": "CSV dialect",
                    "field_type": CSVDialectWidget,
                    "value": self.form.get_recorder_dict_value("dialect"),
                },
            ],
        }

        return data_dict

    def check_complevel(self, name: str, label: str, value: int) -> FormValidation:
        """
        Checks the compression level.
        :param name: The field name.
        :param label: The field value.
        :param value: The field value.
        :return: The validation instance.
        """
        complib_value = self.form.find_field_by_name("complib").value()
        if complib_value and complib_value == "bzip2" and value == 0:
            return FormValidation(
                validation=False,
                error_message="The minimum compression level for the BZIP2 algorithm "
                + "is 1",
            )
        return FormValidation(validation=True)
