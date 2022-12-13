from typing import TYPE_CHECKING
from PySide6.QtWidgets import QPushButton
from pywr_editor.form import build_picker_form_fields, RecorderForm
from pywr_editor.model import RecorderConfig, ModelConfig


if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentPickerDialog

"""
 Form used by ModelComponentPickerDialog when the model
 component is a recorder
"""


class RecorderPickerFormWidget(RecorderForm):
    def __init__(
        self,
        component_obj: RecorderConfig,
        model_config: ModelConfig,
        save_button: QPushButton,
        parent: "ModelComponentPickerDialog",
        include_comp_key: list[str] | None = None,
    ):
        """
        Initialises the form.
        :param component_obj: The recorder instance.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param parent: The parent modal.
        :param include_comp_key: Filters the recorder types shown in the form by keys.
        The list is passed to the RecorderPickerWidget and RecorderTypeSelectorWidget.
        """
        super().__init__(
            model_config=model_config,
            recorder_obj=component_obj,
            available_fields=build_picker_form_fields(
                component_obj=component_obj,
                component_type="recorder",
                include_comp_key=include_comp_key,
            ),
            save_button=save_button,
            parent=parent,
            enable_optimisation_section=False,
        )

        self.load_fields()
