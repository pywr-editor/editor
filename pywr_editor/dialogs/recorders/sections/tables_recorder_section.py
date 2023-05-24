from pywr_editor.form import (
    DictionaryWidget,
    FieldConfig,
    FileBrowserWidget,
    FileModeWidget,
    FormSection,
    H5CompressionLibWidget,
    MultiNodePickerWidget,
    MultiParameterPickerWidget,
)

from ..recorder_dialog_form import RecorderDialogForm


class TablesRecorderSection(FormSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for TableRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)

        filter_kwd = form.field_value("filter_kwd")
        if filter_kwd is None:
            filter_kwd = {}

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="url",
                        label="File",
                        field_type=FileBrowserWidget,
                        field_args={"file_extension": "h5"},
                        value=form.field_value("url"),
                        help_text="The path where the recorder saves the H5 file. "
                        "If the file already exists, the recorder updates it",
                    ),
                    FieldConfig(
                        name="nodes",
                        value=form.field_value("nodes"),
                        field_type=MultiNodePickerWidget,
                        help_text="A list of nodes to export. The recorder exports "
                        "all nodes' flow and storage, when no node is selected",
                    ),
                    FieldConfig(
                        name="parameters",
                        value=form.field_value("parameters"),
                        field_type=MultiParameterPickerWidget,
                        help_text="A list of parameter values to export",
                    ),
                    form.comment,
                ],
                "Grouping": [
                    FieldConfig(
                        name="where",
                        value=form.field_value("where"),
                        default_value="/",
                        allow_empty=False,
                        help_text="The default path to use for all the H5 groups",
                    ),
                    FieldConfig(
                        name="time",
                        value=form.field_value("time"),
                        default_value="/time",
                        allow_empty=False,
                        help_text="The group name/path where to save the time array",
                    ),
                    FieldConfig(
                        name="scenarios",
                        value=form.field_value("scenarios"),
                        default_value="/scenarios",
                        help_text="The group name/path where to save the scenario "
                        "information. If empty, no information is saved",
                    ),
                    FieldConfig(
                        name="routes_flows",
                        label="Routes' flows",
                        value=form.field_value("routes_flows"),
                        help_text="The path relative to 'Where' where to save the "
                        "routes' flows information. If empty, no information is saved",
                    ),
                    FieldConfig(
                        name="routes",
                        value=form.field_value("routes"),
                        default_value="/routes",
                        help_text="The path relative to 'Where' where to save the "
                        'routes. If "Routes\' flows" or this field is empty, no '
                        "information is saved",
                    ),
                ],
                "Advanced": [
                    FieldConfig(
                        name="mode",
                        field_type=FileModeWidget,
                        value=form.field_value("mode"),
                        help_text="The mode to open the file",
                    ),
                    FieldConfig(
                        name="complevel",
                        label="Compression level",
                        field_type="integer",
                        default_value=0,
                        min_value=0,
                        max_value=9,
                        value=filter_kwd["complevel"]
                        if "complevel" in filter_kwd
                        else None,
                        help_text="A value of 0 (the default) disables compression",
                    ),
                    FieldConfig(
                        name="complib",
                        label="Compression algorithm",
                        field_type=H5CompressionLibWidget,
                        value=filter_kwd["complib"]
                        if "complib" in filter_kwd
                        else None,
                    ),
                    FieldConfig(
                        name="metadata",
                        field_type=DictionaryWidget,
                        field_args={"is_mandatory": False},
                        value=form.field_value("metadata"),
                        help_text="Additional attributes to store in the H5 file",
                    ),
                    FieldConfig(
                        name="create_directories",
                        value=form.field_value("create_directories"),
                        field_type="boolean",
                        default_value=False,
                        help_text="If one or more directories in the 'File' path do "
                        "not exist, the recorder attempts to create them",
                    ),
                ],
            }
        )

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
