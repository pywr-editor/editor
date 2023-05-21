from typing import TYPE_CHECKING, Union

from pywr_editor.form import FormField, FormValidation, ModelParameterPickerWidget

if TYPE_CHECKING:
    from pywr_editor.form import ParameterPickerFormWidget, RecorderPickerFormWidget

"""
 This widgets inherits from ModelParameterPickerWidget but
 with a different validation method and is used by the
 ParameterPickerFormWidget.
"""


class ParameterPickerWidget(ModelParameterPickerWidget):
    def __init__(self, name: str, value: str | None, parent: FormField, **kwargs):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected parameter name.
        :param parent: The parent widget.
        """
        super().__init__(name, value, parent, **kwargs)

    def validate(self, name: str, label: str, value: str) -> FormValidation:
        """
        Validates the value. The name is mandatory only if the value of
        ModelComponentSelectorWidget is set to "model_component".
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The instance of FormValidation
        """
        self.form: Union["ParameterPickerFormWidget", "RecorderPickerFormWidget"]
        return self.validate_model_component(value, self.form)

    @staticmethod
    def validate_model_component(
        component_value: str | None,
        form: Union["ParameterPickerFormWidget", "RecorderPickerFormWidget"],
    ) -> FormValidation:
        """
        Validates the field to select a model parameter or recorder. The field is
        mandatory only if the value of ModelComponentSourceSelectorWidget is set to
        "model_component".
        :param component_value: The selected component.
        :param form: The instance of the form.
        :return: The instance of FormValidation
        """
        component_source_widget = form.find_field_by_name("comp_source").widget
        if (
            component_source_widget.get_value()
            == component_source_widget.labels["model_component"]
            and component_value == "None"
        ):
            return FormValidation(
                validation=False,
                error_message="You must select an item",
            )
        return FormValidation(validation=True)
