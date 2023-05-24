import os.path
from typing import Any

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.dialogs.node.node_dialog import NodeDialog
from pywr_editor.dialogs.parameters.sections.constant_parameter_section import (
    ConstantParameterSection,
)
from pywr_editor.dialogs.parameters.sections.monthly_profile_parameter_section import (
    MonthlyProfileParameterSection,
)
from pywr_editor.form import (
    FormCustomWidget,
    FormField,
    FormSection,
    ModelComponentPickerDialog,
    ModelComponentSourceSelectorWidget,
    ParameterPickerWidget,
    SourceSelectorWidget,
)
from pywr_editor.form.widgets.float_widget import FloatWidget
from pywr_editor.form.widgets.parameter_line_edit_widget import ParameterLineEditWidget
from pywr_editor.model import ModelConfig, ParameterConfig
from tests.utils import resolve_model_path


class TestDialogParameterPicker:
    """
    Tests the picker dialog, and its widgets, that is used to set a parameter as value
    of another parameter (for example the value in AbstractThresholdParameter)
    """

    model_file = resolve_model_path("model_dialog_parameter_picker.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(resolve_model_path(self.model_file))

    def get_form_data(
        self, form_data: str | dict[str, Any], additional_data: Any
    ) -> None:
        """
        Gets the validated form data after the Save button is clicked.
        This is used as callback function for ModelComponentPickerDialog.
        :param form_data: The form data.
        :param additional_data: Additional data to send to the parent widget.
        :return: None
        """
        self._form_data = form_data

    def test_valid_model_parameter(self, qtbot, model_config):
        """
        Tests the dialog when the value is a string (i.e. an existing model parameter).
        This also tests the ParameterPickerWidget.
        """
        child_param_name = "constant_param"
        # object passed by ParameterLineEditWidget
        param_obj = model_config.parameters.config(child_param_name, as_dict=False)
        parent = QWidget()
        qtbot.addWidget(parent)
        dialog = ModelComponentPickerDialog(
            model_config=model_config,
            component_obj=param_obj,
            component_type="parameter",
            parent=parent,
            after_form_save=self.get_form_data,
        )
        dialog.show()

        # 1. Check parameter source
        param_source_widget: ModelComponentSourceSelectorWidget = (
            dialog.form.find_field("comp_source").widget
        )
        assert (
            param_source_widget.combo_box.currentText()
            == param_source_widget.labels["model_component"]
        )

        # 2. Check model parameter list widget
        # noinspection PyTypeChecker
        model_param_field: FormField = dialog.form.find_field("comp_name")
        model_param_widget: ParameterPickerWidget = model_param_field.widget
        assert model_param_widget.combo_box.currentText() == child_param_name
        assert model_param_field.message.text() == ""

        # 3. Check visibility
        # no custom section
        assert dialog.findChild(FormSection) is None
        # parameter selector is visible
        assert model_param_field.isHidden() is False

        # 4. Validate form
        # noinspection PyTypeChecker
        save_button: QPushButton = dialog.findChild(QPushButton, "save_button")
        assert save_button.isEnabled() is False
        # enable button
        save_button.setEnabled(True)

        # send form
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert self._form_data == child_param_name

        # 5. Change source to new anonymous parameter
        param_source_widget.combo_box.setCurrentText(
            param_source_widget.labels["new_component"]
        )
        # custom section added for CustomParameter (default)
        # noinspection PyTypeChecker
        section: ConstantParameterSection = dialog.findChild(FormSection)
        assert section.name == "ConstantParameterSection"
        # all fields are empty
        for form_field in section.findChildren(FormField):
            form_field: FormField
            assert form_field.message.text() == ""
        # parameter selector is hidden
        assert model_param_field.isHidden() is True

    def test_invalid_model_parameter(self, qtbot, model_config):
        """
        Tests the dialog when the value is a string (i.e. a model parameter) but the
        parameter does not exist.
        """
        child_param_name = "non_existing_parameter"
        # object passed by ParameterLineEditWidget
        param_obj = ParameterConfig(props={}, name=child_param_name)
        dialog = ModelComponentPickerDialog(
            model_config=model_config,
            component_obj=param_obj,
            component_type="parameter",
        )
        dialog.hide()

        # 1. Check parameter source
        param_source_widget: ModelComponentSourceSelectorWidget = (
            dialog.form.find_field("comp_source").widget
        )
        assert (
            param_source_widget.combo_box.currentText()
            == param_source_widget.labels["model_component"]
        )

        # 2. Check model parameter list widget
        # noinspection PyTypeChecker
        model_param_field: FormField = dialog.form.find_field("comp_name")
        model_param_widget: ParameterPickerWidget = model_param_field.widget
        # parameter selector is visible
        assert model_param_field.isHidden() is False
        assert model_param_widget.combo_box.currentText() == "None"
        assert "does not exist" in model_param_field.message.text()

        # no custom section
        assert dialog.findChild(FormSection) is None

        # 3. Validate widget
        assert (
            model_param_widget.validate(
                "", "", model_param_widget.get_value()
            ).validation
            is False
        )

    # noinspection PyTypeChecker
    @pytest.mark.parametrize(
        "param_dict, section_class, source_type",
        [
            # monthly profile
            (
                {
                    "type": "monthlyprofile",
                    "values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                },
                MonthlyProfileParameterSection,
                "value",
            ),
            # constant from url
            (
                {
                    "type": "constant",
                    "url": os.path.normpath("files/table.xlsx"),
                    "sheet_name": "Sheet 1",
                    "index_col": ["Column 2"],
                    "column": "Column 3",
                    "index": 1,
                },
                ConstantParameterSection,
                "anonymous_table",
            ),
            # constant from table
            (
                {
                    "type": "constant",
                    "table": "csv_table",
                    "index": [5, 6],
                    "column": " Date",
                },
                ConstantParameterSection,
                "table",
            ),
        ],
    )
    def test_valid_anonymous_parameter(
        self, qtbot, model_config, param_dict, section_class, source_type
    ):
        """
        Tests the dialog when the value is a dictionary containing an anonymous
        parameter.
        """
        # object passed by ParameterLineEditWidget
        param_obj = ParameterConfig(props=param_dict)

        parent = QWidget()
        qtbot.addWidget(parent)
        dialog = ModelComponentPickerDialog(
            model_config=model_config,
            component_obj=param_obj,
            component_type="parameter",
            parent=parent,
            after_form_save=self.get_form_data,
        )
        dialog.show()

        # 1. Check parameter source
        param_source_widget: ModelComponentSourceSelectorWidget = (
            dialog.form.find_field("comp_source").widget
        )
        assert (
            param_source_widget.combo_box.currentText()
            == param_source_widget.labels["new_component"]
        )

        # 2. Check custom section
        section: FormSection = dialog.findChild(section_class)
        assert section is not None

        # 3. ParameterPickerWidget is hidden
        # noinspection PyTypeChecker
        model_param_field: FormField = dialog.form.find_field("comp_name")
        # noinspection PyTypeChecker
        model_param_widget: ParameterPickerWidget = model_param_field.widget
        assert model_param_field.message.text() == ""
        assert model_param_field.isHidden() is True
        assert model_param_widget.combo_box.currentText() == "None"

        # 5. Check filled form fields
        # check source widget
        source_selector: SourceSelectorWidget = section.findChild(SourceSelectorWidget)
        assert source_selector.get_value() == source_selector.labels[source_type]

        # check all others
        for key, value in param_dict.items():
            if key == "type":
                continue
            widget: FormCustomWidget = dialog.form.find_field(key).widget
            assert widget.get_value() == value

        # 6. Form validation (must return the same dictionary)
        save_button: QPushButton = dialog.findChild(QPushButton, "save_button")
        assert save_button.isEnabled() is False
        # enable button
        save_button.setEnabled(True)

        # send form
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        if "sheet_name" in param_dict:
            param_dict["index_col"] = [1]
        assert self._form_data == param_dict

        # 7. Change source to new model parameter
        param_source_widget.combo_box.setCurrentText(
            param_source_widget.labels["model_component"]
        )
        # custom section is removed and ParameterPickerWidget is shown
        section = dialog.findChild(FormSection)
        assert section is None

        assert model_param_field.message.text() == ""
        assert model_param_field.isHidden() is False
        assert model_param_widget.combo_box.currentText() == "None"

    def test_save_button_status(self, qtbot):
        """
        Tests that the save button in the parent form is enabled if a change is applied
        to the child form. This is tested by changing a node property.
        """
        dialog = NodeDialog(
            model_config=ModelConfig(
                resolve_model_path("model_dialog_node_storage_section.json")
            ),
            node_name="Reservoir",
        )
        dialog.hide()

        form = dialog.form
        save_button = form.save_button
        # the button is initially disabled
        assert save_button.isEnabled() is False

        # open the dialog and update the child form
        volume_widget: ParameterLineEditWidget = form.find_field("max_volume").widget
        qtbot.mouseClick(volume_widget.select_button, Qt.MouseButton.LeftButton)

        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = dialog.findChild(
            ModelComponentPickerDialog
        )
        # noinspection PyTypeChecker
        child_save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )
        assert child_save_button.isEnabled() is False

        # type a number
        value_widget: FloatWidget = child_dialog.form.find_field("value").widget
        qtbot.keyPress(value_widget.line_edit, Qt.Key.Key_1)
        # the nested save button is enabled
        assert child_save_button.isEnabled() is True

        # save the form and the main save button gets enabled
        qtbot.mouseClick(child_save_button, Qt.MouseButton.LeftButton)
        assert save_button.isEnabled() is True
