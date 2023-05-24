from pywr_editor.form import FloatWidget, FormField
from pywr_editor.utils import Logging


class ValueWidget(FloatWidget):
    def __init__(
        self,
        name: str,
        value: dict,
        parent: FormField,
    ):
        """
        Initialises the widget for a constant parameter. The parameter can be provided
        using either the "value" or "values" keys, but Pywr prioritises "value" when
        both keys are set.
        (see https://github.com/pywr/pywr/blob/4fa474717bca1ca1f99a2d1cdde775e33b89de14/pywr/parameters/_parameters.pyx#L183)   # noqa: E501
        The value can only be a float or int, and it does not depend on scenarios.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)

        self.model_config = self.form.model_config
        self.form.register_after_render_action(self.after_field_render)

    def after_field_render(self) -> None:
        """
        Fills the field and warns if the value is not a valid number.
        :return: None
        """
        fill_value = ""
        if self.value["values"] is not None and isinstance(
            self.value["values"], (int, float)
        ):
            fill_value = str(self.value["values"])
        elif self.value["value"] is not None and isinstance(
            self.value["value"], (int, float)
        ):
            fill_value = str(self.value["value"])
        elif all([val is None for val in self.value.values()]):
            fill_value = None
        self.logger.debug(f"Setting field value to '{fill_value}'")

        # value is not a number
        if fill_value is None:
            self.logger.debug("The value is None. Field left empty")
            return
        if fill_value == "":
            self.logger.debug("The value is not valid. Setting warn message")
            self.field.set_warning("The value in the model configuration is not valid")

        self.line_edit.setText(fill_value)

    def get_default_value(self) -> str:
        """
        The field default value use by self.get_value().
        :return: The default value.
        """
        return ""
