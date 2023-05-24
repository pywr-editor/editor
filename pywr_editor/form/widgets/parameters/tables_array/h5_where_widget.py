from PySide6.QtCore import Signal, SignalInstance, Slot

from pywr_editor.form import (
    AbstractStringComboBoxWidget,
    FormField,
    H5FileWidget,
    Validation,
)
from pywr_editor.utils import get_signal_sender

"""
 Widget used to select the where attribute of
 a H5 file. The attributes are fetched from
 the H5FileWidget.
"""


class H5WhereWidget(AbstractStringComboBoxWidget):
    default_labels_map: dict[str, str] = {"None": "None"}
    where_attr_changed: SignalInstance = Signal(list)

    def __init__(self, name: str, value: str | None, parent: FormField):
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=self.default_labels_map,
            default_value="None",
        )
        self.keys: dict[str, list[str]] = {}
        self.node_keys: list[str] = []

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        # populate widget for the first time using the keys in the h5 file widget
        self.populate_widget(self.value)

        # connect Slot to update the widget keys when the file changes
        # noinspection PyTypeChecker
        file_widget: H5FileWidget = self.form.find_field("url").widget
        # noinspection PyTypeChecker
        file_widget.file_changed.connect(self.on_update_file)

        # updates the where keys if the where attribute changes
        # noinspection PyUnresolvedReferences
        self.combo_box.currentTextChanged.connect(self.on_attribute_change)

    def populate_widget(self, selected_attribute: str) -> None:
        """
        Resets and populates the combo box and the widget attributes with
        new values using the keys stored in the h5 file.
        :param selected_attribute: The selected attribute name.
        :return: None
        """
        # reset field
        self.reset()

        # get keys in h5 file
        file_field = self.form.find_field("url")
        # noinspection PyTypeChecker
        file_widget: H5FileWidget = file_field.widget

        if file_field.value() is not None and file_widget.keys:
            self.combo_box.setEnabled(True)
        else:
            self.logger.debug("File not available")

        # get attributes
        self.keys = file_widget.keys
        attributes = list(self.keys.keys())
        # convert to dictionary and prepend None
        attributes_dict = {name: name for name in sorted(attributes)}
        attributes_dict = {**self.default_labels_map, **attributes_dict}
        self.labels_map = attributes_dict

        # validate values
        self.label, self.warning_message = self.sanitise_value(selected_attribute)
        self.logger.debug(f"Setting selection to {self.label}")

        # sort values alphabetically
        combo_box_items = list(attributes_dict.values())
        self.logger.debug(f"Adding items {combo_box_items}")
        self.combo_box.addItems(combo_box_items)
        self.combo_box.setCurrentText(self.label)

        if self.combo_box.isEnabled():
            self.logger.debug("Setting warning message")
            self.field.set_warning(self.warning_message)

            # store the where keys of the attribute
            self.on_attribute_change()

    def get_value(self) -> str | None:
        """
        Returns the value from the label.
        :return: The selected attribute or None if the field is disabled or no
        attribute is selected.
        """
        value = super().get_value()
        if value == "None":
            return None
        return value

    def validate(self, name: str, label: str, value: str | None) -> Validation:
        """
        Checks that the attribute is selected.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label.
        :return: The Validation instance.
        """
        if self.get_value() is None and self.combo_box.isEnabled():
            self.logger.debug("Validation failed")
            return Validation("You must select a name from the list")

        self.logger.debug("Validation passed")
        return Validation()

    def get_default_value(self) -> str:
        """
        Returns the default value.
        :return: The default value "/".
        """
        return "/"

    def reset(self) -> None:
        """
        Resets the widget by setting the default values.
        """
        self.logger.debug("Resetting widget")
        self.combo_box.setEnabled(False)

        # prevent change Signal from being called here
        self.combo_box.blockSignals(True)
        self.combo_box.clear()
        self.combo_box.blockSignals(False)

        self.labels_map = self.default_labels_map
        self.keys = {}
        self.node_keys = []

        super().reset()

    @Slot()
    def on_update_file(self) -> None:
        """
        Updates the keys when the file changes.
        :return: None
        """
        self.logger.debug(
            "Running on_update_file Slot because file changed from "
            + get_signal_sender(self)
        )
        self.populate_widget(self.combo_box.currentText())

    @Slot()
    def on_attribute_change(self) -> None:
        """
        Updates the where keys when the attribute changes.
        :return: None
        """
        self.logger.debug(
            "Running on_attribute_change Slot because file changed from "
            + get_signal_sender(self)
        )
        attribute_name = self.combo_box.currentText()

        if attribute_name and attribute_name != "None":
            self.node_keys = self.keys[attribute_name]
            self.logger.debug(
                f"Setting node keys to: {self.node_keys} for where attribute "
                + f"{attribute_name}"
            )
        else:
            self.node_keys = []
            self.logger.debug(f"Emptied node keys. Attribute is '{attribute_name}'")

        # emit signal
        # noinspection PyUnresolvedReferences
        self.where_attr_changed.emit(self.node_keys)
