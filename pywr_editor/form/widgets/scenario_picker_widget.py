from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField, Validation
from pywr_editor.utils import Logging
from pywr_editor.widgets import ComboBox

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm


"""
 This widgets displays a list of available model
 scenarios and allows the user to pick one.
"""


class ScenarioPickerWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: list[Any],
        parent: FormField,
        is_mandatory: bool = True,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected node name.
        :param parent: The parent widget.
        :param is_mandatory: Whether the field must be provided or can be left empty.
        Default to True.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        super().__init__(name, value, parent)

        self.is_mandatory = is_mandatory
        self.form: "ModelComponentForm"
        self.model_config = self.form.model_config
        model_scenarios = self.model_config.scenarios
        scenario_names = model_scenarios.names

        # add recorder names with icon
        self.combo_box = ComboBox()
        self.combo_box.addItem("None", None)
        for name in scenario_names:
            size = model_scenarios.get_size(name)
            self.combo_box.addItem(f"{name} ({size} ensembles)", name)

        # set selected
        if not value:
            self.logger.debug("Value is None or empty. No value set")
        elif not isinstance(value, str):
            self.field.set_warning(
                "The scenario in the model configuration must be a string"
            )
        # name is in scenario names
        elif value in scenario_names:
            # find index by data
            selected_index = self.combo_box.findData(value, Qt.UserRole)
            self.combo_box.setCurrentIndex(selected_index)
        else:
            self.field.set_warning(
                f"The scenario named '{value}' does not exist in the model "
                "configuration"
            )

        # overwrite warning if there are no scenarios in the model
        if is_mandatory and len(scenario_names) == 0:
            self.combo_box.setEnabled(False)
            self.field.set_warning(
                "The are no scenarios defined in the model. Add a new scenario first "
                "before setting up this field"
            )

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

    def get_value(self) -> str | None:
        """
        Returns the selected scenario name.
        :return: The scenario name, None if nothing is selected
        """
        return self.combo_box.currentData()

    def validate(
        self,
        name: str,
        label: str,
        value: str | None,
    ) -> Validation:
        """
        Validates the value.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The instance of Validation
        """
        if self.get_value() is None and self.is_mandatory:
            return Validation("You must select a scenario")
        return Validation()

    def reset(self) -> None:
        """
        Reset the widget by selecting no node.
        :return: None
        """
        self.combo_box.setCurrentText("None")
