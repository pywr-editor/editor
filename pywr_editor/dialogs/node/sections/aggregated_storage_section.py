from pywr_editor.form import FieldConfig, FormSection, MultiNodePickerWidget

from ..node_dialog_form import NodeDialogForm


class AggregatedStorageSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a AggregatedStorageSection.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        sub_class = "Storage"

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="storage_nodes",
                        value=form.field_value("storage_nodes"),
                        field_type=MultiNodePickerWidget,
                        field_args={
                            "include_node_keys": form.model_config.pywr_node_data.get_keys_with_parent_class(  # noqa: E501
                                sub_class
                            )
                            + form.model_config.includes.get_keys_with_subclass(
                                sub_class, "node"
                            ),
                            "is_mandatory": True,
                        },
                        help_text="Combine the absolute storage of the selected nodes",
                    ),
                    form.comment,
                ],
            }
        )
