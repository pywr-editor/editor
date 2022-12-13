import pywr_editor
from PySide6.QtCore import QSize, Slot
from PySide6.QtWidgets import QHBoxLayout
from pywr_editor.model import NodeConfig
from pywr_editor.utils import Logging
from pywr_editor.widgets import ComboBox
from pywr_editor.node_shapes import (
    get_node_icon_classes,
    get_node_icon,
    get_pixmap_from_type,
)
from pywr_editor.form import FormCustomWidget, FormField


class NodeStylePickerWidget(FormCustomWidget):
    default_str_style = "None"

    def __init__(
        self,
        name: str,
        value: NodeConfig,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The NodeConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(name, value, parent)

        selected_style = value.custom_style

        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value '{selected_style}'")
        self.combo_box = ComboBox()
        icon_size = QSize(25, 24)

        # Add the icon for the current node type
        icon, _ = get_pixmap_from_type(
            icon_size,
            get_node_icon(model_node_obj=value, ignore_custom_type=True),
        )
        self.combo_box.addItem(
            icon,
            f"{value.humanise_node_type} (default)",
            self.default_str_style,
        )

        # Add the other icons
        name_key_map = {}
        for index, icon_class_name in enumerate(
            get_node_icon_classes(include_pywr_nodes=False)
        ):
            icon_class_type = getattr(pywr_editor.node_shapes, icon_class_name)
            icon, label = get_pixmap_from_type(icon_size, icon_class_type)
            self.combo_box.addItem(icon, label, icon_class_name)
            name_key_map[icon_class_name.lower()] = icon_class_name

        # select the icon
        if selected_style and selected_style in name_key_map:
            self.logger.debug(f"Setting icon to {selected_style}")
            selected_index = self.combo_box.findData(
                name_key_map[selected_style]
            )
        else:
            self.logger.debug("Setting default icon")
            selected_index = self.combo_box.findData(self.default_str_style)
        self.combo_box.setCurrentIndex(selected_index)

        # connect slot to change the icon in the dialog title
        # noinspection PyUnresolvedReferences
        self.combo_box.currentIndexChanged.connect(self.on_value_changed)

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

    @Slot()
    def on_value_changed(self) -> None:
        """
        Updates the dialog title when the icon changes.
        :return: None
        """
        from pywr_editor.dialogs.node.node_dialog_form import NodeDialogForm

        icon_class_name = self.combo_box.currentData()
        # get icon for default type
        if icon_class_name == self.default_str_style:
            icon_class_type = get_node_icon(
                model_node_obj=self.value, ignore_custom_type=True
            )
        # custom icon
        else:
            icon_class_type = getattr(pywr_editor.node_shapes, icon_class_name)

        if not isinstance(self.form, NodeDialogForm):
            raise ValueError(
                "The widget can only be registered in NodeDialogForm"
            )

        self.form: NodeDialogForm
        self.form.dialog.title.update_icon(icon_class_type)

    def get_value(self) -> str | None:
        """
        Returns the selected colour
        :return: The colour or None if the default colour is selected.
        """
        value = self.combo_box.currentData()
        if value == self.default_str_style:
            return None
        return value.lower()
