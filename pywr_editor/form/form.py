from typing import Any, Callable, Literal, Type, Union

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.utils import Logging, get_signal_sender, humanise_label
from pywr_editor.widgets import (
    CheckableComboBox,
    ComboBox,
    SpinBox,
    ToggleSwitchWidget,
)

from .field_config import FieldConfig
from .form_field import FormField
from .form_section import FormSection
from .form_validation import FormValidation


class Form(QScrollArea):
    def __init__(
        self,
        available_fields: dict[str, list[FieldConfig]],
        defaults: None | dict = None,
        save_button: QPushButton = None,
        parent: QWidget = None,
        direction: Literal["horizontal", "vertical"] = "horizontal",
    ):
        """
        Initialises the form widget from a dictionary. To load the form, call
        self.load_fields(). Once the form is loaded. self.loaded is True.
        :param available_fields: The dictionary containing the section name as key and
        a list of FieldConfig dictionaries as values.
        :param defaults: Optional method to supply the default value to use for a field
        instead of "default_value".
        :param save_button: The button used to save the form. The button will be
        enabled if there is a change in any field and will be disabled after the
        form is successfully saved.
        :param parent: The parent widget. Default to None.
        :param direction: The form direction. Vertical to align the labels vertically
        with respect to the fields, or horizontal.
        """
        super().__init__(parent)
        cls_name = self.__class__.__name__
        self.setObjectName(cls_name)

        self.logger = Logging().logger(cls_name)
        self.parent = parent
        self.available_fields = available_fields
        self.save_button = save_button
        self.fields: dict[str, FormField] = {}
        self.sections: dict[str, QGroupBox | FormSection] = {}
        self.loaded = False

        # actions defined in FormCustomWidget.after_field_render() when a widget needs
        # access to other fields
        self.after_render_actions: list[callable] = []
        # actions defined by a widget in FormSection when widget needs access to other
        # fields
        self.after_render_section_actions: list[callable] = []
        self.defaults = defaults
        self.direction = direction
        self.field_config: dict[str, dict] = {}
        if self.defaults is None:
            self.defaults = {}

        # hide the scroll area background and the context menu
        self.setStyleSheet("Form{ background: transparent; border: 0; }")
        self.horizontalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
        self.verticalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)

        # add one widget in the scroll area to enable scrolling
        form_container = FormContainer(self)
        self.setWidget(form_container)
        self.setWidgetResizable(True)

        self.area_layout = QVBoxLayout(form_container)
        self.area_layout.setAlignment(Qt.AlignTop)
        self.area_layout.setContentsMargins(0, 0, 0, 0)

    def load_fields(self) -> None:
        """
        Adds and renders the widget fields.
        :return: Non
        """
        if self.loaded is True:
            return

        self.loaded = True

        # field configuration dictionary
        for section_data in self.available_fields.values():
            for field_data in section_data:
                self.field_config[field_data["name"]] = field_data

        # add the fields and their values in each section
        self.add_section(self.available_fields)

        # after render method for custom widgets. If a widget needs a value from
        # another form field, this must be fetched after all fields are rendered.
        for custom_widget_action in self.after_render_actions:
            custom_widget_action()

        # disable the save button if provided. This is re-enabled after the user
        # applies a change to the form
        if self.save_button is not None:
            self.save_button.setEnabled(False)

    def get_default(self, key: str) -> str | bool | None:
        """
        Gets the default value for a parameter configuration value.
        :param key: The key
        :return: The default value or None if no default value is available.
        """
        if key in self.defaults.keys():
            return self.defaults[key]
        return None

    @staticmethod
    def get_dict_value(
        key: str, dict_values: dict
    ) -> str | float | bool | None:
        """
        Gets a value from a dictionary containing the form field values.
        :param key: The key to extract the value of.
        :param dict_values: The dictionary containing the field values.
        :return: The value or empty if the key is not set.
        """
        if dict_values is None or key not in dict_values.keys():
            return None

        return dict_values[key]

    def add_section(
        self,
        section_data: dict[str, list[FieldConfig]],
        section_class: FormSection | None = None,
    ) -> None:
        """
        Adds a new section to the form.
        :param section_data: The dictionary describing the section parts.
        :param section_class: For custom sections, this is the class used to initialise
         the section.
        :return: None
        """
        for name, data in section_data.items():
            self.logger.debug(f"Adding QGroupBox '{name}'")
            self._render_partial_section(name, data, section_class)

        # for custom sections, when all QGroupBox are added to section, add it to layout
        # and record it in self.sections
        if section_class is not None:
            self.area_layout.addWidget(section_class)
            self.sections[section_class.name] = section_class

        # after render method for custom sections, when a widget in the section needs a
        # value from another form field
        for custom_section_action in self.after_render_section_actions:
            custom_section_action()

        # attach event to fields to enable/disable the save button if provided
        children_container = self
        if section_class is not None:
            children_container = section_class

        if self.save_button is not None:
            for form_field in children_container.findChildren(FormField):
                for field in (
                    form_field.findChildren(QLineEdit)
                    + form_field.findChildren(SpinBox)
                    + form_field.findChildren(QSpinBox)
                    + form_field.findChildren(QDoubleSpinBox)
                ):
                    field.textChanged.connect(self.on_field_changed)

                for field in form_field.findChildren(ComboBox):
                    field.activated.connect(self.on_field_changed)

                for field in form_field.findChildren(
                    QCheckBox
                ) + form_field.findChildren(ToggleSwitchWidget):
                    field.stateChanged.connect(self.on_field_changed)

                for field in form_field.findChildren(CheckableComboBox):
                    field.model().dataChanged.connect(self.on_field_changed)

    def delete_section(self, section: Union["FormSection", None]) -> None:
        """
        Removes a section from the form.
        :param section: The section instance.
        :return: None
        """
        if section is None:
            return

        # hide section. When it is removed from layout it may be visible as standalone
        # for a few ms.
        section.setHidden(True)

        # delete reference from form
        self.area_layout.removeWidget(section)
        del self.sections[section.name]
        self.after_render_section_actions = []

        # delete widget
        # noinspection PyTypeChecker
        section.setParent(None)
        section.deleteLater()

    def add_section_from_class(
        self, section_class: Type[FormSection], section_data: dict
    ) -> None:
        """
        Adds a form section from a class inheriting from FormSection.
        :param section_class: The instance of the class.
        :param section_data: A dictionary with additional data to pass to the class.
        :return: None
        """
        section_class_instance = section_class(
            form=self, section_data=section_data
        )
        self.add_section(section_class_instance.data, section_class_instance)

    def _render_partial_section(
        self,
        section_name: str,
        section_data: list[FieldConfig],
        section_class=None,
    ) -> None:
        """
        Adds a new section to the form. This adds a QGroupBox to the form or to
        section_class for custom sections.
        :param section_name: The section name.
        :param section_data: The dictionary describing the section.
        :param section_class: For custom sections, this is the class used to initialise
         the section.
        :return: None
        """
        container = QGroupBox()
        container.setTitle(section_name)
        container.setObjectName(section_name)
        # noinspection PyTypeChecker
        container.setProperty("class", section_class)

        # add QGroupBox to form or custom section
        # for custom section, the section is added to the form and registered in
        # self.sections, once all QGroupBox are rendered
        if section_class is not None:
            section_class.add_group_box(container)
        else:
            self.area_layout.addWidget(container)
            self.sections[section_name] = container

        # render fields
        form_layout = QGridLayout(container)
        form_layout.setContentsMargins(15, 10, 15, 10)

        row = 0
        for field_dict in section_data:
            name = field_dict["name"]
            label = QLabel(
                field_dict.get("label", self._get_field_label(field_dict))
            )
            base_label_style = "font-weight: bold"
            label.setStyleSheet(f"QLabel {{ {base_label_style} }}")

            label.setObjectName(f"{field_dict['name']}_label")
            if "hide_label" in field_dict:
                label.setHidden(field_dict["hide_label"])

            # default get be provided in field dict or in the form dict
            default = field_dict.get("default_value", None)
            if default is None and name in self.defaults:
                default = self.defaults[name]

            field = FormField(
                name=name,
                label=label.text(),
                value=field_dict["value"],
                default_value=default,
                field_type=field_dict.get("field_type"),
                field_args=field_dict.get("field_args"),
                help_text=field_dict.get("help_text"),
                min_value=field_dict.get("min_value"),
                max_value=field_dict.get("max_value"),
                suffix=field_dict.get("suffix"),
                form=self,
            )
            self.fields[name] = field
            if self.direction == "horizontal":
                label.setStyleSheet(
                    f"QLabel {{ {base_label_style}; padding-top: 10px; }}"
                )
                form_layout.addWidget(label, row, 1, Qt.AlignTop)
                form_layout.addWidget(field, row, 2)
                row += 1
            else:
                form_layout.addWidget(label, row, 1, Qt.AlignBottom)
                form_layout.addWidget(field, row + 1, 1)
                row += 2
            # message is already set before field was added to the form layout
            if field.message.text():
                field.message.show()

            # add to class attribute
            self.field_config[field_dict["name"]] = field_dict

    def find_field_by_name(self, name: str) -> FormField | None:
        """
        Find a form field by its name.
        :param name: The field name.
        :return: The field instance or None if it does not exist.
        """
        # noinspection PyTypeChecker
        return self.findChild(FormField, name)

    def register_after_render_action(self, action: Callable) -> None:
        """
        Registers an action to execute after the whole form has been rendered and all
        fields are available.
        :param action: The action to execute.
        :return: None.
        """
        self.after_render_section_actions.append(action)

    def change_field_visibility(
        self,
        name: str,
        show: bool,
        clear_message: bool = True,
        disable_on_hide: bool = False,
        throw_if_missing: bool = True,
    ) -> None:
        """
         Changes the visibility of the field (input and label).
        :param name: The field name.
        :param show: True to show the field, False to hide it.
        :param clear_message: Remove any error message set on the field.
        Default to True.
        :param disable_on_hide: Disable the field on hide, enable it on show.
        :param throw_if_missing: Throw an exception if the field does not exist.
        Default to True
        :return: None.
        """
        # noinspection PyTypeChecker
        field: FormField = self.find_field_by_name(name)
        if field is None:
            if throw_if_missing:
                raise ValueError(f"The field {name} does not exist")
            else:
                return
        field.setVisible(show)
        if disable_on_hide is True:
            field.setEnabled(show)

        # if clear_message is True and show is False:
        if clear_message is True:
            field.clear_message("warning")

        # noinspection PyUnresolvedReferences
        self.findChild(QLabel, f"{name}_label").setVisible(show)

    @staticmethod
    def _get_field_label(field_dict: dict) -> str:
        """
        Returns the field label.
        :param field_dict: The field configuration.
        :return: The label.
        """
        if "label" in field_dict:
            return field_dict["label"]
        return humanise_label(field_dict["name"])

    def get_field_label_from_name(self, name: str) -> str:
        """
        Returns the field label.
        :param name: The name of the field.
        :return: The label.
        """
        if name not in self.field_config:
            raise ValueError(f"The form field named '{name}' does not exist")

        field_dict = self.field_config[name]
        return self._get_field_label(field_dict)

    def _validate_field(
        self, name: str, value: str | bool, form_field: FormField
    ) -> bool:
        """
        Validates a field before saving the form. This checks if a field is empty
        (when allow_empty is False) and runs a custom validation (when the
        "validate_fun" key is set in the form dictionary or a custom widget has the
        validate method).
        :param name: The field name to validate.
        :param value: The field set value.
        :param form_field: The FormField instance.
        :return: True if the field passes validation, False otherwise.
        """
        self.logger.debug(f"Validating '{name}' with '{value}'")
        field_dict = self.field_config[name]
        form_label = self.get_field_label_from_name(name)
        form_field.clear_message()

        # check field is not empty
        if (
            "allow_empty" in field_dict
            and field_dict["allow_empty"] is False
            and (value == "" or value is None)
        ):
            self.logger.debug("Field cannot be empty")
            form_field.set_error_message("The field cannot be empty")
            return False

        # custom validation functions returning FormValidation
        if "validate_fun" in field_dict or form_field.is_custom_widget:
            output: FormValidation | None = None
            if form_field.is_custom_widget:
                output = form_field.widget.validate(name, form_label, value)

            if "validate_fun" in field_dict:
                validate_fun = field_dict["validate_fun"]
                # custom widget has not failed validation, otherwise preserve first
                # message
                if form_field.is_custom_widget and output.validation is True:
                    output = validate_fun(name, form_label, value)
                # any other case
                elif form_field.is_custom_widget is False:
                    output = validate_fun(name, form_label, value)

            if not isinstance(output, FormValidation):
                raise TypeError(
                    f"Custom validation for {name} must return FormValidation"
                )

            if output.validation is False:
                form_field.set_error_message(output.error_message)
                return False

        return True

    def validate(self) -> bool | dict[str, Any]:
        """
        Event to execute before saving the form. Validation of hidden fields or fields
        in hidden sections is ignored and the field values is not returned.
        :return: The form values as dictionary or False if the form does not validate.
        """
        form_data = {}
        is_valid = True

        if self.loaded is False:
            raise ValueError(
                "You must load the form first using the load_fields() method"
            )

        # Loop through fields in sections
        for section_name, section_widget in self.sections.items():
            self.logger.debug(
                f"Processing {section_widget.__class__.__name__}({section_name})"
            )

            # ignore hidden/disabled sections
            if section_widget.isEnabled() is False or section_widget.isHidden():
                self.logger.debug("Skipped. Section is hidden or disabled")
                continue

            for field in section_widget.findChildren(FormField):
                field: FormField
                widget = field.widget

                # ignore hidden fields - check parent as workaround when visibility
                # prop of a widget does not propagate to its children
                if field.isHidden() or field.parent().isHidden():
                    continue

                name = field.objectName()
                if name == "" or name is None:
                    raise ValueError(
                        f"The form field {widget} does not have an objectName set"
                    )

                # store key only if value is different from the default value
                # noinspection PyTypeChecker
                default_value = widget.property("default_value")
                value = field.value()

                if not self._validate_field(name, value, field):
                    is_valid = False

                # do not export if the value is empty or the default value
                if (
                    value == default_value
                    or value is None
                    or value == ""
                    or value == []
                    or value == {}
                ):
                    self.logger.debug(f"Ignoring {name} with value '{value}'")
                    continue
                else:
                    form_data[name] = value

                # the widget event after_validate can manipulate the form dictionary
                if field.is_custom_widget:
                    self.logger.debug(f"Running after_validate on '{name}'")
                    getattr(widget, "after_validate")(form_data, name)

        if is_valid is False:
            QMessageBox().critical(
                self,
                "Cannot save the form",
                "The form cannot be updated because it contains errors",
            )
            return False

        self.logger.debug(f"Collected {form_data}")

        # each custom section can manipulate/filter the form dictionary
        for section_name, section in self.sections.items():
            # additional validation run by custom form sections after all widgets are
            # validated
            if hasattr(section, "validate"):
                self.logger.debug(
                    f"Validating data by {section.__class__.__name__}({section_name}) "
                    + f"with {form_data}"
                )
                output = section.validate(form_data)
                if output.validation is False:
                    QMessageBox().critical(
                        self,
                        "Cannot save the form",
                        output.error_message,
                    )
                    return False

            # custom sections can manipulate the form data
            if hasattr(section, "filter"):
                self.logger.debug(
                    f"Filtering form data by {section.name} with {form_data}"
                )
                section.filter(form_data)

        # disable save button
        if self.save_button is not None:
            self.save_button.setEnabled(False)

        return form_data

    @Slot(str)
    def on_field_changed(self) -> None:
        """
        Slot called when a field in the form changes.
        :return: None
        """
        if not self.save_button.isEnabled():
            self.logger.debug(
                f"Save button enabled because {get_signal_sender(self)}"
            )
            self.save_button.setEnabled(True)


class FormContainer(QWidget):
    def __init__(self, parent: Form):
        """
        Initialises the form container.
        :param parent: The parent widget.
        """
        super().__init__()
        self.setStyleSheet(
            "FormContainer { background: transparent; border:1px solid blue }"
        )


class FormTitle(QLabel):
    def __init__(self, title: str = "", parent: QWidget = None):
        super().__init__(title, parent)
        self.setStyleSheet("font-size: 20px")
