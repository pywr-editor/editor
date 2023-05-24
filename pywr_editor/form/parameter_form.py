from PySide6.QtWidgets import QMessageBox, QPushButton, QWidget

from pywr_editor.form import BooleanWidget, FieldConfig, ModelComponentForm
from pywr_editor.model import ModelConfig, ParameterConfig
from pywr_editor.utils import Logging

"""
 This widgets define a base class of a form that change a parameter
 configuration. For example, this can be used to add or change an
 existing parameter defined in the model configuration section or to
 add or change a value of a parameter that is another Parameter.

 This class does not render any field. The form can be validated
 and its configuration can be returned by calling the self.save()
 method.
"""


class ParameterForm(ModelComponentForm):
    def __init__(
        self,
        model_config: ModelConfig,
        parameter_obj: ParameterConfig | None,
        fields: dict,
        save_button: QPushButton,
        parent: QWidget,
        enable_optimisation_section: bool = True,
    ):
        """
        Initialises the parameter form.
        :param model_config: The ModelConfig instance.
        :param parameter_obj: The ParamConfig instance of the selected parameter.
        :param save_button: The button used to save the form.
        :param parent: The parent widget.
        :param enable_optimisation_section: If False the optimisation section of a
        parameter will not be shown. Default to True.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        self.parameter_obj = parameter_obj
        if parameter_obj is not None:
            self.parameter_dict = parameter_obj.props
        else:
            self.parameter_dict = {}

        super().__init__(
            form_dict=self.parameter_dict,
            model_config=model_config,
            fields=fields,
            save_button=save_button,
            parent=parent,
        )

        # clean up dictionary if it contains mixed configurations
        # (for example for table and external file)
        self.clean_keys()
        self.section_form_data["parameter_obj"] = self.parameter_obj
        self.section_form_data[
            "enable_optimisation_section"
        ] = enable_optimisation_section
        self.params_data = model_config.pywr_parameter_data
        self.show_warning = False

    def load_fields(self) -> None:
        """
        Loads the fields.
        :return: None
        """
        if self.loaded_ is True:
            return

        if self.show_warning:
            QMessageBox.warning(
                self,
                "Mixed configuration",
                "The parameter configuration has been adjusted because it contained "
                "mixed configurations. This happens when you edited the model "
                "configuration file manually and you connected the parameter, for "
                "example, to a table and an external file at the same time.\n\n"
                "If the configuration is not what you expect, manually edit the model "
                "file and restart the editor. Pywr always uses this priority order for "
                "the dictionary keys: 'value', 'table' and 'url'",
                QMessageBox.StandardButton.Ok,
            )

        super().load_fields()

    def clean_keys(self) -> None:
        """
        Cleans up the parameter dictionary if it contains mixed configurations (for
        example for table and external file) Pywr priority order is value -> table
        -> url.
        :return: None
        """
        keys = self.parameter_dict.keys()
        keys_to_del = []

        if "value" in keys or "values" in keys:
            keys_to_del = ["table", "url", "index_col", "parse_dates"]
        elif "table" in keys:
            keys_to_del = ["value", "values", "url", "index_col", "parse_dates"]
        elif "url" in keys:
            keys_to_del = ["value", "values", "table"]

        for key in keys_to_del:
            if key in keys:
                del self.parameter_dict[key]

                # show message only with url, table and value keys
                if key not in ["index_col", "parse_dates"]:
                    self.show_warning = True

    @property
    def is_variable_field(self) -> dict:
        """
        Returns the form configuration for the "is_variable" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="is_variable",
            value=self.field_value("is_variable"),
            field_type=BooleanWidget,
            default_value=False,
            help_text="If Yes, this parameter will change between the lower and "
            "upper bound provided below during optimisation",
        )
