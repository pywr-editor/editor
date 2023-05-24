from typing import Type

from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    NodePickerWidget,
    StoragePickerWidget,
    ThresholdRelationSymbolWidget,
    ThresholdValuesWidget,
)

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
        node_widget: Type[NodePickerWidget | StoragePickerWidget],
    ):
        """
        Initialises the form section for node threshold recorders.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param node_widget: The widget to use to select the node.
        """
        super().__init__(form, section_data)

        if node_widget == NodePickerWidget:
            self.node_value_type = "flow"
        elif node_widget == StoragePickerWidget:
            self.node_value_type = "storage"
        else:
            raise ValueError(
                "The node widget can only be of type NodePickerWidget "
                + "or StoragePickerWidget"
            )

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="threshold",
                        field_type=FloatWidget,
                        value=form.field_value("threshold"),
                        help_text=f"Compare the {self.node_value_type} of the node "
                        "provided below against the constant threshold",
                    ),
                    FieldConfig(
                        name="node",
                        field_type=node_widget,
                        value=form.field_value("node"),
                    ),
                    FieldConfig(
                        name="predicate",
                        label="Relation symbol",
                        field_type=ThresholdRelationSymbolWidget,
                        value=form.field_value("predicate"),
                        help_text="This defines the predicate, which is the node's"
                        f"{self.node_value_type}, followed by the relation symbol, "
                        "followed by the threshold. For example, if the symbol is '>', "
                        "Pywr  will assess the following predicate: "
                        f"{self.node_value_type} > threshold",
                    ),
                    FieldConfig(
                        name="values",
                        field_type=ThresholdValuesWidget,
                        value=form.field_value("values"),
                        help_text="If the predicate is false, this recorder will "
                        "return  the left value above, otherwise the right value "
                        "will be used",
                    ),
                ],
            }
        )
