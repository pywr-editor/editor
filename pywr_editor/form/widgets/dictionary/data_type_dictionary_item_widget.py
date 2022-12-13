from PySide6.QtCore import Slot
from typing import TYPE_CHECKING
from pywr_editor.form import AbstractStringComboBoxWidget, FormField
from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from .dictionary_item_form_widget import DictionaryItemFormWidget

"""
 Widget to select the data type of
 a dictionary value
"""


class DataTypeDictionaryItemWidget(AbstractStringComboBoxWidget):
    def __init__(self, name: str, value: str, parent: FormField):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The dictionary value
        :param parent: The parent widget.
        """
        # noinspection PyTypeChecker
        form: "DictionaryItemFormWidget" = parent.form
        self.model_config: ModelConfig = form.model_config

        labels_map = {
            "bool": "Boolean",
            "number": "Number",
            "node": "Node",
            "parameter": "Parameter",
            "recorder": "Recorder",
            "table": "Table",
            "scenario": "Scenario",
            "string": "String",
            # "list_str": "List of strings",
            "1d_array": "1D array",
            "2d_array": "2D array",
            "3d_array": "3D array",
            "dict": "Dictionary",
        }
        self.is_empty = value is None

        # Select the data type based on the dictionary value type
        data_type = None
        if isinstance(value, bool):
            data_type = "bool"
        elif isinstance(value, (float, int)):
            data_type = "number"
        elif isinstance(value, str):
            if value in self.model_config.nodes.names:
                data_type = "node"
            elif value in self.model_config.parameters.names:
                data_type = "parameter"
            elif value in self.model_config.recorders.names:
                data_type = "recorder"
            elif value in self.model_config.tables.names:
                data_type = "table"
            elif value in self.model_config.scenarios.names:
                data_type = "scenario"
            else:
                data_type = "string"
        elif isinstance(value, list):
            if all([isinstance(v, (float, int)) for v in value]):
                data_type = "1d_array"
            elif all([isinstance(v, list) for v in value]):
                if len(value) == 2:
                    data_type = "2d_array"
                elif len(value) == 3:
                    data_type = "3d_array"
            # elif all([isinstance(v, str) for v in value]):
            #     data_type = "list_str"
        elif isinstance(value, dict):
            data_type = "dict"

        self.data_type = data_type
        super().__init__(
            name=name,
            value=data_type,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value="number",
            keep_default=True,
        )

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        super().register_actions()

        # show/hide fields at init
        self.on_value_change()
        # show default value field when value is None
        if self.value is None:
            self.form.change_field_visibility(
                name="field_number",
                show=True,
            )

        # noinspection PyUnresolvedReferences
        self.combo_box.currentTextChanged.connect(self.on_value_change)

        # show warning if value is provided but its type is not recognised
        if (
            self.warning_message is None
            and not self.is_empty
            and self.data_type is None
        ):
            self.form_field.set_warning_message(
                "The type of data provided in the "
                "model configuration is not supported"
            )

    @Slot()
    def on_value_change(self) -> None:
        """
        Shows the correct field only when the data type is changed.
        :return: None
        """
        for data_type in self.labels_map.keys():
            self.form.change_field_visibility(
                name=f"field_{data_type}",
                show=data_type == self.get_value(),
            )
        dialog = self.form.parent
        dialog.resize(dialog.minimumSizeHint())
