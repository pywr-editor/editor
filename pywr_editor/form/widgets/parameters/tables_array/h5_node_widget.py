from PySide6.QtCore import Slot

from pywr_editor.form import (
    AbstractStringComboBoxWidget,
    FormField,
    H5WhereWidget,
    Validation,
)
from pywr_editor.utils import get_signal_sender

"""
 Widget used to select the node from the
 where attribute of a H5 file. The node
 are fetched from the H5WhereWidget.
"""


class H5NodeWidget(AbstractStringComboBoxWidget):
    default_labels_map: dict[str, str] = {"None": "None"}

    def __init__(self, name: str, value: str | None, parent: FormField):
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=self.default_labels_map,
            default_value="None",
        )

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        # populate widget for the first time using the keys in the h5 file widget
        self.populate_widget(self.value)

        # connect Slot to update the nodes when the where attribute changes
        # noinspection PyTypeChecker
        where_widget: H5WhereWidget = self.form.find_field("where").widget
        # noinspection PyUnresolvedReferences
        where_widget.where_attr_changed.connect(self.on_update_where)

    def populate_widget(self, selected_node: str) -> None:
        """
        Resets and populates the combo box and the widget attributes with
        new values using the data stored in the H5WhereWidget.
        :param selected_node: The selected node name.
        :return: None
        """
        # reset field
        self.reset()

        # get keys in h5 file
        where_field = self.form.find_field("where")
        # noinspection PyTypeChecker
        where_widget: H5WhereWidget = where_field.widget

        if where_field.value() is not None and where_widget.node_keys:
            self.combo_box.setEnabled(True)
        else:
            self.logger.debug("Nodes not available")

        # get attributes
        nodes = where_widget.node_keys
        # convert to dictionary and prepend None
        attributes_dict = {name: name for name in sorted(nodes)}
        attributes_dict = {**self.default_labels_map, **attributes_dict}
        self.labels_map = attributes_dict

        # validate values
        self.label, self.warning_message = self.sanitise_value(selected_node)
        self.logger.debug(f"Setting selection to {self.label}")

        # sort values alphabetically
        combo_box_items = list(attributes_dict.values())
        self.logger.debug(f"Adding items {combo_box_items}")

        self.combo_box.addItems(combo_box_items)
        if self.combo_box.isEnabled():
            self.combo_box.setCurrentText(self.label)
            self.field.set_warning(self.warning_message)

    def get_value(self) -> str | None:
        """
        Returns the value.
        :return: The selected node or None if the field is disabled or no node is
        selected.
        """
        value = super().get_value()
        if value == "None":
            return None
        return value

    def validate(self, name: str, label: str, value: str | None) -> Validation:
        """
        Checks that the node is selected.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label.
        :return: The Validation instance.
        """
        if self.get_value() is None and self.combo_box.isEnabled():
            self.logger.debug("Validation failed")
            return Validation("You must select a node from the list")

        self.logger.debug("Validation passed")
        return Validation()

    def reset(self) -> None:
        """
        Resets the widget by setting the default values.
        """
        self.logger.debug("Resetting widget")
        self.combo_box.setEnabled(False)
        self.combo_box.setCurrentText("None")
        self.combo_box.clear()

        self.labels_map = self.default_labels_map

        super().reset()

    @Slot()
    def on_update_where(self) -> None:
        """
        Updates the nodes when the where attribute changes.
        :return: None
        """
        self.logger.debug(
            "Running on_update_where Slot because file changed from "
            + get_signal_sender(self)
        )
        self.populate_widget(self.combo_box.currentText())
