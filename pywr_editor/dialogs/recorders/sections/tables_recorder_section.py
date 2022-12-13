from ..recorder_dialog_form import RecorderDialogForm
from pywr_editor.form import (
    FormSection,
    FileBrowserWidget,
    FileModeWidget,
    MultiNodePickerWidget,
    H5CompressionLibWidget,
    DictionaryWidget,
    MultiParameterPickerWidget,
)
from pywr_editor.utils import Logging


class TablesRecorderSection(FormSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for TableRecorder.
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

        filter_kwd = self.form.get_recorder_dict_value("filter_kwd")
        if filter_kwd is None:
            filter_kwd = {}

        data_dict = {
            "Configuration": [
                {
                    "name": "url",
                    "label": "File",
                    "field_type": FileBrowserWidget,
                    "field_args": {"file_extension": "h5"},
                    "value": self.form.get_recorder_dict_value("url"),
                    "help_text": "The path where the recorder saves the H5 file. "
                    + "If the file already exists, the recorder updates it",
                },
                {
                    "name": "nodes",
                    "value": self.form.get_recorder_dict_value("nodes"),
                    "field_type": MultiNodePickerWidget,
                    "help_text": "A list of nodes to export. The recorder exports "
                    + "all nodes' flow and storage, when no node is selected",
                },
                {
                    "name": "parameters",
                    "value": self.form.get_recorder_dict_value("parameters"),
                    "field_type": MultiParameterPickerWidget,
                    "help_text": "A list of parameter values to export",
                },
                self.form.comment,
            ],
            "Grouping": [
                {
                    "name": "where",
                    "value": self.form.get_recorder_dict_value("where"),
                    "default_value": "/",
                    "allow_empty": False,
                    "help_text": "The default path to use for all the H5 groups",
                },
                {
                    "name": "time",
                    "value": self.form.get_recorder_dict_value("time"),
                    "default_value": "/time",
                    "allow_empty": False,
                    "help_text": "The group name/path where to save the time array",
                },
                {
                    "name": "scenarios",
                    "value": self.form.get_recorder_dict_value("scenarios"),
                    "default_value": "/scenarios",
                    "help_text": "The group name/path where to save the scenario "
                    + "information. If empty, no information is saved",
                },
                {
                    "name": "routes_flows",
                    "label": "Routes' flows",
                    "value": self.form.get_recorder_dict_value("routes_flows"),
                    "help_text": "The path relative to 'Where' where to save the "
                    + "routes' flows information. If empty, no information is saved",
                },
                {
                    "name": "routes",
                    "value": self.form.get_recorder_dict_value("routes"),
                    "default_value": "/routes",
                    "help_text": "The path relative to 'Where' where to save the "
                    + 'routes. If "Routes\' flows" or this field is empty, no '
                    + "information is saved",
                },
            ],
            "Advanced": [
                {
                    "name": "mode",
                    "field_type": FileModeWidget,
                    "value": self.form.get_recorder_dict_value("mode"),
                    "help_text": "The mode to open the file",
                },
                {
                    "name": "complevel",
                    "label": "Compression level",
                    "field_type": "integer",
                    "default_value": 0,
                    "min_value": 0,
                    "max_value": 9,
                    "value": filter_kwd["complevel"]
                    if "complevel" in filter_kwd
                    else None,
                    "help_text": "A value of 0 (the default) disables compression",
                },
                {
                    "name": "complib",
                    "label": "Compression algorithm",
                    "field_type": H5CompressionLibWidget,
                    "value": filter_kwd["complib"]
                    if "complib" in filter_kwd
                    else None,
                },
                {
                    "name": "metadata",
                    "field_type": DictionaryWidget,
                    "value": self.form.get_recorder_dict_value("metadata"),
                    "help_text": "Additional attributes to store in the H5 file",
                },
                {
                    "name": "create_directories",
                    "value": self.form.get_recorder_dict_value(
                        "create_directories"
                    ),
                    "field_type": "boolean",
                    "default_value": False,
                    "help_text": "If one or more directories in the 'File' path do "
                    + "not exist, the recorder attempts to create them",
                },
            ],
        }

        return data_dict

    def filter(self, form_data: dict) -> None:
        """
        Combines the filter_kwd fields.
        :param form_data: The form data.
        :return: None
        """
        form_data["filter_kwd"] = {}
        for field in ["complevel", "complib"]:
            # handle complevel=0 (default) and None
            if field in form_data and form_data[field]:
                form_data["filter_kwd"][field] = form_data[field]
                del form_data[field]

        # remove key if not filled
        if len(form_data["filter_kwd"]) == 0:
            del form_data["filter_kwd"]
