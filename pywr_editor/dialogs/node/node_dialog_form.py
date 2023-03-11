import ast
from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtWidgets import QGroupBox, QLineEdit, QPushButton

import pywr_editor.dialogs
from pywr_editor.form import (
    EdgeColorPickerWidget,
    FloatWidget,
    Form,
    FormValidation,
    NodeStylePickerWidget,
    ParameterLineEditWidget,
)
from pywr_editor.model import Constants, ModelConfig, NodeConfig
from pywr_editor.utils import Logging

from .sections.custom_node_section import CustomNodeSection

if TYPE_CHECKING:
    from pywr_editor.dialogs import NodeDialog
    from pywr_editor.form import FieldConfig

"""
 This forms allow editing a node configuration.
"""


class NodeDialogForm(Form):
    def __init__(
        self,
        node_dict: dict,
        model_config: ModelConfig,
        save_button: QPushButton,
        parent: "NodeDialog",
    ):
        """
        Initialises the form.
        :param node_dict: A dictionary containing the node configuration.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        self.dialog = parent
        self.model_config = model_config
        self.node_dict = node_dict
        self.node_obj = NodeConfig(node_dict)
        self.node_type = self.node_obj.type

        # the node type cannot be changed for built-in nodes or custom nodes that
        # have been imported
        self.can_type_be_changed = (
            not model_config.pywr_node_data.does_type_exist(self.node_type)
            and self.node_type
            not in model_config.includes.get_custom_nodes().keys()
        )
        self.logger.debug(f"Loading with {self.node_dict}")

        # main fields
        if model_config.pywr_node_data.does_type_exist(self.node_type):
            node_type_field = self.node_obj.humanised_type
        else:
            node_type_field = self.node_type

        main_fields: list[FieldConfig] = [
            {
                "name": "name",
                "value": self.node_obj.name,
                "allow_empty": False,
                "validate_fun": self.check_unique_name,
            },
            {
                "name": "type",
                "value": node_type_field,
                "validate_fun": self.check_node_class,
            },
            {
                "name": Constants.NODE_STYLE_KEY.value,
                "value": self.node_obj,
                "field_type": NodeStylePickerWidget,
                "help_text": "Change the appearance of the node on the schematic",
            },
        ]
        if not self.node_obj.is_virtual:
            main_fields.append(
                {
                    "name": Constants.EDGE_COLOR_KEY.value,
                    "field_type": EdgeColorPickerWidget,
                    "value": self.node_obj.edge_color,
                    "help_text": "The colour of the edges to the target nodes",
                }
            )

        # load section based on node type - sections are node loaded dynamically like
        # for recorders or parameters, because type cannot be changed
        pywr_class = self.model_config.pywr_node_data.get_class_from_type(
            self.node_type
        )
        section_data = {}

        # custom component
        if pywr_class is None:
            self.logger.debug(f"'{self.node_type}' is custom")
            # imported Python class
            if (
                self.node_type
                in self.model_config.includes.get_custom_nodes().keys()
            ):
                self.logger.debug(
                    f"{self.node_type.title()} is included as custom import"
                )
                section_data["imported"] = True
            # unknown class
            else:
                self.logger.debug(
                    f"{self.node_type.title()} is not included as custom import"
                )
            self.logger.debug("Adding section for 'NodeCustomSection'")
            section_class = CustomNodeSection
        # pywr built-in node
        elif hasattr(pywr_editor.dialogs, f"{pywr_class}Section"):
            section_class = getattr(pywr_editor.dialogs, f"{pywr_class}Section")
        else:
            raise ValueError(f"Cannot find form section for '{self.node_type}'")

        super().__init__(
            available_fields={"Node": main_fields},
            save_button=save_button,
            parent=parent,
            direction="vertical",
        )
        self.load_fields()
        self.add_section_from_class(section_class, section_data)

        # remove the border and padding from the first box
        # noinspection PyTypeChecker
        first_section: QGroupBox = self.findChild(QGroupBox, "Node")
        first_section.setTitle("")
        first_section.setStyleSheet(
            "QGroupBox{border:0;padding:0;padding-top:15px; margin-top:-15px}"
        )

        # disable type field
        if not self.can_type_be_changed:
            type_widget = self.find_field_by_name("type").widget
            type_widget.setDisabled(True)
            type_widget.setToolTip("The node type cannot be changed")

    def check_node_class(
        self, name: str, label: str, value: str
    ) -> FormValidation:
        """
        Checks the node type is a valid Python class name.
        :param name: The field name.
        :param label: The field label.
        :param value: THe field value.
        :return: The validation instance.
        """
        type_widget: QLineEdit = self.find_field_by_name("type").widget
        if not type_widget.isEnabled():
            return FormValidation(validation=True)

        class_definition = f"class {value}: pass"
        # noinspection PyBroadException
        try:
            ast.parse(class_definition)
            return FormValidation(validation=True)
        except Exception:
            return FormValidation(
                validation=False,
                error_message="The type must be a valid Python class",
            )

    def get_node_dict_value(self, key: str) -> Any:
        """
        Gets a value from the dictionary containing the node data.
        :param key: The key to extract the value of.
        :return: The value or empty if the key is not set.
        """
        return super().get_dict_value(key, self.node_dict)

    def save(self) -> dict | bool:
        """
        Validates the form and return the form dictionary.
        :return: The form dictionary or False if the validation fails.
        """
        self.logger.debug("Saving form")

        form_data = self.validate()
        if form_data is False:
            self.logger.debug("Validation failed")
            return False

        new_name = form_data["name"]
        if form_data["name"] != self.node_obj.name:
            # update the model configuration
            self.model_config.nodes.rename(self.node_obj.name, new_name)
            # update the dialog title
            self.dialog.title.update_name(new_name)

        # get type from field if it can be changed
        type_widget: QLineEdit = self.find_field_by_name("type").widget
        if type_widget.isEnabled():
            form_data["type"] = type_widget.text()
        else:
            form_data["type"] = self.node_obj.type

        # set type
        self.model_config.nodes.update(form_data)

        # update the schematic, tree and status bar
        app = self.dialog.app
        if app is not None:
            if hasattr(app, "schematic"):
                app.schematic.reload()
            if hasattr(app, "components_tree"):
                app.components_tree.reload()
            if hasattr(app, "statusBar"):
                app.statusBar().showMessage(f'Updated node "{new_name}"')

        return form_data

    def check_unique_name(
        self, name: str, label: str, value: str
    ) -> FormValidation:
        """
        Checks that the node name is unique.
        :param name: The filed name.
        :param label: The field label.
        :param value: The node name.
        :return: The validation instance.
        """
        if (
            value != self.node_obj.name
            and value in self.model_config.nodes.names
        ):
            return FormValidation(
                validation=False, error_message="The node name already exists"
            )
        return FormValidation(validation=True)

    @property
    def min_flow_field(self) -> dict[str, Any]:
        """
        Returns the form field representing the minimum flow through the node.
        :return: A dictionary with the field configuration
        """
        return {
            "name": "min_flow",
            "label": "Minimum flow",
            "field_type": ParameterLineEditWidget,
            "field_args": {"is_mandatory": False},
            "value": self.get_node_dict_value("min_flow"),
            "help_text": "The minimum flow constraint on the node. When it is "
            + "not set, it defaults to 0.",
        }

    @property
    def max_flow_field(self) -> dict[str, Any]:
        """
        Returns the form field representing the maximum flow through the node.
        :return: A dictionary with the field configuration
        """
        return {
            "name": "max_flow",
            "label": "Maximum flow",
            "field_type": ParameterLineEditWidget,
            "field_args": {"is_mandatory": False},
            "value": self.get_node_dict_value("max_flow"),
            "help_text": "The maximum flow constraint on the node. When it is "
            + "not set, it defaults to infinite.",
        }

    def cost_field(
        self, node_type: Literal["flow", "storage"]
    ) -> dict[str, Any]:
        """
        Returns the form field representing the cost of node.
        :param node_type: The type of node (flow or storage).
        :return: A dictionary with the field configuration
        """
        if node_type == "flow":
            help_text = "The cost per unit flow through the node. The cost "
            help_text += "drives the model behaviour. A positive value is  "
            help_text += "usually associated with supplied nodes whereas a "
            help_text += "negative cost (or benefit) is set for demand nodes. "
            help_text += "Default to 0 (for neutral cost)"
        elif node_type == "storage":
            help_text = "The cost of the net flow of the storage node. "
            help_text += "The cost drives the model behaviour. A positive "
            help_text += "value penalises increasing volumes (by assigning a "
            help_text += "benefit to released flow) whereas a negative "
            help_text += "cost penalises decreasing volumes (benefit is given "
            help_text += "to inflow)"
        else:
            raise ValueError(
                f"node_type can only be node or storage. '{node_type}' given"
            )

        return {
            "name": "cost",
            "field_type": ParameterLineEditWidget,
            "field_args": {"is_mandatory": False},
            "default_value": 0,
            "value": self.get_node_dict_value("cost"),
            "help_text": help_text,
        }

    @property
    def comment(self) -> dict[str, Any]:
        """
        Returns the form configuration for the "comment" field.
        :return: The field dictionary.
        """
        return {
            "name": "comment",
            "value": self.get_node_dict_value("comment"),
        }

    @property
    def initial_volume_field(self) -> dict[str, Any]:
        """
        Returns the form configuration for the "initial_volume" field.
        :return: The field dictionary.
        """
        return {
            "name": "initial_volume",
            "value": self.get_node_dict_value("initial_volume"),
            "field_type": FloatWidget,
            "help_text": "The initial absolute volume for the storage",
        }

    @property
    def initial_volume_pc_field(self) -> dict[str, Any]:
        """
        Returns the form configuration for the "initial_volume_pc" field.
        :return: The field dictionary.
        """
        return {
            "name": "initial_volume_pc",
            "label": "Initial volume",
            "value": self.get_node_dict_value("initial_volume_pc"),
            "field_type": FloatWidget,
            "validate_fun": self.validate_initial_volume_pc,
            "help_text": "The relative volume for the storage. This is a number "
            + "between 0 (when empty) and 1 (when full)",
        }

    @staticmethod
    def validate_initial_volume_pc(
        name: str, label: str, value: float | int
    ) -> FormValidation:
        """
        Checks that the relative storage is a number between 0 and 1.
        :param name: The field name.
        :param label: The field label.
        :param value: The storage.
        :return: The validation instance.
        """
        if value and not 0 <= value <= 1:
            return FormValidation(
                validation=False,
                error_message="The relative storage must be a number between 0 and 1",
            )
        return FormValidation(validation=True)
