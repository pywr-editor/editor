import operator
from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtCore import QSize, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from pywr_editor.form import (
    FormCustomWidget,
    FormField,
    FormValidation,
    ScenarioPickerWidget,
    ScenarioValuesModel,
    ScenarioValuesPickerDialogWidget,
)
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import ListView, PushIconButton

if TYPE_CHECKING:
    from pywr_editor.dialogs import ParameterDialogForm, ParametersDialog

"""
 Widget handling values for a scenario. The value is a
 list, containing a list for each scenario. There must
 be as many lists as the scenario size and each nested
 list must contain as many values as dictated by the
 data type (for example 12 for a monthly profile).
"""


class ScenarioValuesWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: list[list[int | float]] | None,
        parent: FormField,
        data_type: Literal[
            "daily_profile",
            "weekly_profile",
            "monthly_profile",
            "timestep_series",
        ],
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The list of parameters or numbers.
        :param parent: The parent widget.
        :param data_type: The data type. It can be one of the following: daily_profile,
        weekly_profile, monthly_profile or timestep_series.
        """
        self.form: "ParameterDialogForm"
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)

        # noinspection PyTypeChecker
        self.dialog: "ParametersDialog" = self.form.parent
        self.model_config = self.form.model_config
        self.scenario_size: int | None = None
        self.data_type = data_type

        self.logger.debug(f"Data type is {data_type}")
        if data_type == "daily_profile":
            self.min_ensemble_values = 366
        elif data_type == "weekly_profile":
            self.min_ensemble_values = 52
        elif data_type == "monthly_profile":
            self.min_ensemble_values = 12
        elif data_type == "timestep_series":
            self.min_ensemble_values = self.model_config.number_of_steps
        else:
            raise ValueError(f"The data type '{data_type}' is not supported")

        self.value, self.warning_message = self.sanitise_value(value)

        # # noinspection PyCallingNonCallable
        self.model = ScenarioValuesModel(values=self.value)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.connect(self.on_value_change)

        # Action buttons
        buttons_layout = QHBoxLayout()
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add", small=True
        )
        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_ensemble)
        self.add_button.setToolTip("Add a new ensemble")

        self.edit_button = PushIconButton(
            icon=":misc/edit",
            label="Edit",
            small=True,
            icon_size=QSize(10, 10),
        )
        self.edit_button.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.edit_button.clicked.connect(self.on_edit_ensemble)
        self.edit_button.setToolTip("Edit the values for the selected ensemble")

        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", small=True
        )
        self.delete_button.setDisabled(True)
        self.delete_button.setToolTip("Delete the selected ensemble values")
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_ensemble)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)

        # List
        self.list = ListView(
            model=self.model,
            toggle_buttons_on_selection=[self.delete_button, self.edit_button],
        )
        self.list.setMaximumHeight(100)

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
        self.form: ParameterDialogForm
        self.logger.debug("Registering post-render section actions")

        scenario_field = self.form.find_field_by_name("scenario")
        # noinspection PyTypeChecker
        scenario_widget: ScenarioPickerWidget = scenario_field.widget

        # update scenario size if a different scenario is selected
        # noinspection PyUnresolvedReferences
        scenario_widget.combo_box.currentIndexChanged.connect(
            self.on_update_scenario
        )

        # check that the list matches the size of the selected scenario
        scenario = scenario_field.value()
        if self.value and scenario is not None:
            self.scenario_size = (
                self.form.model_config.scenarios.get_size_from_name(scenario)
            )
            if self.scenario_size != len(self.value):
                new_message = "The value must contain as many ensembles as the "
                new_message += f"scenario size ({self.scenario_size})"
                if self.warning_message is not None:
                    self.warning_message = (
                        f"{new_message}. {self.warning_message}"
                    )
                else:
                    self.warning_message = new_message
                self.logger.debug(new_message)

        self.form_field.set_warning_message(self.warning_message)

    @Slot(int)
    def on_update_scenario(self) -> None:
        """
        Updates the scenario size, if a new scenario is selected.
        :return: None
        """
        self.form: ParameterDialogForm
        self.logger.debug(
            f"Running on_update_scenario Slot from {get_signal_sender(self)}"
        )

        scenario_field = self.form.find_field_by_name("scenario")
        self.scenario_size = (
            self.form.model_config.scenarios.get_size_from_name(
                scenario_field.value()
            )
        )
        self.form_field.clear_message()
        self.logger.debug(f"Updated scenario size with {self.scenario_size}")

    @Slot()
    def on_delete_ensemble(self) -> None:
        """
        Deletes the selected ensemble values.
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_ensemble Slot from {get_signal_sender(self)}"
        )
        indexes = self.list.selectedIndexes()
        row_indexes = [index.row() for index in indexes]

        # Preserve only the row values that are not selected
        new_values = []
        for index, sub_values in enumerate(self.model.values):
            if index not in row_indexes:
                new_values.append(sub_values)
            else:
                self.logger.debug(
                    f"Deleted index {index} with values {sub_values}"
                )

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.values = new_values
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        self.list.clear_selection()

    @Slot()
    def on_edit_ensemble(self) -> None:
        """
        Opens the dialog to edit the values of the selected ensemble from the list.
        :return: None
        """
        current_index = (
            self.list.selectionModel().selection().indexes()[0].row()
        )

        dialog = ScenarioValuesPickerDialogWidget(
            model_config=self.model_config,
            values=self.model.values[current_index],
            additional_data={
                "index": current_index,
                "ensemble_number": current_index + 1,
                "ensemble_index": current_index,
                "data_type": self.data_type,
                "min_ensemble_values": self.min_ensemble_values,
            },
            after_form_save=self.on_form_save,
            parent=self.dialog,
        )
        dialog.open()

    @Slot()
    def on_add_new_ensemble(self) -> None:
        """
        Opens the dialog to add new ensemble values.
        :return: None
        """
        dialog = ScenarioValuesPickerDialogWidget(
            model_config=self.model_config,
            additional_data={
                "ensemble_number": self.model.rowCount() + 1,
                "data_type": self.data_type,
                "min_ensemble_values": self.min_ensemble_values,
            },
            after_form_save=self.on_form_save,
            parent=self.dialog,
        )
        dialog.open()

    def on_form_save(
        self, form_data: dict[str, Any], additional_data: dict[str, Any]
    ) -> None:
        """
        Updates the values for a scenario ensemble.
        :param form_data: The form data from ScenarioValuesPickerDialogWidget.
        :param additional_data: A dictionary containing the model index for the
        ensemble to update.
        :return: None
        """
        self.logger.debug(
            f"Running post-saving action on_form_save with value {form_data}"
        )

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        values = form_data["values"]

        # update an existing ensemble
        if additional_data is not None and "ensemble_index" in additional_data:
            self.model.values[additional_data["ensemble_index"]] = values
        # new ensemble
        else:
            self.model.values.append(values)

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def on_value_change(self) -> None:
        """
        Enables the form button when the widget is updated.
        :return: None
        """
        self.logger.debug(
            f"Running on_value_change Slot from {get_signal_sender(self)}"
        )
        self.form.save_button.setEnabled(True)

    def sanitise_value(
        self, value: list[list[int | float]] | None
    ) -> [list[list[int | float]], str | None]:
        """
        Sanitises the field value. The value is a list with nested list of numbers.
        :param value: The value to sanitise.
        :return: The values and the warning message.
        """
        self.logger.debug(f"Sanitising value {value}")
        message = None
        _value = self.get_default_value()

        # check value
        if value is None:
            self.logger.debug("The value is not provided. Using default")
        # value must be a list
        elif not isinstance(value, list):
            message = (
                "The value provided in the model configuration must be a list"
            )
        # the list must contain list
        elif any([not isinstance(el, list) for el in value]) is True:
            message = "The value provided in the model configuration can contain only "
            message += "lists"
        # each nested list can contain only numbers
        elif any(
            [
                not (
                    not isinstance(val, bool) and isinstance(val, (float, int))
                )
                for sublist in value
                for val in sublist
            ]
        ):
            message = "All the ensemble values can contain only numbers"
        else:
            # timestep_series requires at least X values
            comp_op = (
                operator.lt
                if self.data_type == "timestep_series"
                else operator.ne
            )
            part_message = (
                "have at least"
                if self.data_type == "timestep_series"
                else "exactly have"
            )
            # check size of each nested list
            if any(
                [
                    comp_op(len(sublist), self.min_ensemble_values)
                    for sublist in value
                ]
            ):
                message = (
                    f"Each ensemble must {part_message} "
                    + f"{self.min_ensemble_values} numbers"
                )
            _value = value

        return _value, message

    def get_default_value(self) -> list:
        """
        The field default value.
        :return: An empty list.
        """
        return []

    def get_value(self) -> list[list[int | float]] | None:
        """
        Returns the widget value.
        :return: A list containing the values for each scenario.
        """
        return self.model.values

    def validate(
        self,
        name: str,
        label: str,
        value: list[list[int | float]] | None,
    ) -> FormValidation:
        """
        Checks that the value is valid.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value. Not used.
        :return: The FormValidation instance.
        """
        value = self.get_value()
        self.logger.debug(f"Validating field with {value}")
        is_timestep_series = self.data_type == "timestep_series"

        # empty list
        if not value:
            return FormValidation(
                validation=False,
                error_message="You must provide the values for the scenario",
            )
        # check size of each nested list
        elif not is_timestep_series and any(
            [len(sublist) != self.min_ensemble_values for sublist in value]
        ):
            return FormValidation(
                validation=False,
                error_message="Each ensemble must exactly have "
                f"{self.min_ensemble_values} numbers",
            )
        elif is_timestep_series and any(
            [len(sublist) < self.min_ensemble_values for sublist in value]
        ):
            return FormValidation(
                validation=False,
                error_message="Each ensemble must have at least "
                f"{self.min_ensemble_values} numbers",
            )
        elif self.scenario_size is not None and self.scenario_size != len(
            value
        ):
            return FormValidation(
                validation=False,
                error_message="The value must contain as many ensembles as the "
                f"scenario size ({self.scenario_size})",
            )

        return FormValidation(validation=True)

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
