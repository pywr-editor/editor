from typing import Literal

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField, FormSection
from pywr_editor.model import ParameterConfig, RecorderConfig
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import ComboBox

"""
 This widget allows the user to choose how to define the component value
 in the component picker form. The component can be provided as string,
 to use an already defined component in the model configuration, or can
 be defined from scratch by defining its value or fetching the data
 from a table or an external file.
"""


class ModelComponentSourceSelectorWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: ParameterConfig | RecorderConfig,
        parent: FormField,
        component_type: Literal["parameter", "recorder"],
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The parameter instance.
        :param parent: The parent widget.
        :param component_type: The component type (parameter or recorder).
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        self.labels = {
            "model_component": f"Use an exiting model {component_type}",
            "new_component": f"Define a new {component_type}",
        }

        super().__init__(name, value, parent)

        self.combo_box = ComboBox()
        self.combo_box.addItems(list(self.labels.values()))
        self.init = True

        # the component configuration depends on which fields are provided in
        # the configuration
        if value.name is not None:
            self.logger.debug(f"Source is a model {component_type}")
            self.combo_box.setCurrentText(self.labels["model_component"])
        else:
            self.logger.debug(f"Source is an anonymous {component_type}")
            self.combo_box.setCurrentText(self.labels["new_component"])

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

        # run action after all fields are available
        self.form.after_render_actions.append(self.after_field_render)

    def after_field_render(self) -> None:
        """
        Action called after the entire section has been rendered.
        :return: None
        """
        # init form
        self.on_type_change(self.get_value())

        # noinspection PyUnresolvedReferences
        self.combo_box.currentTextChanged.connect(self.on_type_change)

        # delete section if source is "model_component"
        # noinspection PyTypeChecker
        component_type_widget = self.form.find_field("type").widget
        # noinspection PyUnresolvedReferences
        component_type_widget.section_added.connect(self.on_section_added)

        self.init = False

    @Slot(str)
    def on_type_change(self, field_value: str) -> None:
        """
        Slots called at init or when the field changes its value.
        :param field_value: The field value or index.
        :return: None
        """
        self.logger.debug(
            f"Running on_type_change Slot with value '{field_value}' "
            + f"from {get_signal_sender(self)}"
        )

        # Trigger field reset after field is initialised -  the component name and
        # type fields are always present in the form but one is hidden depending
        # on the value of this widget
        if self.init is False:
            for name in ["type", "comp_name"]:
                self.logger.debug(f"Resetting FormField '{name}'")
                form_field = self.form.find_field(name)
                # noinspection PyUnresolvedReferences
                form_field.widget.reset()
        else:
            self.logger.debug("Skipping fields reset because widget is initialising")

        # Toggle component visibility
        if field_value == self.labels["model_component"]:
            hide = "type"
            show = "comp_name"
        elif field_value == self.labels["new_component"]:
            hide = "comp_name"
            show = "type"
        else:
            raise ValueError("Wrong source type provided")

        # show (and enable) or hide (and disable) the correct fields
        self.logger.debug(f"Hiding field: {hide}")
        self.form.change_field_visibility(
            hide,
            show=False,
            clear_message=self.init is False,
            disable_on_hide=True,
            throw_if_missing=True,
        )
        self.logger.debug(f"Showing field: {show}")
        self.form.change_field_visibility(
            show,
            show=True,
            clear_message=self.init is False,
            disable_on_hide=True,
            throw_if_missing=True,
        )

    @Slot()
    def on_section_added(self) -> None:
        """
        Removes a section if the component source is "model_component".
        :return: None
        """
        if self.get_value() != self.labels["model_component"]:
            return

        # noinspection PyTypeChecker
        current_section: FormSection = self.form.findChild(FormSection)
        if current_section is not None:
            self.logger.debug(f"Deleted {current_section.name}")
            self.form.delete_section(current_section)

    def get_value(self) -> str:
        """
        Returns the form field value.
        :return: The form field value.
        """
        return self.combo_box.currentText()
