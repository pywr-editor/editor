from typing import Any, Callable, TYPE_CHECKING
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMessageBox, QPushButton
from pywr_editor.form import (
    ModelComponentForm,
    SourceSelectorWidget,
    UrlWidget,
)
from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from pywr_editor.form import ExternalDataPickerDialogWidget


class ExternalDataPickerFormWidget(ModelComponentForm):
    def __init__(
        self,
        external_data_dict: dict[str, Any],
        model_config: ModelConfig,
        save_button: QPushButton,
        after_save: Callable[[str | dict[str, Any]], None] | None,
        parent: "ExternalDataPickerDialogWidget",
    ):
        """
        Initialises the parameter form.
        :param external_data_dict: The dictionary containing the instructions to fetch
        external data using Pywr.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param after_save: A function to execute after the form is validated. This
        receives the form data as dictionary.
        :param parent: The parent modal.
        """
        self.after_save = after_save

        super().__init__(
            form_dict=external_data_dict,
            available_fields={},
            model_config=model_config,
            save_button=save_button,
            parent=parent,
        )

        # Make fields optional. At least one of them must be provided depending
        # on how the profile is selected in the table (by row or by column).
        # See self.on_save
        optional_col_field = self.column_field
        optional_col_field["field_args"] = {"optional": True}

        optional_index_field = self.index_field
        optional_index_field["field_args"] = {"optional": True}

        self.available_fields = {
            "Source": [
                self.source_field_wo_value,
                # table
                self.table_field,
                # anonymous table
                self.url_field,
            ]
            + self.csv_parse_fields
            + self.excel_parse_fields
            + self.h5_parse_fields,
            self.table_config_group_name: [
                self.index_col_field,
                optional_index_field,
                optional_col_field,
            ],
        }

        self.load_fields()

    @Slot()
    def on_save(self) -> None | bool:
        """
        Slot called when user clicks on the "Save" button.
        The form data are sent to self.after_save().
        :return: None
        """
        form_data = self.save()
        if form_data is False:
            return

        # get source
        # noinspection PyTypeChecker
        source_widget: SourceSelectorWidget = self.find_field_by_name(
            "source"
        ).widget
        labels = source_widget.labels

        # delete keys
        url_fields = (
            UrlWidget.csv_fields
            + UrlWidget.excel_fields
            + UrlWidget.hdf_fields
            + UrlWidget.common_field
        )

        keys_to_delete = ["source"]
        if form_data["source"] == labels["table"]:
            keys_to_delete += ["values", "url"] + url_fields
        elif form_data["source"] == labels["anonymous_table"]:
            keys_to_delete += ["values", "table"]

        self.logger.debug(f"Deleting keys: {keys_to_delete}")
        for key in keys_to_delete:
            form_data.pop(key, None)

        # column or index is mandatory
        error_message = None
        if "column" not in form_data and "index" not in form_data:
            error_message = "You must select an index or column name"
        if "column" in form_data and "index" in form_data:
            error_message = (
                "You must select an index value (to select a table row) "
                + "or a column name (to select a table column). You cannot "
                + "select both at the same time"
            )

        if error_message is not None:
            self.logger.debug(error_message)
            QMessageBox().critical(self, "Cannot save the form", error_message)
            self.save_button.setEnabled(True)
            return False

        # callback function
        self.after_save(form_data)
