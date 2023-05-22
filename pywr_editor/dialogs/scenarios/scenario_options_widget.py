from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from pywr_editor.form import FormCustomWidget, FormField, Validation
from pywr_editor.model import ScenarioConfig
from pywr_editor.utils import Logging
from pywr_editor.widgets import PushButton, SpinBox, TableView

from .scenario_options_model import ScenarioOptionsModel

if TYPE_CHECKING:
    from .scenario_form_widget import ScenarioFormWidget


class ScenarioOptionsWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: dict[str, list[str] | list[int] | None],
        parent: FormField,
    ):
        """
        Initialises the widget containing the ensemble names and scenario slice.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)
        self.form: "ScenarioFormWidget"
        self.scenario_config = ScenarioConfig(self.form.scenario_dict)

        # Sanitise variables
        self.slice_value, self.slice_message = self.sanitise_slice(value["slice"])
        self.names_value, self.names_message = self.sanitise_names(
            value["ensemble_names"]
        )

        # Set table model
        self.model = ScenarioOptionsModel(
            slice_idx=self.slice_value,
            names=self.names_value,
            total_rows=self.scenario_config.size,
        )
        # noinspection PyUnresolvedReferences
        self.model.dataChanged.connect(self.form.on_field_changed)

        # Set table widget
        self.table = TableView(self.model)
        self.table.setMaximumHeight(400)
        self.table.setAlternatingRowColors(False)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 300)

        # Buttons
        reset_names = PushButton("Reset names", small=True)
        # noinspection PyUnresolvedReferences
        reset_names.clicked.connect(self.reset_names)
        check_all = PushButton("Check all", small=True)
        # noinspection PyUnresolvedReferences
        check_all.clicked.connect(self.check_all_ensembles)
        uncheck_all = PushButton("Uncheck all", small=True)
        # noinspection PyUnresolvedReferences
        uncheck_all.clicked.connect(self.uncheck_all_ensembles)

        button_layout = QHBoxLayout()
        button_layout.addWidget(reset_names)
        button_layout.addStretch()
        button_layout.addWidget(check_all)
        button_layout.addWidget(uncheck_all)

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render actions")

        # combine messages if needed from both variables
        warning_message = None
        if self.names_message and self.slice_message:
            warning_message = f"{self.names_message}. {self.slice_message}"
        elif self.names_message:
            warning_message = self.names_message
        elif self.slice_message:
            warning_message = self.slice_message

        self.form_field.set_warning_message(warning_message)

        # register Slot if scenario size changes
        size_field = self.form.find_field_by_name("size")
        # noinspection PyTypeChecker
        size_widget: SpinBox = size_field.findChild(SpinBox)
        # noinspection PyUnresolvedReferences
        size_widget.valueChanged.connect(self.on_scenario_resize)

    def sanitise_slice(self, value: list[int] | None) -> [list[int], str | None]:
        """
        Sanitises the slice value.
        :param value: The value to sanitise.
        :return: The final value and warning message.
        """
        self.logger.debug(f"Sanitising slice '{value}'")
        message = None
        final_value = []

        # if None or wrong type, return empty list
        if value is None:
            self.logger.debug("Slice not provided")
        elif not isinstance(value, list) or any(
            [isinstance(v, bool) or not isinstance(v, int) for v in value]
        ):
            message = "The slice is not a valid list of integers"
        elif len(value) > self.scenario_config.size:
            message = f"The slice length ({len(value)}) is larger than the "
            message += f"scenario size ({self.scenario_config.size})"
        elif max(value) > self.scenario_config.size:
            message = "One or more slice item is larger than the scenario "
            message += f"size ({self.scenario_config.size})"
        else:
            final_value = value

        if message is not None:
            self.logger.debug(message)

        return final_value, message

    def sanitise_names(self, value: list[str] | None) -> [list[str], str | None]:
        """
        Sanitises the ensemble names.
        :param value: The value to sanitise.
        :return: The final value.
        """
        self.logger.debug(f"Sanitising ensemble names '{value}'")
        message = None
        final_value = [""] * self.scenario_config.size

        # if None or empty, return empty list
        if value is None or value == []:
            self.logger.debug("Names list was not provided or was empty")
        elif not isinstance(value, list) or any(
            [not isinstance(v, str) for v in value]
        ):
            message = "The list of ensemble names must be a valid list of strings"
        elif len(value) != self.scenario_config.size:
            message = f"The number of ensemble names ({len(value)}) must match "
            message += f"the scenario size ({self.scenario_config.size})"
        else:
            final_value = value

        if message is not None:
            self.logger.debug(message)

        return final_value, message

    @Slot(int)
    def on_scenario_resize(self, new_size: int) -> None:
        """
        Resizes the model lists when the scenario size changes.
        :param new_size: The new scenario size.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()

        # add new empty names and check ensemble
        if new_size > self.model.total_rows:
            self.model.names += [""] * (new_size - self.model.total_rows)
            self.model.slice += list(range(self.model.total_rows, new_size))
        else:
            self.model.names = self.model.names[0:new_size]
            # remove all index > new_size
            self.model.slice = [
                slice_idx for slice_idx in self.model.slice if slice_idx < new_size
            ]

        self.model.total_rows = new_size
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    def get_value(self) -> dict[str, list[int | str]]:
        """
        Returns a dictionary with the ensemble names and slice.
        :return: The slice and ensemble names.
        """
        # empty slice if all ensembles are selected. Pywr runs
        # all ensembles by default
        if len(self.model.slice) == self.model.rowCount():
            slice_list = None
        else:
            slice_list = self.model.slice

        if all([name == "" for name in self.model.names]):
            names = []
        else:
            names = self.model.names
        return {"ensemble_names": names, "slice": slice_list}

    def validate(
        self, name: str, label: str, value: dict[str, list[int | str]] | None
    ) -> Validation:
        """
        Validates the field.
        :param name: The field name.
        :param label: The field name.
        :param value: The value. Not used.
        :return: The Validation instance.
        """
        # slice in the table cannot be empty
        if not self.model.slice:
            return Validation("You must select at least a scenario ensemble to run")

        # if no name is not provided, validation passes
        if all([not name for name in self.model.names]):
            return Validation()
        # if at least one name is given, all names are mandatory
        elif any([not name for name in self.model.names]):
            return Validation(
                "The ensemble names are optional, but if you provide at "
                "least one name, you must provide the names for all the ensembles",
            )

        return Validation()

    def reset(self) -> None:
        """
        Resets the widget. This removes all scenario names and checks all the
        checkboxes.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.slice = list(range(self.model.rowCount() + 1))
        self.model.names = []
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def reset_names(self) -> None:
        """
        Resets the ensemble names in the QTableView.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.names = [""] * self.model.total_rows
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def check_all_ensembles(self) -> None:
        """
        Selects all the ensemble to run.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.slice = list(range(self.model.rowCount()))
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def uncheck_all_ensembles(self) -> None:
        """
        De-selects all the ensemble to run.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.slice = []
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
