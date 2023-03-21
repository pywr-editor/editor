from typing import Literal, Type

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QTreeWidgetItem

from pywr_editor.model import ModelConfig, ParameterConfig, RecorderConfig
from pywr_editor.style import Color
from pywr_editor.widgets import ParameterIcon, RecorderIcon

compType = Literal["parameter", "recorder"] | None


class AbstractTreeWidgetComponent:
    def __init__(
        self,
        comp_value: dict | list,
        model_config: ModelConfig,
        parent_type: Type[dict | list] = None,
        comp_type: compType = None,
        comp_name: str | None = None,
        parent: QTreeWidgetItem | None = None,
    ):
        """
        Initialises the tree item for a parameter or recorder.
        :param comp_value: The component value. This can be a dictionary, a list or a
        number for a ConstantParameter.
        :param model_config: The ModelConfig instance.
        :param parent_type: The type of parent item (dict or list).
        :param comp_type: The type of component ("parameter" or "recorder").
        :param comp_name: The component name. This is available only if the component
        is not anonymous (i.e. it is defined in the "parameters" or "recorders" section
        of the JSON file).
        :param parent: The component parent. This can be a node attribute or
        another component.
        """
        custom_parameter_keys = list(
            model_config.includes.get_custom_parameters().keys()
        )
        custom_recorder_keys = list(
            model_config.includes.get_custom_recorders().keys()
        )

        self.model_config = model_config
        self.items: list[QTreeWidgetItem] = []

        if isinstance(comp_value, dict):
            param_obj = ParameterConfig(comp_value)
            recorder_obj = RecorderConfig(comp_value)
            comp_obj = None  # comp_value is a plain dictionary

            # forced parameter or type is in Pywr built-in types or custom classes
            if comp_type == "parameter" or (
                "type" in comp_value
                and (
                    model_config.pywr_parameter_data.get_lookup_key(
                        param_obj.type
                    )
                    or param_obj.key in custom_parameter_keys
                )
                and "recorders" not in comp_value.keys()
            ):
                comp_obj = model_config.parameters.parameter(
                    config=comp_value, name=comp_name
                )
            # forced recorder or type is in Pywr built-in types or custom classes
            elif comp_type == "recorder" or (
                "type" in comp_value
                and (
                    model_config.pywr_recorder_data.get_lookup_key(
                        recorder_obj.type
                    )
                    or recorder_obj.key in custom_recorder_keys
                )
            ):
                comp_obj = model_config.recorders.recorder(
                    config=comp_value, name=comp_name
                )

            # if the value is a parameter or recorder add the type and icon
            # to the parent item
            if comp_obj:
                comp_key = comp_obj.key
                humanised_type = comp_obj.humanised_type

                # if the parent is a dictionary add to 2nd column
                column = 0
                if parent_type == dict:
                    column = 1
                # if the component is in a list add to 1st column
                elif parent_type == list:
                    column = 0

                parent.setText(column, humanised_type)
                parent.setToolTip(column, humanised_type)
                if comp_key is not None:
                    if isinstance(comp_obj, ParameterConfig):
                        parent.setIcon(column, QIcon(ParameterIcon(comp_key)))
                    elif isinstance(comp_obj, RecorderConfig):
                        parent.setIcon(column, QIcon(RecorderIcon(comp_key)))

            for key, value in comp_value.items():
                # never show the type as the type and icon has already been added
                if key == "type":
                    continue

                item = QTreeWidgetItem(parent)
                if comp_obj:
                    item.setText(0, comp_obj.humanise_attribute_name(key))
                else:
                    item.setText(0, str(key))

                # the value is a nested list or a dictionary
                if isinstance(value, (list, dict)):
                    sub_item = AbstractTreeWidgetComponent(
                        comp_value=value,
                        parent_type=type(value),
                        model_config=self.model_config,
                        parent=item,
                    )
                    item.addChildren(sub_item.items)
                # float, int, bool or string
                else:
                    self.add_string_to_item(
                        value=value, column=1, item=item, is_file=key == "url"
                    )
                self.items.append(item)
        # nested listed of components
        elif isinstance(comp_value, list):
            for (
                idx,
                value,
            ) in enumerate(comp_value):
                item = QTreeWidgetItem(parent)
                # parameter dictionary in a list (for example in AggregatedParameter)
                if isinstance(value, dict):
                    sub_item = AbstractTreeWidgetComponent(
                        comp_value=value,
                        parent_type=list,
                        model_config=self.model_config,
                        parent=item,
                    )
                    item.addChildren(sub_item.items)
                # float, int, bool or string
                else:
                    self.add_string_to_item(value=value, column=0, item=item)

                self.items.append(item)

    def add_string_to_item(
        self,
        value: str | int | float,
        column: int,
        item: QTreeWidgetItem,
        is_file: bool = False,
    ) -> None:
        """
        Add a string to a tree item.
        :param value: The string or number to add.
        :param column: The column item to add the string to.
        :param item: The tree item.
        :param is_file: Whether the string represent a file path. Default to False.
        :return None
        """
        label = item.text(0)
        item.setText(column, str(value))

        # the parameter contains the url key to fetch external data
        if is_file and self.model_config.does_file_exist(value) is False:
            item.setBackground(column, Color("red", 100).qcolor)
            item.setData(
                column, Qt.ItemDataRole.BackgroundRole, Color("red", 100).qcolor
            )
            item.setToolTip(column, f'The file "{value}" cannot be found')
        elif isinstance(value, str):
            item.setToolTip(column, value)
            # check if string is a model parameter. Add type to 2nd column
            if value in self.model_config.parameters.names:
                param_obj = self.model_config.parameters.get_config_from_name(
                    value, as_dict=False
                )
                param_type = param_obj.humanised_type

                # change label when the parameter is rendered outside
                # the parameter section
                if item.text(0) == "Parameter":
                    item.setText(1, value)
                else:
                    item.setText(1, param_type)
                item.setToolTip(1, f"Parameter of type {param_type}")
                item.setIcon(1, QIcon(ParameterIcon(param_obj.key)))
            # check if string is a model recorder
            elif value in self.model_config.recorders.names and label in [
                "Recorder",
                "Recorders",
            ]:
                recorder_obj = self.model_config.recorders.get_config_from_name(
                    value, as_dict=False
                )
                recorder_type = recorder_obj.humanised_type
                item.setText(1, value)
                item.setToolTip(1, f"Recorder of type {recorder_type}")
                item.setIcon(1, QIcon(RecorderIcon(recorder_obj.key)))
            # string is a model node
            elif value in self.model_config.nodes.names:
                node_obj = self.model_config.nodes.get_node_config_from_name(
                    value, as_dict=False
                )
                node_type = node_obj.humanised_type
                item.setText(1, f"{value} ({node_type})")
                item.setToolTip(1, f"Node of type {node_type}")
