from typing import Any

from pywr_editor.form import (
    FieldConfig,
    FormSection,
    MultiNodePickerWidget,
    ParametersListPickerWidget,
    Validation,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class WeightedAverageProfileParameterSection(FormSection):
    """
    This defines the section for a WeightedAverageProfileParameter
    """

    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict[str, Any],
    ):
        """
        Initialises the form section.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)
        self.form: ParameterDialogForm

        self.allowed_keys = []
        for param in [
            "ConstantParameter",
            "DailyProfileParameter",
            "MonthlyProfileParameter",
        ]:
            self.allowed_keys += self.form.model_config.pywr_parameter_data.keys_with_parent_class(  # noqa: E501
                param, include_parent=True
            )
            self.allowed_keys += self.form.model_config.includes.get_keys_with_subclass(
                param, "parameter"
            )

        self.form: ParameterDialogForm
        sub_class = "Storage"
        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="storages",
                        label="Storage nodes",
                        field_type=MultiNodePickerWidget,
                        field_args={
                            "is_mandatory": True,
                            "include_node_keys": self.form.model_config.pywr_node_data.keys_with_parent_class(  # noqa: E501
                                sub_class
                            )
                            + self.form.model_config.includes.get_keys_with_subclass(
                                sub_class, "node"
                            ),
                        },
                        value=self.form.field_value("storages"),
                        help_text="This parameter calculates a daily profile by "
                        "weighting the profile values provided below with the "
                        "maximum storage of the nodes. The storage nodes and the "
                        "profiles are paired as they appear in the lists",
                    ),
                    FieldConfig(
                        name="profiles",
                        field_type=ParametersListPickerWidget,
                        field_args={"include_param_key": self.allowed_keys},
                        validate_fun=self.check_profiles,
                        value=self.form.field_value("profiles"),
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

    def check_profiles(
        self,
        name: str,
        label: str,
        value: list[str | dict | float | int],
    ) -> Validation:
        """
        Checks that the number of profiles equals the number of storage nodes.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        nodes_widget: MultiNodePickerWidget = self.form.find_field("storages").widget
        selected_nodes = nodes_widget.get_value()
        if len(selected_nodes) and len(value) and len(value) != len(selected_nodes):
            return Validation(
                f"The number of profiles ({len(value)}) must equal the "
                f"number of selected nodes ({len(selected_nodes)})",
            )

        return Validation()
