from typing import Callable, Any
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton, QWidget
from .dictionary_widget import DictionaryWidget
from pywr_editor.form import (
    FloatWidget,
    NodePickerWidget,
    ModelParameterPickerWidget,
    ModelRecorderPickerWidget,
    TableSelectorWidget,
    ScenarioPickerWidget,
    TableValuesWidget,
    DataTypeDictionaryItemWidget,
    Form,
)
from pywr_editor.model import ModelConfig
from pywr_editor.utils import Logging


class DictionaryItemFormWidget(Form):
    def __init__(
        self,
        model_config: ModelConfig,
        dict_key: str | None,
        dict_value: str | None,
        save_button: QPushButton,
        after_save: Callable[[str | dict[str, Any], Any], None] | None,
        parent: QWidget | None,
        additional_data: Any | None = None,
    ):
        """
        Initialises the form.
        :param model_config: The ModelConfig instance.
        :param dict_key: The dictionary key.
        :param dict_value: The dict_value key.
        :param save_button: The button used to save the form.
        :param after_save: A function to execute after the form is validated. This
        receives the form data as dictionary .
        :param parent: The parent modal.
        :param additional_data: Any additional data to store in the form. This is
        passed to the save_form callback.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        self.after_save = after_save
        self.additional_data = additional_data
        self.model_config = model_config
        self.default_label_1d = "Values"

        # convert values to dict for TableValuesWidget
        data_values_dict = {self.default_label_1d: []}
        empty_data_values_dict = data_values_dict.copy()
        if isinstance(dict_value, list):
            # 1D
            if all([isinstance(v, (float, int)) for v in dict_value]):
                data_values_dict = {self.default_label_1d: dict_value}
            elif all([isinstance(v, list) for v in dict_value]):
                if 2 <= len(dict_value) <= 3:
                    data_values_dict = {
                        f"Dimension {i+1}": dict_value[i]
                        for i in range(len(dict_value))
                    }

        available_fields = {
            "Dictionary item": [
                {"name": "key", "value": dict_key, "allow_empty": False},
                {
                    "name": "data_type",
                    "label": "Data type",
                    "field_type": DataTypeDictionaryItemWidget,
                    "value": dict_value,
                },
                {
                    "name": "field_bool",
                    "label": "Boolean value",
                    "field_type": "boolean",
                    "value": dict_value,
                },
                {
                    "name": "field_number",
                    "label": "Value",
                    "field_type": FloatWidget,
                    "value": dict_value,
                },
                {
                    "name": "field_node",
                    "label": "Node name",
                    "field_type": NodePickerWidget,
                    "value": dict_value,
                },
                {
                    "name": "field_parameter",
                    "label": "Parameter name",
                    "field_type": ModelParameterPickerWidget,
                    "value": dict_value,
                },
                {
                    "name": "field_recorder",
                    "label": "Recorder name",
                    "field_type": ModelRecorderPickerWidget,
                    "value": dict_value,
                },
                {
                    "name": "field_table",
                    "label": "Table name",
                    "field_type": TableSelectorWidget,
                    "field_args": {"static": True},
                    "value": dict_value,
                },
                {
                    "name": "field_scenario",
                    "label": "Scenario name",
                    "field_type": ScenarioPickerWidget,
                    "value": dict_value,
                },
                {
                    "name": "field_string",
                    "label": "String",
                    "value": dict_value,
                },
                {
                    "name": "field_1d_array",
                    "label": "1 dimensional array",
                    "field_type": TableValuesWidget,
                    "field_args": {"min_total_values": 1},
                    "value": data_values_dict
                    if len(data_values_dict) == 1
                    else empty_data_values_dict,
                },
                {
                    "name": "field_2d_array",
                    "label": "2 dimensional array",
                    "field_type": TableValuesWidget,
                    "field_args": {"min_total_values": 1},
                    "value": data_values_dict
                    if len(data_values_dict) == 2
                    else empty_data_values_dict,
                },
                {
                    "name": "field_3d_array",
                    "label": "3 dimensional array",
                    "field_type": TableValuesWidget,
                    "field_args": {"min_total_values": 1},
                    "value": data_values_dict
                    if len(data_values_dict) == 3
                    else empty_data_values_dict,
                },
                {
                    "name": "field_dict",
                    "label": "Dictionary",
                    "field_type": DictionaryWidget,
                    "value": dict_value,
                },
            ],
        }

        super().__init__(
            available_fields=available_fields,
            save_button=save_button,
            parent=parent,
            direction="vertical",
        )
        self.load_fields()
        save_button.setEnabled(True)

    @Slot()
    def on_save(self) -> None | bool:
        """
        Slot called when user clicks on the "Save" button. The form data are sent
        to self.after_save().
        :return: None
        """
        self.logger.debug("Saving form")

        form_data = self.validate()
        if form_data is False:
            self.logger.debug("Validation failed")
            return False

        # the url and table keys must be set up by enabling the external data toggle
        if form_data["key"] in ["url", "table"]:
            self.find_field_by_name("key").set_warning_message(
                "To configure external data using the 'url' or 'table' dictionary "
                "keys, you must use the External data toggle in the previous form"
            )
            return False

        # convert TableValuesWidget dictionary to array
        if "d_array" in form_data["data_type"]:
            field_name = f"field_{form_data['data_type']}"
            # 1D
            if form_data["data_type"] == "1d_array":
                form_data[field_name] = list(
                    form_data[field_name][self.default_label_1d]
                )
            # 2D and 3D
            else:
                array = []
                for var_values in form_data[field_name].values():
                    array.append(var_values)
                form_data[field_name] = array

        # callback function
        self.after_save(form_data, self.additional_data)
