from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from .field_config import FieldConfig
from .form_validation import FormValidation

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
        self.section_data = section_data
        self.setObjectName(type(self).__name__)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_group_box(self, group_box: QGroupBox) -> None:
        """
        Adds the QGroupBox widget to the section layout.
        :param group_box: The QGroupBox widget instance.
        :return: None
        """
        self.layout.addWidget(group_box)

    @property
    def name(self) -> str:
        """
        Returns a name for the custom section.
        :return: The section name.
        """
        return self.__class__.__name__

    @property
    def data(self) -> dict[str, list[FieldConfig]]:
        """
        Defines the section data dictionaries list.
        :return: The section data.
        """
        raise NotImplementedError(
            "The section data property is not implemented"
        )

    # noinspection PyMethodMayBeStatic
    def validate(self, form_data: dict) -> FormValidation:
        """
        Validates the section/data after all the widgets are validated.
        :param form_data: The form data dictionary when the form validation is
        successfully.
        :return: The FormValidation instance.
        """
        return FormValidation(validation=True)

    def filter(self, form_data: dict) -> None:
        """
        Filters the data form dictionary when the form is being saved. This method
        directly alters the dictionary.
        :param form_data: The form data dictionary when the form validation is
        successfully.
        :return: None.
        """
        pass
