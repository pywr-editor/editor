from typing import Union
from PySide6.QtWidgets import QTreeWidgetItem
from pywr_editor.model import ModelConfig
from .abstract_tree_widget_component import AbstractTreeWidgetComponent


class TreeWidgetRecorderName(QTreeWidgetItem):
    def __init__(self, name: str, parent: QTreeWidgetItem | None = None):
        super().__init__(parent)
        self.name = name


class TreeWidgetRecorder(AbstractTreeWidgetComponent):
    def __init__(
        self,
        recorder_config: dict,
        model_config: ModelConfig,
        parent: Union[
            "TreeWidgetRecorder", TreeWidgetRecorderName, None
        ] = None,
    ):
        """
        Initialises the item containing the recorder configuration.
        :param recorder_config: The recorder configuration dictionary.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(
            comp_value=recorder_config,
            model_config=model_config,
            comp_type="recorder",
            parent_type=dict,
            parent=parent,
        )
