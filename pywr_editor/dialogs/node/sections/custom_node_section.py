from typing import TYPE_CHECKING, Any

from pywr_editor.form import DictionaryWidget, FieldConfig, FormSection

if TYPE_CHECKING:
    from ..node_dialog_form import NodeDialogForm

"""
 This section allows setting up a custom node dictionary
 by providing key/value pairs.
"""


class CustomNodeSection(FormSection):
    def __init__(self, form: "NodeDialogForm", section_data: dict):
        """
        Initialises the form section for a custom node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form=form, section_data=section_data)

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="component_dict",
                        label="Dictionary",
                        field_type=DictionaryWidget,
                        value=form.node_dict.copy(),
                        help_text="Configure the node by providing its dictionary "
                        "keys and values",
                    ),
                    form.comment,
                ],
            }
        )

    def filter(self, form_data: dict[str, Any]) -> None:
        """
        Set the component type.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # unpack the dictionary items
        for key, value in form_data["component_dict"].items():
            form_data[key] = value
        del form_data["component_dict"]
