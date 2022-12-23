from typing import TYPE_CHECKING

from PySide6.QtWidgets import QPushButton

from pywr_editor.form import ParameterForm, build_picker_form_fields
from pywr_editor.model import ModelConfig, ParameterConfig

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentPickerDialog

"""
 Form used by ModelComponentPickerDialog when the model
 component is a parameter
"""


class ParameterPickerFormWidget(ParameterForm):
    def __init__(
        self,
        component_obj: ParameterConfig,
        model_config: ModelConfig,
        save_button: QPushButton,
        parent: "ModelComponentPickerDialog",
        include_comp_key: list[str] | None = None,
    ):
        """
        Initialises the form.
        :param component_obj: The parameter instance.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param parent: The parent modal.
        :param include_comp_key: Filters the parameter types shown in the form by keys.
        The list is passed to the ParameterPickerWidget and ParameterTypeSelectorWidget.
        """
        super().__init__(
            model_config=model_config,
            parameter_obj=component_obj,
            available_fields=build_picker_form_fields(
                component_obj=component_obj,
                component_type="parameter",
                include_comp_key=include_comp_key,
            ),
            save_button=save_button,
            parent=parent,
            enable_optimisation_section=False,
        )

        self.load_fields()
