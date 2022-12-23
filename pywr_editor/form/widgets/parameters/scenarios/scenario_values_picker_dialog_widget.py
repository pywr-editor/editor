from typing import Any, Callable

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.form import (
    DailyValuesWidget,
    Form,
    FormCustomWidget,
    FormField,
    FormTitle,
    ModelComponentForm,
    MonthlyValuesWidget,
    TableValuesWidget,
    WeeklyValuesWidget,
)
from pywr_editor.model import ModelConfig
from pywr_editor.utils import Logging


class ScenarioValuesPickerDialogWidget(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        values: list[int | float] | None = None,
        after_form_save: Callable[[str | dict[str, Any], Any], None]
        | None = None,
        additional_data: Any | None = None,
        parent: QWidget | None = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The model configuration instance.
        :param values: The values.
        :param after_form_save: A function to execute after the form is saved.
        This receives the form data.
        :param additional_data: Any additional data to store in the form.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug("Loading dialog")
        self.after_form_save = after_form_save
        self.additional_data = additional_data

        # check parent
        if issubclass(parent.__class__, (Form, FormField, FormCustomWidget)):
            raise ValueError(
                "The parent cannot be a form component already instantiated"
            )

        # Dialog title and description
        title = FormTitle(
            f"Values for ensemble {additional_data['ensemble_number']}"
        )
        description = QLabel("Specify the values for the scenario ensemble")

        # Value widget
        data_type = additional_data["data_type"]
        widget_args = {}
        widget_values = values
        self.logger.debug(f"Using data type: {data_type}")
        if data_type == "daily_profile":
            widget_class = DailyValuesWidget
        elif data_type == "weekly_profile":
            widget_class = WeeklyValuesWidget
        elif data_type == "monthly_profile":
            widget_class = MonthlyValuesWidget
        elif data_type == "timestep_series":
            widget_class = TableValuesWidget
            widget_values = {"Values": values}
            widget_args = {
                "show_row_numbers": True,
                "row_number_label": "Timestep",
                "min_total_values": additional_data["min_ensemble_values"],
            }
        else:
            raise ValueError(f"The data type '{data_type}' is not supported")

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Close
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = button_box.findChild(QPushButton)
        save_button.setObjectName("save_button")
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)

        available_fields = {
            "Configuration": [
                {
                    "name": "values",
                    "field_type": widget_class,
                    "field_args": widget_args,
                    "value": widget_values,
                    "allow_empty": False,
                },
            ]
        }

        # Form
        self.form = ModelComponentForm(
            form_dict={},
            available_fields=available_fields,
            model_config=model_config,
            save_button=save_button,
            parent=self,
        )
        self.form.load_fields()
        save_button.setEnabled(True)
        # noinspection PyUnresolvedReferences
        button_box.accepted.connect(self.on_save)

        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.form)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle(title.text())
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumSize(600, 600)

    @Slot()
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Save" button.
        The form data are sent to self.after_save().
        :return: None
        """
        self.logger.debug("Saving form")

        form_data = self.form.save()
        if form_data is False:
            return

        # reduce dictionary to list if data_type is timestep_series
        if isinstance(form_data["values"], dict):
            form_data["values"] = form_data["values"]["Values"]
        # callback function
        self.after_form_save(form_data, self.additional_data)
