from typing import Type

from pywr_editor.form import (
    FloatWidget,
    FormSection,
    NodePickerWidget,
    StoragePickerWidget,
    ThresholdRelationSymbolWidget,
    ThresholdValuesWidget,
)
from pywr_editor.utils import Logging

from ..recorder_dialog_form import RecorderDialogForm

"""
  Abstract section class to use for node threshold
  recorders.
"""


class AbstractThresholdRecorderSection(FormSection):
    def __init__(
        self,
        form: RecorderDialogForm,
        section_data: dict,
        log_name: str,
        node_widget: Type[NodePickerWidget | StoragePickerWidget],
    ):
        """
        Initialises the form section for node threshold recorders.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param node_widget: The widget to use to select the node.
        :param log_name: The name to use in the logger.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(log_name)
        self.node_widget = node_widget

        if node_widget == NodePickerWidget:
            self.node_value_type = "flow"
        elif node_widget == StoragePickerWidget:
            self.node_value_type = "storage"
        else:
            raise ValueError(
                "The node widget can only be of type NodePickerWidget "
                + "or StoragePickerWidget"
            )

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.logger.debug("Registering form")
        self.form: RecorderDialogForm

        data_dict = {
            "Configuration": [
                {
                    "name": "threshold",
                    "field_type": FloatWidget,
                    "value": self.form.get_recorder_dict_value("threshold"),
                    "help_text": f"Compare the {self.node_value_type} of the node "
                    + "provided below against the constant threshold",
                },
                {
                    "name": "node",
                    "field_type": self.node_widget,
                    "value": self.form.get_recorder_dict_value("node"),
                },
                {
                    "name": "predicate",
                    "label": "Relation symbol",
                    "field_type": ThresholdRelationSymbolWidget,
                    "value": self.form.get_recorder_dict_value("predicate"),
                    "help_text": "This defines the predicate, which is the node's"
                    + f"{self.node_value_type}, followed by the relation symbol, "
                    + "followed by the threshold. For example, if the symbol is '>', "
                    + "Pywr  will assess the following predicate: "
                    + f"{self.node_value_type} > threshold",
                },
                {
                    "name": "values",
                    "field_type": ThresholdValuesWidget,
                    "value": self.form.get_recorder_dict_value("values"),
                    "help_text": "If the predicate is false, this recorder will "
                    + "return  the left value above, otherwise the right value "
                    + "will be used",
                },
            ],
        }

        return data_dict
