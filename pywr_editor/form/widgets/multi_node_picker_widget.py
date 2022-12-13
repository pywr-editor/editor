from typing import Union, TYPE_CHECKING
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from pywr_editor.utils import Logging
from pywr_editor.widgets import CheckableComboBox
from pywr_editor.form import (
    FormField,
    FormCustomWidget,
    FormValidation,
)

if TYPE_CHECKING:
    from pywr_editor.dialogs import (
        NodeDialogForm,
        ParameterDialogForm,
        RecorderDialogForm,
    )

"""
 This widgets displays a list of available model nodes
 and allows the user to select multiple nodes.
"""


class MultiNodePickerWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: list[str] | None,
        parent: FormField,
        is_mandatory: bool = False,
        include_node_keys: list[str] | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected node names.
        :param parent: The parent widget.
        :param is_mandatory: Whether at least one node should be provided or the
        field can be left empty. Default to False.
        :param include_node_keys: A list of strings representing node keys to only
        include in the widget. For example "storage" to include nodes inheriting
        from the Storage class only. An error will be shown if a not allowed
        type is used as value.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        self.logger.debug(f"Using the following keys {include_node_keys}")
        super().__init__(name, value, parent)

        self.is_mandatory = is_mandatory
        self.form: Union[
            "NodeDialogForm", "ParameterDialogForm", "RecorderDialogForm"
        ]
        self.model_config = self.form.model_config

        # Collect all pywr and custom node types
        all_nodes = {
            **self.model_config.pywr_node_data.nodes_data,
            **self.model_config.includes.get_custom_nodes(),
        }

        # check if the type exists
        self.include_node_types = None
        if include_node_keys:
            for node_type in include_node_keys:
                if node_type not in all_nodes.keys():
                    raise ValueError(
                        f"The node type '{node_type}' does not exist. Available "
                        + f"types are: {', '.join(all_nodes.keys())}"
                    )
            self.logger.debug(
                f"Including only the following node keys: {include_node_keys}"
            )
            # prettified types
            self.include_node_types = list(
                map(
                    self.model_config.pywr_node_data.humanise_name,
                    include_node_keys,
                )
            )

        # add node names
        self.combo_box = CheckableComboBox()
        model_nodes = self.model_config.nodes.names

        for name in model_nodes:
            node_obj = self.model_config.nodes.get_node_config_from_name(
                node_name=name, as_dict=False
            )

            # filter node types
            if (
                include_node_keys is not None
                and node_obj.type not in include_node_keys
            ):
                continue

            self.combo_box.addItem(
                f"{name} ({node_obj.humanise_node_type})", name
            )

        # set selected
        if not value:
            self.logger.debug("Value is None or empty. No value set")
        # there are no nodes in the model
        elif len(self.combo_box.all_items) == 0:
            message = "There are no nodes available"
            self.logger.debug(message)
            self.form_field.set_warning_message(
                message
                + ". Add a new node first, before setting up this option"
            )
        # value must be a list of strings
        elif not isinstance(value, list):
            message = "The node names must be a list"
            self.form_field.set_warning_message(message)
            self.logger.debug(message + ". None selected")
        elif not all([isinstance(n, str) for n in value]):
            message = "The node names must be valid strings"
            self.form_field.set_warning_message(message)
            self.logger.debug(message + ". None selected")
        else:
            wrong_node_types = []
            non_existing_nodes = []
            selected_indexes = []

            # check that names exists
            for node_name_value in value:
                node_obj = self.model_config.nodes.get_node_config_from_name(
                    node_name=node_name_value, as_dict=False
                )
                # filter node types
                if (
                    include_node_keys is not None
                    and node_obj.type not in include_node_keys
                ):
                    wrong_node_types.append(node_name_value)
                    continue

                index = self.combo_box.findData(node_name_value, Qt.UserRole)
                if index != -1:
                    self.logger.debug(
                        f"Selecting index #{index} for '{node_name_value}'"
                    )
                    selected_indexes.append(index)
                else:
                    non_existing_nodes.append(node_name_value)

            # select valid names
            self.combo_box.check_items(selected_indexes, False)

            if wrong_node_types:
                message = (
                    f"The following node names were removed from the list because "
                    f"their type is not allowed: {', '.join(wrong_node_types)}"
                    f" Allowed types are: {', '.join(self.include_node_types)}"
                )
                self.logger.debug(message)
                self.form_field.set_warning_message(message)
            elif non_existing_nodes:
                message = (
                    "The following node names do not exist in the model "
                    + f"configuration: {', '.join(non_existing_nodes)}"
                )
                self.logger.debug(message)
                self.form_field.set_warning_message(message)

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

    def get_value(self) -> list[str] | None:
        """
        Returns the selected node names.
        :return: The node names, None if nothing is selected
        """
        values = self.combo_box.checked_items(use_data=True)
        if values:
            return values
        return None

    def reset(self) -> None:
        """
        Reset the widget by selecting no node.
        :return: None
        """
        self.combo_box.uncheck_all()

    def validate(
        self, name: str, label: str, value: list[str]
    ) -> FormValidation:
        """
        Checks that the value is valid.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The FormValidation instance.
        """
        self.logger.debug(f"Validating field with {value}")

        # empty list
        if not value and self.is_mandatory:
            return FormValidation(
                validation=False,
                error_message="The field cannot be empty",
            )
        return FormValidation(validation=True)