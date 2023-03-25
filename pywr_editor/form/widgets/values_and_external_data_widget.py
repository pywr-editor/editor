from typing import Any

import qtawesome as qta
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from pywr_editor.form import (
    ExternalDataPickerDialogWidget,
    FormField,
    FormValidation,
    TableValuesWidget,
)
from pywr_editor.utils import get_signal_sender
from pywr_editor.widgets import ComboBox, PushButton, PushIconButton

"""
 Defines a widget that allows providing values for one variable:
    - from a list
    - from an external file, using a model table or a table file

 This widget extends the TableValuesWidget.
"""


class ValuesAndExternalDataWidget(TableValuesWidget):
    labels_map: dict[str, str] = {
        "values": "Provide values",
        "external": "From a table or file",
    }

    def __init__(
        self,
        name: str,
        value: list[float | int] | dict[str, Any] | None,
        parent: FormField,
        show_row_numbers: bool = False,
        multiple_variables: bool = False,
        variable_names: list[str] = None,
        row_number_label: str = "Row",
        min_total_values: int | None = None,
        upper_bound: float | None = None,
        lower_bound: float | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected parameter name.
        :param parent: The parent widget.
        :param show_row_numbers: Shows the number of the row in the table. Default to
        False.
        :param multiple_variables: Enable supports for more than one variable.
        :param variable_names: When multiple_variables is False, this is a string and
        is optional. When multiple_variables is True, this is mandatory and must be a
        list of names for the variables.
        :param row_number_label: The column label for the row numbers. Default to Row.
        :param min_total_values: The minimum total values each variable must have in
        the table. Default to None to avoid any initial check and form validation.
        :param lower_bound: The allowed minimum number. Optional.
        :param upper_bound: The allowed maximum number. Optional.
        """
        if multiple_variables and (
            not variable_names or not isinstance(variable_names, list)
        ):
            raise ValueError(
                "You must provide a list of variables when multiple_variables is True"
            )

        table_dict = {}
        # in case of one variable, use field name or supplied name
        self.one_var_name = (
            variable_names if isinstance(variable_names, str) else name
        )

        if multiple_variables:
            if isinstance(value, list):
                for vi, var_name in enumerate(variable_names):
                    try:
                        table_dict[var_name] = value[vi]
                    except IndexError:
                        table_dict[var_name] = []
            elif value is None:
                table_dict = {var_name: [] for var_name in variable_names}
            else:
                table_dict = {self.one_var_name: []}
        else:
            table_dict = {self.one_var_name: value}

        table_args = dict(
            name=name,
            # TableValuesWidget wants a dictionary
            value=table_dict,
            parent=parent,
            show_row_numbers=show_row_numbers,
            row_number_label=row_number_label,
            min_total_values=min_total_values,
        )
        if lower_bound:
            table_args["lower_bound"] = lower_bound
        if upper_bound:
            table_args["upper_bound"] = upper_bound
        super().__init__(**table_args)

        self.init = True
        self.model_config = self.form.model_config

        self.raw_value = value
        self.multiple_variables = multiple_variables
        self.external_data_dict = None
        self.min_total_values = min_total_values
        # if at least one data point is required, field is mandatory
        self.is_mandatory = min_total_values and min_total_values > 0

        # Add the ComboBox with choice
        self.combo_box = ComboBox()
        self.combo_box.addItems(list(self.labels_map.values()))
        # noinspection PyUnresolvedReferences
        self.combo_box.currentIndexChanged.connect(self.on_update_value)

        # add external file pickers
        self.line_edit_widget_container = self.generate_data_picker_widget()
        # noinspection PyTypeChecker
        self.line_edit: QLineEdit = self.line_edit_widget_container.findChild(
            QLineEdit
        )

        # add all widgets
        # noinspection PyTypeChecker
        layout: QVBoxLayout = self.findChild(QVBoxLayout)
        layout.insertWidget(0, self.combo_box)
        layout.addWidget(self.line_edit_widget_container)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        # Init parent widget
        super().register_actions()
        # Show/hide widgets at init
        self.on_update_value()
        # Set current value in QLineEdit
        self.update_line_edit(self.raw_value)

        # empty string or value not provided
        if self.raw_value is None:
            self.logger.debug(
                f"Empty value. Setting default choice to '{self.labels_map['values']}'"
            )
            # reset warning from parent widget and hide TableView
            self.combo_box.setCurrentText(self.labels_map["values"])
            self.form_field.clear_message()
        # external file or model table
        elif isinstance(self.raw_value, dict):
            self.logger.debug(
                "Value is a dictionary to fetch data from an external file"
            )
            self.combo_box.setCurrentText(self.labels_map["external"])

            # reset warning from parent widget and hide QLineEdit
            self.form_field.clear_message()
            self.external_data_dict = self.raw_value

            if "url" in self.raw_value:
                self.logger.debug(f"Url is '{self.raw_value['url']}'")
            elif "table" in self.raw_value:
                self.logger.debug(f"Table is '{self.raw_value['table']}'")
            # field is mandatory
            elif self.is_mandatory:
                message = (
                    "The configuration to fetch the external data is not valid"
                )
                self.logger.debug(message)
                self.form_field.set_warning_message(message)
        # default to parent widget - fill with values
        else:
            self.combo_box.setCurrentText(self.labels_map["values"])

        self.init = False

    @Slot()
    def on_update_value(self) -> None:
        """
        Shows or hides the TableView and data picker widgets based on the selected
        value in the ComboBox.
        :return: None
        """
        self.logger.debug(
            f"Running on_update_value Slot from {get_signal_sender(self)}"
        )

        # when source changes, resets all widgets
        if self.init is False:
            self.logger.debug("Resetting widget")
            # reset table and QLineEdit
            super().reset()
            self.reset_line_edit()
            self.form_field.clear_message()

        is_values_selected = (
            self.combo_box.currentText() == self.labels_map["values"]
        )
        # toggle TableView and its buttons
        self.table.setVisible(is_values_selected)
        for button in self.table_buttons:
            button.setVisible(is_values_selected)
        # toggle external data pickers
        self.line_edit_widget_container.setVisible(not is_values_selected)

    def generate_data_picker_widget(self) -> QWidget:
        """
        Returns the widget containing the widget allowing selecting the external data.
        :return: The widget.
        """
        line_edit_widget_container = QWidget()

        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        line_edit.setText("None")

        # buttons
        select_button = PushIconButton(
            icon=qta.icon("msc.inspect"), label="Select", small=True
        )
        select_button.setToolTip(
            "Select an existing model parameter or define a new one"
        )
        # noinspection PyUnresolvedReferences
        select_button.clicked.connect(self.open_data_picker)

        clear_button = PushIconButton(
            icon=qta.icon("msc.remove"), label="Clear", small=True
        )
        clear_button.setToolTip("Empty the field")
        # noinspection PyUnresolvedReferences
        clear_button.clicked.connect(self.reset_line_edit)

        # main layout
        layout = QHBoxLayout(line_edit_widget_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(line_edit)
        layout.addWidget(select_button)
        layout.addWidget(clear_button)

        return line_edit_widget_container

    def get_value(
        self,
    ) -> list[float | int] | list[list[float | int]] | dict | None:
        """
        Returns the value.
        :return: The list of values or the dictionary to fetch external data.
        """
        source = self.combo_box.currentText()
        # return the list from the dictionary
        if source == self.labels_map["values"]:
            values_dict = super().get_value()
            if self.multiple_variables:
                # return nested lists
                return [var_values for var_values in values_dict.values()]
            else:
                return values_dict[self.one_var_name]
        elif source == self.labels_map["external"]:
            return self.external_data_dict

    def validate(
        self,
        name: str,
        label: str,
        value: list[float | int] | list[list[float | int]] | dict | None,
    ) -> FormValidation:
        """
        Checks that the value is valid.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label
        :return: The FormValidation instance.
        """
        if self.combo_box.currentText() == self.labels_map["values"]:
            self.logger.debug(f"Validation with {self.labels_map['values']}")
            return super().validate(name, label, {self.name: value})
        elif (
            self.combo_box.currentText() == self.labels_map["external"]
            and self.is_mandatory
        ):
            self.logger.debug(f"Validation with {self.labels_map['external']}")
            # dictionary is empty or variable is None
            # the dictionary content is checked in the dialog window when saving the
            # form; perform minimum validation by checking for "url" and "table keys
            if not self.external_data_dict or (
                "url" not in self.external_data_dict
                and "table" not in self.external_data_dict
            ):
                return FormValidation(
                    validation=False,
                    error_message="You must configure the field to fetch the data",
                )

        return FormValidation(validation=True)

    def update_line_edit(self, value_dict: dict[str, Any]) -> None:
        """
        Sets the selected file in the QLineEdit.
        :param value_dict: The dictionary containing the external data information.
        :return: None
        """
        if isinstance(value_dict, dict):
            self.logger.debug(f"Setting data picker text using {value_dict}")
            if "url" in value_dict:
                self.line_edit.setText(f"File: {value_dict['url']}")
            elif "table" in value_dict:
                self.line_edit.setText(f"Table: {value_dict['table']}")

    @Slot()
    def open_data_picker(self) -> None:
        """
        Opens the dialog to select an external file or table.
        :return: None
        """
        dialog = ExternalDataPickerDialogWidget(
            model_config=self.model_config,
            external_data_dict=self.external_data_dict,
            after_form_save=self.on_form_save,
            parent=self.form.parent,
        )
        dialog.open()

    def on_form_save(self, form_data: str | dict[str, Any]) -> None:
        """
        Updates the external data dictionary.
        :param form_data: The form data from ExternalDataPickerDialogWidget.
        :return: None
        """
        self.logger.debug(
            f"Running post-saving action on_form_save with value {form_data}"
        )
        self.external_data_dict = form_data
        self.update_line_edit(self.external_data_dict)

    @Slot()
    def reset_line_edit(self):
        """
        Resets the QLineEdit widget.
        :return: None
        """
        self.external_data_dict = None
        self.line_edit.setText("None")

    def reset(self) -> None:
        """
        Resets the field. This empties the TableView and QLineEdit widgets and restore
        the choice to "Provide values".
        :return: None
        """
        # reset table
        super().reset()
        # reset QLineEdit
        self.reset_line_edit()
        # set ComboBox to default value
        self.combo_box.setCurrentText(self.labels_map["values"])

    @property
    def table_buttons(self) -> list[PushButton | PushIconButton]:
        """
        Returns all the buttons used to manipulate the table.
        :return: A list of button instances.
        """
        buttons = []
        for widget_id in range(0, self.button_layout.count()):
            widget = self.button_layout.itemAt(widget_id).widget()
            if widget is not None:
                buttons.append(widget)

        return buttons
