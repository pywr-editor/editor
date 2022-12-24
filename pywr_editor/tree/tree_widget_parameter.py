from typing import TYPE_CHECKING, Union

from PySide6.QtWidgets import QTreeWidgetItem

from pywr_editor.model import ModelConfig

from .abstract_tree_widget_component import AbstractTreeWidgetComponent

if TYPE_CHECKING:
    from .tree_widget_node import TreeWidgetNodeAttribute


class TreeWidgetParameterName(QTreeWidgetItem):
    def __init__(self, name: str, parent: QTreeWidgetItem | None = None):
        super().__init__(parent)
        self.name = name


class TreeWidgetParameter(AbstractTreeWidgetComponent):
    def __init__(
        self,
        parameter_config: dict,
        model_config: ModelConfig,
        parent: Union[
            "TreeWidgetParameter",
            TreeWidgetParameterName,
            "TreeWidgetNodeAttribute",
            None,
        ] = None,
    ):
        """
        Initialises the item containing the parameter configuration.
        :param parameter_config: The parameter configuration dictionary.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(
            comp_value=parameter_config,
            model_config=model_config,
            comp_type="parameter",
            parent_type=dict,
            parent=parent,
        )
