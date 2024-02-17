from typing import TYPE_CHECKING, Any, List, Literal, Union

import qtawesome as qta
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QVBoxLayout

from pywr_editor.form import (
    AbstractModelComponentListPickerModel,
    FormField,
    FormWidget,
    ModelComponentPickerDialog,
    Validation,
)
from pywr_editor.model import ParameterConfig, RecorderConfig
from pywr_editor.utils import Logging, get_signal_sender, move_row
from pywr_editor.widgets import ListView, PushIconButton, TableView

if TYPE_CHECKING:
    from pywr_editor.dialogs import ParameterDialogForm, RecorderDialogForm

"""
 This widget provides a list of model components (parameters or recorders)
 and allows the user to add, delete and sort the items.
"""


class AbstractModelComponentsListPickerWidget(FormWidget):
    def __init__(
        self,
        name: str,
        value: List[int | float | str | dict] | None,
        parent: FormField,
        component_type: Literal["parameter", "recorder"],
        log_name: str,
        is_mandatory: bool = True,
        show_row_numbers: bool = False,
        row_number_label: str | None = None,
        include_component_key: List[str] | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The list of model components. Each item can be a dictionary, for
        anonymous parameters or recorders or a string representing a model component.
        :param parent: The parent widget.
        :param component_type: The component type (parameter or recorder).
        :param log_name: The name to use in the logger.
        :param is_mandatory: Whether at least one component should be provided or the
        field can be left empty. Default to True.
        :param include_component_key: A string or list of strings representing
        component keys to only include in the widget. An error will be shown if any
        other component types is present in the value. The picker dialog will filter
        the component types as well.
        """
        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget for {component_type} with value {value}")

        super().__init__(name, value, parent)

        self.is_mandatory = is_mandatory
        self.component_type = component_type
        self.form: Union["ParameterDialogForm", "RecorderDialogForm"]
        self.dialog = self.form.parent
        self.model_config = self.form.model_config

        if self.is_parameter:
            self.components_data = self.model_config.pywr_parameter_data
            custom_component_keys = (
                self.model_config.includes.get_custom_parameters().keys()
            )
            self._config_prop = self.model_config.parameters
            self._exist_config_method = self._config_prop.exists
            self._config_class = ParameterConfig
        elif self.is_recorder:
            self.components_data = self.model_config.pywr_recorder_data
            custom_component_keys = (
                self.model_config.includes.get_custom_recorders().keys()
            )
            self._config_prop = self.model_config.recorders
            self._exist_config_method = self._config_prop.exists
            self._config_class = RecorderConfig
        else:
            raise ValueError("The component_type can only be 'parameter' or 'recorder'")

        # include only certain component types
        if include_component_key is not None:
            if isinstance(include_component_key, str):
                include_component_key = [include_component_key]
            # convert to lowercase
            include_component_key = [key.lower() for key in include_component_key]

            # check if the component type exists
            all_component_keys = self.components_data.keys + list(custom_component_keys)
            for comp_key in include_component_key:
                if comp_key not in all_component_keys:
                    raise ValueError(
                        f"The {component_type} type {comp_key} does not exist. "
                        + f"Available types are: {', '.join(all_component_keys)}"
                    )
            self.logger.debug(
                f"Including only the following {component_type} keys: "
                + f"{include_component_key}"
            )
            # prettified keys
            self.include_component_names = list(
                map(
                    self.components_data.humanise_name,
                    include_component_key,
                )
            )
        else:
            self.include_component_names = None
        self.include_component_key = include_component_key

        self.value, self.warning_message = self.sanitise_value(value)
        self.model = AbstractModelComponentListPickerModel(
            values=self.value,
            component_type=component_type,
            model_config=self.model_config,
            show_row_numbers=show_row_numbers,
            row_number_label=row_number_label,
        )
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.connect(self.form.on_field_changed)

        # Action buttons
        buttons_layout = QHBoxLayout()
        self.add_button = PushIconButton(
            icon=qta.icon("msc.add"), label="Add", small=True
        )
        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_component)
        self.add_button.setToolTip(f"Add a new {component_type}")

        self.edit_button = PushIconButton(
            icon=qta.icon("msc.edit"), label="Edit", small=True
        )
        self.edit_button.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.edit_button.clicked.connect(self.on_edit_component)
        self.edit_button.setToolTip(f"Edit the selected {component_type}")

        self.delete_button = PushIconButton(
            icon=qta.icon("msc.remove"), label="Delete", small=True
        )
        self.delete_button.setDisabled(True)
        self.delete_button.setToolTip(f"Delete the selected {component_type}")
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete)

        self.move_up = PushIconButton(
            icon=qta.icon("msc.chevron-up"), label="Move up", small=True
        )
        self.move_up.setToolTip(f"Move the {component_type} up in the list")
        self.move_up.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.move_up.clicked.connect(self.on_move_up)

        self.move_down = PushIconButton(
            icon=qta.icon("msc.chevron-down"), label="Move down", small=True
        )
        self.move_down.setToolTip(f"Move the {component_type} down in the list")
        self.move_down.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.move_down.clicked.connect(self.on_move_down)

        buttons_layout.addWidget(self.move_up)
        buttons_layout.addWidget(self.move_down)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)

        # List
        widget_args = {
            "model": self.model,
            "toggle_buttons_on_selection": [
                self.delete_button,
                self.move_up,
                self.move_down,
            ],
        }
        if show_row_numbers:
            self.list = TableView(**widget_args)
            # always select row
            self.list.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
        else:
            self.list = ListView(**widget_args)
        self.list.setMaximumHeight(100)
        # noinspection PyUnresolvedReferences
        self.list.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.list)
        layout.addLayout(buttons_layout)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.field.set_warning(self.warning_message)

    @Slot()
    def on_selection_changed(self) -> None:
        """
        Enable or disable action buttons based on the number of selected items.
        :return: None
        """
        self.logger.debug(
            f"Running on_selection_changed Slot from {get_signal_sender(self)}"
        )
        selection = self.list.selectionModel().selection()
        total_rows = self.list.model.rowCount()

        # enable edit button only when item is selected
        self.edit_button.setEnabled(selection.count() == 1)

        if selection.count() == 1:
            # enable/disable sorting buttons based on the selected row (for example,
            # if last row, move down button is disabled)
            selected_row = selection.indexes()[0].row() + 1
            self.move_up.setEnabled(selected_row != 1)
            self.move_down.setEnabled(selected_row != total_rows)

    @Slot()
    def on_move_up(self) -> None:
        """
        Moves a parameter up in the list.
        :return: None
        """
        self.logger.debug(f"Running on_move_up Slot from {get_signal_sender(self)}")
        move_row(widget=self.list, direction="up", callback=self.move_row_in_model)

    @Slot()
    def on_move_down(self) -> None:
        """
        Moves a parameter down in the list.
        :return: None
        """
        self.logger.debug(f"Running on_move_down Slot from {get_signal_sender(self)}")
        move_row(widget=self.list, direction="down", callback=self.move_row_in_model)

    def move_row_in_model(self, current_index: int, new_index: int) -> None:
        """
        Moves a model's item.
        :param current_index: The row index being moved.
        :param new_index: The row index the item is being moved to.
        :return: None
        """
        self.model.values.insert(new_index, self.model.values.pop(current_index))
        self.logger.debug(f"Moved row index {current_index} to {new_index}")

    @Slot()
    def on_delete(self) -> None:
        """
        Deletes selected custom fields.
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_field Slot from {get_signal_sender(self)}"
        )
        indexes = self.list.selectedIndexes()

        # delete by value. Collect only the row values to delete
        row_values = []
        for index in indexes:
            field_value = self.model.values[index.row()]
            if field_value not in row_values:
                row_values.append(field_value)

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        for value in row_values:
            self.logger.debug(f"Deleted {value} from custom fields")
            self.model.values.remove(value)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        self.list.clear_selection()

    @Slot()
    def on_edit_component(self) -> None:
        """
        Opens the dialog to edit an existing component from the list.
        :return: None
        """
        current_index = self.list.selectionModel().selection().indexes()[0].row()

        model_value = self.model.values[current_index]
        # model component
        if isinstance(model_value, str):
            component_config = self._config_prop.config(model_value, as_dict=False)
        # component dictionary
        else:
            component_config = self._config_class(
                props=self.model.values[current_index]
            )

        dialog = ModelComponentPickerDialog(
            model_config=self.model_config,
            component_obj=component_config,
            component_type=self.component_type,
            additional_data={
                "index": current_index,
                "include_comp_key": self.include_component_key,
            },
            after_form_save=self.on_form_save,
            parent=self.dialog,
        )
        dialog.open()

    @Slot()
    def on_add_new_component(self) -> None:
        """
        Opens the dialog to add a new component to the list.
        :return: None
        """
        dialog = ModelComponentPickerDialog(
            model_config=self.model_config,
            component_obj=self._config_class(props={}),
            component_type=self.component_type,
            after_form_save=self.on_form_save,
            additional_data={
                "include_comp_key": self.include_component_key,
            },
            parent=self.dialog,
        )
        dialog.open()

    def on_form_save(
        self, form_data: str | dict[str, Any], additional_data: Any
    ) -> None:
        """
        Updates the parameter configuration object.
        :param form_data: The form data from ParameterPickerDialog or
        RecorderPickerDialogWidget.
        :param additional_data: A dictionary containing the index to update.
        :return: None
        """
        self.logger.debug(
            f"Running post-saving action on_form_save with value {form_data}"
        )
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()

        # update an existing parameter
        if additional_data is not None and "index" in additional_data:
            self.model.values[additional_data["index"]] = form_data
        # new parameter
        else:
            self.model.values.append(form_data)

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

        # disable buttons on change
        self.move_up.setEnabled(False)
        self.move_down.setEnabled(False)
        self.delete_button.setEnabled(False)

    def sanitise_value(
        self, value: list[int | float | str | dict]
    ) -> [list[dict | str], str | None]:
        """
        Sanitises the field value. The value is a list of parameters or recorders
        (as dictionaries or strings).
        :param value: The value to sanitise.
        :return: The list of component dictionaries or strings, and the warning message.
        """
        self.logger.debug(f"Sanitising value {value}")
        message = None
        _value = self.get_default_value()

        # check value
        if value is None:
            self.logger.debug("The value is not provided. Using default.")
        # value must be a list
        elif not isinstance(value, list):
            message = "The value provided in the model configuration is not valid"
            self.logger.debug(message)
        # the list must contain strings, dictionaries (ignore bool treated as int) or
        # numbers (for parameters only)
        elif (
            any([isinstance(el, bool) for el in value]) is True
            or (
                self.is_parameter
                and not all([isinstance(el, (float, dict, int, str)) for el in value])
            )
            or (
                self.is_recorder
                and not all([isinstance(el, (dict, str)) for el in value])
            )
        ):
            message = "The value provided in the model configuration can contain only "
            if self.is_parameter:
                message += f"numbers or valid {self.component_type} configurations"
            elif self.is_recorder:
                message += f"valid {self.component_type} configurations"
        else:
            # validate component as dictionaries - do not check if model component
            # exists when it is a string
            if not all(["type" in el for el in value if isinstance(el, dict)]):
                message = "The value provided in the model configuration must contain "
                message += f"valid {self.component_type} configurations"
                self.logger.debug(message)
            else:
                final_value = []
                for item in value:
                    # convert numbers to ConstantParameter
                    if self.is_parameter and isinstance(item, (float, int)):
                        final_value.append({"type": "constant", "value": item})
                    else:
                        final_value.append(item)

                # check that only specific component types are included
                if self.include_component_key is not None:
                    self.logger.debug(f"Checking {self.component_type} types")
                    valid_values = []
                    for comp in final_value:
                        comp_config = None
                        # model component
                        if isinstance(comp, str) and self._exist_config_method(comp):
                            comp_config = self._config_prop.config(comp, as_dict=False)
                        # anonymous component
                        elif isinstance(comp, dict):
                            comp_config = self._config_class(props=comp)

                        # check which parameter to include
                        # anonymous or model parameter
                        if (
                            comp_config is not None
                            and comp_config.key in self.include_component_key
                        ):
                            valid_values.append(comp)
                        # not accepted parameter type
                        else:
                            message = (
                                f"The type of one or more {self.component_type}s is "
                                "not valid and these were removed from the list. "
                                f"Allowed types are: "
                                + ", ".join(self.include_component_names)
                            )
                            self.logger.debug(
                                f"{comp} is not a valid {self.component_type}"
                            )
                            self.logger.debug(message)
                    _value = valid_values
                # components w/o type filter
                else:
                    # check that the model component exists
                    valid_values = []
                    for comp in final_value:
                        if isinstance(comp, str) and not self._exist_config_method(
                            comp
                        ):
                            message = (
                                f"One or more model {self.component_type}s do "
                                + "not exist and were removed from the list"
                            )
                            self.logger.debug(
                                f"The model {self.component_type} '{comp}' does not "
                                + "exist. Skipped"
                            )
                            continue
                        else:
                            valid_values.append(comp)
                    _value = valid_values

        return _value, message

    def get_default_value(self) -> list:
        """
        The field default value.
        :return: An empty list.
        """
        return []

    def get_value(self) -> list[dict | str]:
        """
        Returns the widget value.
        :return: A list containing dictionaries of component configurations and/or
        component names.
        """
        return self.model.values

    def validate(self, name: str, label: str, _: list[dict | str]) -> Validation:
        """
        Checks that the value is valid.
        :param name: The field name.
        :param label: The field label.
        :param _: The field value.
        :return: The Validation instance.
        """
        value = self.get_value()
        self.logger.debug(f"Validating field with {value}")

        # empty list
        if not value and self.is_mandatory:
            return Validation("The field cannot be empty")
        # skip validation if field is optional
        elif self.is_mandatory is False:
            return Validation()

        # model component does not exist
        for v in value:
            if isinstance(v, str) and self._exist_config_method(v) is False:
                return Validation(
                    f"The {self.component_type} named '{v}' does "
                    "not exist in the model configuration",
                )
        return Validation()

    def reset(self) -> None:
        """
        Resets the widget. This sets an empty list on the model.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.values = self.get_default_value()
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        self.list.clear_selection()

    @property
    def is_parameter(self) -> bool:
        """
        Returns True if the component type is a parameter.
        :return: True if the type is a parameter, False otherwise
        """
        return self.component_type == "parameter"

    @property
    def is_recorder(self) -> bool:
        """
        Returns True if the component type is a recorder.
        :return: True if the type is a recorder, False otherwise
        """
        return self.component_type == "recorder"
