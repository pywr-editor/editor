from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField, Validation
from pywr_editor.utils import Logging
from pywr_editor.widgets import ComboBox

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm


"""
 This widgets displays a list of available model nodes
 and allows the user to pick one.
"""


class AbstractModelNodePickerWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
        log_name: str,
        is_mandatory: bool = True,
        include_node_types: str | list[str] | None = None,
        exclude_node_types: str | list[str] | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected node name.
        :param parent: The parent widget.
        :param log_name: The name to use in the logger.
        :param is_mandatory: Whether the field must be provided or can be left empty.
        Default to True.
        :param include_node_types: A string or list of strings representing a node key
        to only include in the widget. For example storage for the Storage node to
        include only storage nodes; all other node types will not be shown.
        :param exclude_node_types: A string or list of strings representing a node key
        to exclude from the widget.
        """
        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with value {value}")
        super().__init__(name, value, parent)
        self.form: "ModelComponentForm"

        self.is_mandatory = is_mandatory
        self.model_config = self.form.model_config
        model_nodes = list(self.model_config.nodes.names)

        # include nodes
        nodes_data = self.model_config.pywr_node_data
        if include_node_types is not None:
            if isinstance(include_node_types, str):
                include_node_types = [include_node_types]
            # convert to lowercase
            include_node_types = [key.lower() for key in include_node_types]

            # check if node type exists
            for node_type in include_node_types:
                if node_type not in nodes_data.keys:
                    raise ValueError(
                        f"The node type {node_type} does not exist. Available types "
                        + f"are: {', '.join(nodes_data.keys)}"
                    )
            self.logger.debug(
                f"Including only the following node keys: {include_node_types}"
            )

        # exclude nodes
        if exclude_node_types is not None:
            if isinstance(exclude_node_types, str):
                exclude_node_types = [exclude_node_types]
            # convert to lowercase
            exclude_node_types = [key.lower() for key in exclude_node_types]

            # check if node type exists
            for node_type in exclude_node_types:
                if node_type not in nodes_data.keys:
                    raise ValueError(
                        f"The node type {node_type} does not exist. Available types "
                        + f"are: {', '.join(nodes_data.keys)}"
                    )
            self.logger.debug(
                f"Excluding the following node keys: {include_node_types}"
            )

        # add node names
        self.combo_box = ComboBox()
        valid_model_nodes = []
        for name in model_nodes:
            node_obj = self.model_config.nodes.config(node_name=name, as_dict=False)
            node_type = node_obj.key
            # filter nodes
            if include_node_types is not None and node_type not in include_node_types:
                continue
            if exclude_node_types is not None and node_type in exclude_node_types:
                continue

            valid_model_nodes.append(name)
            self.combo_box.addItem(f"{name} ({node_obj.humanised_type})", name)

        # sort node alphabetically
        self.combo_box.model().sort(0)
        # place default value at the top
        self.combo_box.insertItem(0, "None", None)
        self.combo_box.setCurrentIndex(0)

        # set selected
        if value is None or value == "":
            self.logger.debug("Value is None or empty. No value set")
        elif not isinstance(value, str):
            message = "The node name must be a string"
            self.field.set_warning(message)
            self.logger.debug(message + ". None selected")
        # name is in model nodes
        elif value in model_nodes:
            # valid type
            if value in valid_model_nodes:
                self.logger.debug(f"Setting '{value}' as selected node")
                # find node index by data
                selected_index = self.combo_box.findData(value, Qt.UserRole)
                self.combo_box.setCurrentIndex(selected_index)
            # type is wrong if filters are set
            else:
                message = "The node type set in the model configuration is not valid"
                self.field.set_warning(message)
                self.logger.debug(message + ". None selected")
        else:
            message = (
                f"The node named '{value}' does not exist in the model "
                + "configuration"
            )
            self.logger.debug(message)
            self.field.set_warning(message)

        # overwrite warning if there are no nodes in the model
        if len(self.combo_box.all_items) == 1:
            message = "There are no nodes available"
            self.logger.debug(message)
            self.field.set_warning(
                message + ". Add a new node first before setting up this option"
            )

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

    def get_value(self) -> str | None:
        """
        Returns the selected node name.
        :return: The node name.,None if nothing is selected
        """
        return self.combo_box.currentData()

    def validate(self, name: str, label: str, value: str) -> Validation:
        """
        Validates the value.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The instance of Validation
        """
        if self.get_value() is None and self.is_mandatory:
            return Validation("You must select a model node")
        return Validation()

    def reset(self) -> None:
        """
        Reset the widget by selecting no node.
        :return: None
        """
        self.combo_box.setCurrentText("None")
