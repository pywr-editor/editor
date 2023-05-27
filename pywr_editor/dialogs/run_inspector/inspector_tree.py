import inspect
from typing import TYPE_CHECKING, Any, Tuple

import numpy as np
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem
from pywr.model import Model
from pywr.parameters import Parameter
from pywr.recorders import Recorder

from pywr_editor.model import ModelConfig, ParameterConfig
from pywr_editor.node_shapes import get_node_icon, get_pixmap_from_type
from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.utils import humanise_label
from pywr_editor.widgets import ParameterIcon, RecorderIcon

if TYPE_CHECKING:
    from inspector_dialog import InspectorDialog

"""
 Tree widget to display the attributes of pywr
 nodes, parameters and recorders from a model run
 for a given timestep.
"""


class InspectorTree(QTreeWidget):
    def __init__(
        self,
        model_config: ModelConfig,
        pywr_model: Model,
        parent: "InspectorDialog",
    ):
        """
        Initialises the widget.
        :param model_config: The ModelConfig instance.
        :param pywr_model: The pywr Model instance.
        :param parent: The parent window.
        """
        super().__init__(parent)
        self.parent = parent
        self.model_config = model_config
        self.pywr_model = pywr_model
        # noinspection PyUnresolvedReferences
        self.has_scenarios = len(pywr_model.scenarios.scenarios)
        # noinspection PyUnresolvedReferences
        self.scenario_combinations = list(pywr_model.scenarios.combination_names)

        self.setStyleSheet(self.stylesheet)

        # header
        self.setHeaderLabels(("Attribute", "Value"))
        self.setColumnCount(2)
        self.header().resizeSection(0, 300)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setStyleSheet(self.header_stylesheet)
        self.add_nodes()
        self.add_parameters()
        self.add_recorders()
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def add_nodes(self) -> None:
        """
        Adds the nodes and their attributes to the tree.
        :return: None
        """
        node_root = QTreeWidgetItem(self)
        node_root.setText(0, f"Nodes ({len(self.pywr_model.nodes)})")
        node_root.setExpanded(True)

        allowed_types = (int, float, str, list)
        for node in self.pywr_model.nodes:
            node_config = self.model_config.nodes.config(node.name, as_dict=False)
            node_item = QTreeWidgetItem(node_root)
            node_item.setText(0, f"{node.name} - {node_config.humanised_type}")

            # set icon
            icon, _ = get_pixmap_from_type(
                QSize(26, 25),
                get_node_icon(model_node_obj=node_config, ignore_custom_type=True),
            )
            node_item.setIcon(0, icon)

            # set attributes
            all_attributes = inspect.getmembers(
                node,
                lambda a: not inspect.isroutine(a),
            )

            for attr in all_attributes:
                attr_raw_name = attr[0]
                attr_value = attr[1]
                attr_name = node_config.humanise_attribute_name(attr_raw_name)

                # exclude private attributes
                if (
                    attr_raw_name.startswith("__")
                    or attr_raw_name.endswith("__")
                    or attr_raw_name
                    in [
                        "component_attrs",
                        "inputs",
                        "outputs",
                        "color",
                        "visible",
                    ]
                ):
                    continue

                # exclude invalid types
                if (
                    not isinstance(attr_value, allowed_types)
                    or attr_value is None
                    or (isinstance(attr_value, (list, dict)) and len(attr_value) == 0)
                ):
                    continue

                # only allow list of strings or numbers
                if isinstance(attr_value, list) and not all(
                    [isinstance(a, allowed_types) for a in attr_value]
                ):
                    continue

                # any other attribute (float, string or boolean)
                attr_item = QTreeWidgetItem(node_item)
                attr_item.setText(0, attr_name)
                attr_item.setText(1, str(attr_value))
                attr_item.setToolTip(1, type(attr_value).__name__)

            # render scenario-dependant attributes
            for attr_raw_name, result_data in self.get_node_value_dict(
                self.pywr_model, all_attributes
            ).items():
                attr_name = node_config.humanise_attribute_name(attr_raw_name)

                attr_item = QTreeWidgetItem(node_item)
                attr_item.setText(0, attr_name)
                if result_data["has_scenarios"]:
                    attr_item.setToolTip(0, result_data["type"])
                    attr_item.setText(1, result_data["combinations"])
                    for sc_i, sc_value in enumerate(result_data["data"]):
                        sc_item = QTreeWidgetItem(attr_item)
                        sc_item.setText(0, sc_value["name"])
                        sc_item.setText(1, sc_value["value"])
                        sc_item.setToolTip(1, sc_value["type"])
                else:
                    attr_item.setText(1, result_data["data"]["value"])
                    attr_item.setToolTip(1, result_data["data"]["type"])

    def add_parameters(self) -> None:
        """
        Adds the parameters and their attributes to the tree.
        :return: None
        """
        root = QTreeWidgetItem(self)
        root.setExpanded(True)

        total_parameters = 0
        for parameter in self.pywr_model.parameters:
            parameter: Parameter
            # render model parameters only
            if parameter.name is None:
                continue
            total_parameters += 1
            parameter_config = self.model_config.parameters.get_config_from_name(
                parameter.name, as_dict=False
            )
            parameter_item = QTreeWidgetItem(root)
            parameter_item.setText(
                0, f"{parameter.name} - {parameter_config.humanised_type}"
            )
            parameter_item.setIcon(0, QIcon(ParameterIcon(parameter_config.key)))

            all_attributes = inspect.getmembers(
                parameter,
                lambda a: not inspect.isroutine(a),
            )

            for attr in all_attributes:
                self.render_component_attribute(
                    attr=attr,
                    attr_name=parameter_config.humanise_attribute_name(attr[0]),
                    root_item=parameter_item,
                )
            # add values
            self.render_parameter_values(parameter=parameter, root_item=parameter_item)

        root.setText(0, f"Parameters ({total_parameters})")

    def add_recorders(self) -> None:
        """
        Adds the recorders and their attributes to the tree.
        :return: None
        """
        root = QTreeWidgetItem(self)
        root.setExpanded(True)

        total_recorders = 0
        for recorder in self.pywr_model.recorders:
            recorder: Recorder
            # render model parameters only
            if recorder.name is None:
                continue

            total_recorders += 1
            recorder_config = self.model_config.recorders.get_config_from_name(
                recorder.name, as_dict=False
            )
            recorder_item = QTreeWidgetItem(root)
            recorder_item.setText(
                0, f"{recorder.name} - {recorder_config.humanised_type}"
            )
            recorder_item.setIcon(0, QIcon(RecorderIcon(recorder_config.key)))

            all_attributes = inspect.getmembers(
                recorder,
                lambda a: not inspect.isroutine(a),
            )

            for attr in all_attributes:
                self.render_component_attribute(
                    attr=attr,
                    attr_name=recorder_config.humanise_attribute_name(attr[0]),
                    root_item=recorder_item,
                )
            # add values
            self.render_recorder_values(recorder=recorder, root_item=recorder_item)

        root.setText(0, f"Recorders ({total_recorders})")

    def render_component_attribute(
        self, attr: tuple[str, Any], attr_name: str, root_item: QTreeWidgetItem
    ) -> None:
        """
        Renders the nested tree for a parameter or recorder attribute.
        :param attr: The tuple with the attribute to render. The first item contains
        the attribute raw name, the second the attribute value.
        :param attr_name: The formatted attribute name to display.
        :param root_item: The QTreeWidgetItem instance to add the attribute to.
        :return: None
        """
        allowed_types = (int, float, str, list)
        attr_raw_name = attr[0]
        attr_value = attr[1]

        # exclude private attributes
        if attr_raw_name.startswith("__") or attr_raw_name.endswith("__"):
            return

        # render nested parameter(s) (for example control_curves)
        if isinstance(attr_value, Parameter) or (
            isinstance(attr_value, list)
            and all([isinstance(a, Parameter) for a in attr_value])
        ):
            if not isinstance(attr_value, list):
                attr_value = [attr_value]

            attr_item = QTreeWidgetItem(root_item)
            attr_item.setText(0, attr_name)
            # print all nested anonymous parameters
            for nested_param in attr_value:
                nested_param: Parameter
                key = ParameterConfig.string_to_key(nested_param.__class__.__name__)
                all_nested_attributes = inspect.getmembers(
                    nested_param,
                    lambda a: not inspect.isroutine(a),
                )

                # print all attribute for the nested parameter
                nested_param_root_item = QTreeWidgetItem(attr_item)
                nested_param_root_item.setText(0, nested_param.__class__.__name__)
                nested_param_root_item.setIcon(0, QIcon(ParameterIcon(key)))
                for nested_attr in all_nested_attributes:
                    self.render_component_attribute(
                        attr=nested_attr,
                        attr_name=humanise_label(nested_attr[0]),
                        root_item=nested_param_root_item,
                    )
                # add values
                self.render_parameter_values(
                    parameter=nested_param, root_item=nested_param_root_item
                )
            return

        # only allow list of strings or numbers
        if isinstance(attr_value, list) and not all(
            [isinstance(a, allowed_types) for a in attr_value]
        ):
            return

        # exclude invalid types
        if (
            not isinstance(attr_value, allowed_types)
            or attr_value is None
            or (isinstance(attr_value, (list, dict)) and len(attr_value) == 0)
        ):
            return

        # any other attribute (float, string or boolean)
        attr_item = QTreeWidgetItem(root_item)
        attr_item.setText(0, attr_name)
        attr_item.setText(1, str(attr_value))
        attr_item.setToolTip(1, type(attr_value).__name__)

    def render_parameter_values(
        self, parameter: Parameter, root_item: QTreeWidgetItem
    ) -> None:
        """
        Renders the values of a parameter.
        :param parameter: The pywr Parameter instance.
        :param root_item: The instance of the tree where to add the new item.
        :return: None
        """
        param_values = np.asarray(parameter.get_all_values())

        param_value_item = QTreeWidgetItem(root_item)
        param_value_item.setText(0, "Value")
        if self.has_scenarios:
            param_value_item.setToolTip(0, type(param_values).__name__)
            param_value_item.setText(
                1, f"{len(self.scenario_combinations)} combinations"
            )
            for sc_i, sc_name in enumerate(self.scenario_combinations):
                sc_item = QTreeWidgetItem(param_value_item)
                sc_item.setText(0, sc_name)
                sc_item.setText(1, str(param_values[sc_i]))
                sc_item.setToolTip(1, type(param_values[sc_i]).__name__)
        else:
            param_value_item.setText(1, str(param_values[0]))
            param_value_item.setToolTip(1, type(param_values[0]).__name__)

    def render_recorder_values(
        self, recorder: Recorder, root_item: QTreeWidgetItem
    ) -> None:
        """
        Renders the values of a  recorder.
        :param recorder: The pywr Recorder instance.
        :param root_item: The instance of the tree where to add the new item.
        :return: None
        """
        methods_and_attrs = {
            "aggregated_value": "method",
            "values": "method",
            "data": "attribute",
        }
        for name, class_type in methods_and_attrs.items():
            # some recorder do not implement all methods
            # noinspection PyBroadException
            try:
                values = getattr(recorder, name)
                if class_type == "method":
                    values = values()

                if name == "aggregated_value":
                    values = float(values)
                else:
                    values = np.asarray(values)

                # data attribute for numpy recorder is initialised with zeros
                # get the values for the current timestep only
                if name == "data":
                    # noinspection PyUnresolvedReferences
                    values = values[self.pywr_model.timestepper.current.index]

                value_item = QTreeWidgetItem(root_item)
                value_item.setText(0, humanise_label(name))
                if name in ["values", "data"] and self.has_scenarios:
                    value_item.setToolTip(0, type(values).__name__)
                    value_item.setText(
                        1, f"{len(self.scenario_combinations)} combinations"
                    )
                    for sc_i, sc_name in enumerate(self.scenario_combinations):
                        sc_item = QTreeWidgetItem(value_item)
                        sc_item.setText(0, sc_name)
                        sc_item.setText(1, str(values[sc_i]))
                        sc_item.setToolTip(1, type(values[sc_i]).__name__)
                else:
                    value_item.setText(1, str(values))
                    value_item.setToolTip(1, type(values).__name__)
            except Exception:
                continue

    @property
    def stylesheet(self) -> str:
        """
        Returns the stylesheet.
        :return: The stylesheet as string.
        """
        style = {
            "InspectorTree": {
                "border": f"1px solid {Color('gray', 300).hex}",
                "border-radius": "6px",
                "outline": 0,
                "color": Color("gray", 700).hex,
            },
            "InspectorTree::item": {"color": Color("gray", 900).hex},
            "InspectorTree::branch:has-siblings:!adjoins-item": {
                "border-image": "url(:components-tree/branch-vline) 0"
            },
            "InspectorTree::branch:has-siblings:adjoins-item ": {
                "border-image: url(:components-tree/branch-more) 0"
            },
            "InspectorTree::branch:!has-children:!has-siblings:adjoins-item": {
                "border-image: url(:components-tree/branch-end) 0"
            },
        }

        return stylesheet_dict_to_str(style)

    @property
    def header_stylesheet(self) -> str:
        """
        Returns the stylesheet for the header.
        :return: The stylesheet as string.
        """
        return stylesheet_dict_to_str(
            {
                "QWidget::section": {
                    "background": Color("gray", 200).hex,
                    "height": "20px",
                    "padding-top": "4px",
                    "padding-left": "6px",
                    "font-size": "110%",
                    "border": f"1px solid {Color('gray', 300).hex}",
                },
            }
        )

    @staticmethod
    def get_node_value_dict(
        pywr_model: Model, all_attributes: list[Tuple[str, Any]]
    ) -> dict[str, Any]:
        """
        Gets the node's results as dictionary.
        :param pywr_model: The pywr model instance.
        :param all_attributes: The pywr node attributes.
        :return: The results as dictionary.
        """
        # noinspection PyUnresolvedReferences
        has_scenarios = len(pywr_model.scenarios.scenarios)
        # noinspection PyUnresolvedReferences
        scenario_combinations = list(pywr_model.scenarios.combination_names)

        value_dict = {}
        for attr in all_attributes:
            attr_name = attr[0]
            attr_value = attr[1]

            # render scenario-dependant attributes
            if attr_name in [
                "flow",
                "prev_flow",
                "current_pc",
                "volume",
            ]:
                value_dict[attr_name] = {}
                if has_scenarios:
                    value_dict[attr_name]["has_scenarios"] = True
                    value_dict[attr_name]["type"] = type(attr_value).__name__
                    value_dict[attr_name][
                        "combinations"
                    ] = f"{len(scenario_combinations)} combinations"
                    value_dict[attr_name]["data"] = []
                    for sc_i, sc_name in enumerate(scenario_combinations):
                        value_dict[attr_name]["data"].append(
                            {
                                "name": sc_name,
                                "value": str(attr_value[sc_i]),
                                "type": type(attr_value[sc_i]).__name__,
                            }
                        )
                else:
                    value_dict[attr_name]["has_scenarios"] = False
                    value_dict[attr_name]["data"] = {
                        "value": str(attr_value[0]),
                        "type": type(attr_value[0]).__name__,
                    }

        return value_dict
