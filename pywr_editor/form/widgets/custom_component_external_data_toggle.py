from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGroupBox, QVBoxLayout

from pywr_editor.form import FormField, FormWidget
from pywr_editor.utils import Logging
from pywr_editor.widgets import ToggleSwitchWidget

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm


class ComponentExternalDataToggle(FormWidget):
    def __init__(
        self,
        name: str,
        value: dict[str, Any] | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The parameter dictionary.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget {name} with value {value}")

        super().__init__(name=name, value=value, parent=parent)

        # enable toggle is the dictionary contains the "url" or "table" keys to
        # import data
        self.enabled = False
        if isinstance(value, dict) and ("url" in value or "table" in value):
            self.enabled = True

        self.toggle = ToggleSwitchWidget()
        self.toggle.setChecked(self.enabled)
        # noinspection PyUnresolvedReferences
        self.toggle.stateChanged.connect(self.on_value_change)

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle)

        # populate fields
        self.form.register_after_render_action(self.after_form_render)

    def after_form_render(self) -> None:
        """
        Actions to perform after the entire form is rendered.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.on_value_change()

    @Slot()
    def on_value_change(self) -> None:
        """
        SHows/hides the sections to load external data for a custom parameter.
        :return: None
        """
        self.form: "ModelComponentForm"
        self.enabled = self.toggle.isChecked()
        for section in self.form.findChildren(QGroupBox):
            if section.objectName() in [
                "External data",
                self.form.table_config_group_name,
            ]:
                self.logger.debug(f"Change visibility of section {section}")
                section.setVisible(self.enabled)

    def get_value(self) -> None:
        """
        Returns None to always ignore the field value.
        :return: None.
        """
        return None

    def get_default_value(self) -> None:
        """
        The field default value.
        :return: None.
        """
        return None

    def reset(self) -> None:
        """
        Resets the widget. This unchecked the toggle.
        :return: None
        """
        self.toggle.setChecked(False)
