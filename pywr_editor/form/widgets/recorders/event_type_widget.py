from typing import TYPE_CHECKING

from PySide6.QtCore import Slot

from pywr_editor.form import AbstractStringComboBoxWidget, FormField
from pywr_editor.model import ParameterConfig, RecorderConfig
from pywr_editor.utils import get_signal_sender

if TYPE_CHECKING:
    from pywr_editor.form import RecorderForm

"""
 Defines a widget to select the type of model component
 to trigger an EventRecorder. The form, the widget is added
 to, must have the "threshold_parameter" and "threshold_recorder"
 fields that handle the parameter and recorder respectively.
"""


class EventTypeWidget(AbstractStringComboBoxWidget):
    def __init__(
        self,
        name: str,
        value: float | int | str | dict,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The model component to trigger the event. This can be
        a parameter or recorder defined as string, number or dictionary.
        :param parent: The parent widget.
        """
        # noinspection PyTypeChecker
        form: "RecorderForm" = parent.form
        self.init = True

        # get component data
        model_config = form.model_config
        pywr_parameters = model_config.pywr_parameter_data
        custom_parameter_keys = list(
            model_config.includes.get_custom_parameters().keys()
        )
        pywr_recorders = model_config.pywr_recorder_data
        custom_recorder_keys = list(
            model_config.includes.get_custom_recorders().keys()
        )

        # default to parameter
        selected_type = "parameter"
        self.message = None

        # the value is a model component
        if isinstance(value, str):
            # find name in model parameters and recorder
            if value in model_config.parameters.names:
                selected_type = "parameter"
            elif value in model_config.recorders.names:
                selected_type = "recorder"
            else:
                self.message = (
                    f"The model component name '{value}', set in the model "
                    + "configuration, is not a model parameter or recorder"
                )
        # if a number, the type can only be parameter
        elif isinstance(value, (float, int)):
            selected_type = "parameter"
        # if dictionary, get the component kye
        elif isinstance(value, dict):
            # try with parameters first
            param_obj = ParameterConfig(value)
            recorder_obj = RecorderConfig(value)
            if (
                pywr_parameters.get_lookup_key(param_obj.type)
                or param_obj.key in custom_parameter_keys
            ):
                selected_type = "parameter"
            elif (
                pywr_recorders.get_lookup_key(recorder_obj.type)
                or recorder_obj.key in custom_recorder_keys
            ):
                selected_type = "recorder"
            else:
                self.message = (
                    "The model component type is not a valid model parameter "
                    + "or recorder. If you are using a custom component make "
                    + "sure to import the Python class first"
                )
        elif value is not None:
            self.message = (
                "The value in the model configuration must be a valid model "
                + "component (number, string or dictionary)"
            )

        super().__init__(
            name=name,
            value=selected_type,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map={
                "parameter": "Parameter",
                "recorder": "Recorder",
            },
            keep_default=True,
            default_value="parameter",
        )

        # add warning message
        if self.message:
            self.logger.debug(self.message)
            self.form_field.set_warning_message(self.message)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        super().register_actions()

        # change field visibility for the first time
        self.on_value_change()
        self.init = False

        # reset the parameter and recorder widgets on error
        if self.message:
            self.form.find_field_by_name("threshold_recorder").widget.reset()
            self.form.find_field_by_name("threshold_parameter").widget.reset()
        # reset only the widget whose type is not selected.
        # The form tries to load both widgets
        else:
            selected_value = self.get_value()
            if selected_value == "parameter":
                self.logger.debug("Resetting recorder field")
                self.form.find_field_by_name(
                    "threshold_recorder"
                ).widget.reset()
            elif selected_value == "recorder":
                self.logger.debug("Resetting parameter field")
                self.form.find_field_by_name(
                    "threshold_parameter"
                ).widget.reset()

        # connect slot to change visibility
        # noinspection PyUnresolvedReferences
        self.combo_box.currentTextChanged.connect(self.on_value_change)

    @Slot()
    def on_value_change(self) -> None:
        """
        Shows and hides fields based on the selected value in the ComboBox.
        :return: None
        """
        self.logger.debug(
            f"Running on_value_change Slot from {get_signal_sender(self)}"
        )

        selected_value = self.get_value()
        for field_name in ["threshold_parameter", "threshold_recorder"]:
            self.form.change_field_visibility(
                name=field_name,
                show=selected_value in field_name,
                clear_message=self.init is False,
            )
            # reset widget when the type is changed
            if not self.init:
                self.form.find_field_by_name(field_name).widget.reset()

    @staticmethod
    def store_threshold(form_dict: dict) -> None:
        """
        Method to use in the filter() method of a section to store the threshold
        depending on the selected type.
        :param form_dict: The form data.
        :return: None
        """
        if (
            form_dict["threshold_type"] == "parameter"
            and "threshold_parameter" in form_dict
        ):
            form_dict["threshold"] = form_dict["threshold_parameter"]
        elif (
            form_dict["threshold_type"] == "recorder"
            and "threshold_recorder" in form_dict
        ):
            form_dict["threshold"] = form_dict["threshold_recorder"]

        for field_name in [
            "threshold_type",
            "threshold_parameter",
            "threshold_recorder",
        ]:
            form_dict.pop(field_name, None)

    def reset(self) -> None:
        """
        Resets the ComboBox and the fields for the parameter and recorder.
        :return: None
        """
        super().reset()
        for field_name in ["threshold_parameter", "threshold_recorder"]:
            self.form.find_field_by_name(field_name).widget.reset()
