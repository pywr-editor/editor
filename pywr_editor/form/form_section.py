from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from .field_config import FieldConfig
from .validation import Validation

if TYPE_CHECKING:
    from pywr_editor.form import Form


class FormSection(QWidget):
    def __init__(self, form: "Form", section_data: dict):
        """
        Initialises a new custom form section.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__()
        self.form = form
        self.fields_: dict[str, list[FieldConfig]] = {}

        self.section_data = section_data
        self.setObjectName(type(self).__name__)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_group_box(self, group_box: QGroupBox) -> None:
        """
        Add the QGroupBox widget to the section layout.
        :param group_box: The QGroupBox widget instance.
        :return: None
        """
        self.layout.addWidget(group_box)

    @property
    def name(self) -> str:
        """
        Return the name of the custom section.
        :return: The section name.
        """
        return self.__class__.__name__

    def add_fields(self, field: dict[str, list[FieldConfig]]) -> None:
        """
        Add new fields to the sections.
        :param field: The fields to add.
        :return: None
        """
        self.fields_ = {**self.fields_, **field}

    # noinspection PyMethodMayBeStatic
    def validate(self, form_data: dict) -> Validation:
        """
        Validate the section/data after all the widgets are validated.
        :param form_data: The form data dictionary when the form validation is
        successfully.
        :return: The Validation instance.
        """
        return Validation()

    def filter(self, form_data: dict) -> None:
        """
        Filter the data form dictionary when the form is being saved. This method
        directly alters the dictionary.
        :param form_data: The form data dictionary when the form validation is
        successfully.
        :return: None.
        """
        return
