import pytest
from PySide6.QtCore import QItemSelectionModel, Qt, QTimer
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

import pywr_editor
from pywr_editor.dialogs import (
    ConstantParameterSection,
    MonthlyProfileParameterSection,
    ParameterDialogForm,
    ParametersDialog,
)
from pywr_editor.dialogs.parameters.parameter_empty_page_widget import (
    ParameterEmptyPageWidget,
)
from pywr_editor.form import FormField, ParameterTypeSelectorWidget, TextWidget
from pywr_editor.model import ModelConfig, PywrParametersData
from tests.utils import close_message_box, resolve_model_path


class TestParametersDialog:
    """
    Tests the general behaviour of the parameter dialog (when adding or deleting
    parameters, etc.)
    """

    model_file = resolve_model_path("model_dialog_parameters.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.fixture()
    def dialog(self, model_config) -> ParametersDialog:
        """
        Initialises the dialog.
        :param model_config: The ModelConfig instance.
        :return: The ParameterDialog instance.
        """
        dialog = ParametersDialog(model_config)
        dialog.show()
        return dialog

    def test_add_new_parameter(self, qtbot, model_config, dialog):
        """
        Tests that a new parameter can be correctly added.
        """
        parameter_list_widget = dialog.parameters_list_widget
        pages_widget = dialog.pages_widget
        add_button: QPushButton = pages_widget.empty_page.findChild(
            QPushButton, "add_button"
        )
        qtbot.mouseClick(add_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        # new name is random
        new_name = list(pages_widget.pages.keys())[-1]
        assert "Parameter " in new_name

        # Parameter model
        # the parameter is added to the model internal list
        assert new_name in parameter_list_widget.model.parameter_names
        # the parameter appears in the parameters list on the left-hand side of the
        # dialog
        new_model_index = parameter_list_widget.model.index(
            model_config.parameters.count - 1, 0
        )
        assert new_model_index.data() == new_name

        # the item is selected
        assert parameter_list_widget.list.selectedIndexes()[0].data() == new_name

        # Page widget
        selected_page = pages_widget.currentWidget()
        selected_page.findChild(ParameterDialogForm).load_fields()
        assert new_name in selected_page.findChild(QLabel).text()
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        # button is disabled
        assert save_button.isEnabled() is False

        # the parameter is in the widgets list
        assert new_name in pages_widget.pages.keys()
        # the form page is selected
        assert selected_page == pages_widget.pages[new_name]
        # the form is filled with the name and type is constant
        name_field = selected_page.findChild(FormField, "name")
        type_field: FormField = selected_page.findChild(FormField, "type")
        value_field: FormField = selected_page.findChild(FormField, "value")
        assert name_field.value() == new_name
        assert type_field.value() == "constant"

        # the model is updated
        assert model_config.has_changes is True
        assert model_config.parameters.exists(new_name) is True
        assert model_config.parameters.config(new_name) == {
            "type": "constant",
            "value": 0,
        }

        # rename and save
        renamed_parameter_name = "A new shiny name"
        new_value = 1.11  # value is mandatory
        name_field.widget.line_edit.setText(renamed_parameter_name)
        value_field.widget.line_edit.setText(str(new_value))

        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""
        assert value_field.message.text() == ""

        # the page widget is renamed
        assert renamed_parameter_name in pages_widget.pages.keys()
        assert renamed_parameter_name in selected_page.findChild(QLabel).text()

        # model configuration
        assert model_config.parameters.exists(new_name) is False
        assert model_config.parameters.exists(renamed_parameter_name) is True
        assert model_config.parameters.config(renamed_parameter_name) == {
            "type": "constant",
            "value": new_value,
        }

    def test_clone_parameter(self, qtbot, model_config, dialog):
        """
        Tests the clone parameter button.
        """
        pages_widget = dialog.pages_widget
        current_param = "dataframe_param"

        # Page widget
        pages_widget.set_current_widget_by_name(current_param)
        selected_page = pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        selected_page.findChild(ParameterDialogForm).load_fields()

        assert selected_page.name == current_param

        # Clone the parameter
        # noinspection PyTypeChecker
        clone_button: QPushButton = selected_page.findChild(QPushButton, "clone_button")
        qtbot.mouseClick(clone_button, Qt.MouseButton.LeftButton)

        # new name is random
        new_name = list(pages_widget.pages.keys())[-1]
        assert "Parameter " in new_name
        # the parameter is in the widgets list
        assert new_name in pages_widget.pages.keys()

        # the form page is selected
        assert pages_widget.currentWidget() == pages_widget.pages[new_name]

        # the model is updated
        assert model_config.has_changes is True
        assert model_config.parameters.exists(new_name) is True
        assert model_config.parameters.config(new_name) == {
            "type": "dataframe",
            "url": "files/table.csv",
            "column": 0,
        }

    def test_rename_parameter(self, qtbot, model_config, dialog):
        """
        Tests that a parameter is renamed correctly.
        """
        current_name = "param_with_valid_excel_table"
        new_name = "Param X"
        pages_widget = dialog.pages_widget

        # select the parameter
        pages_widget.set_current_widget_by_name(current_name)
        selected_page = pages_widget.currentWidget()
        selected_page.form.load_fields()
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        name_field = selected_page.findChild(FormField, "name")

        # Change the name and save
        assert name_field.value() == current_name
        name_field.widget.line_edit.setText(new_name)

        qtbot.wait(200)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""
        assert selected_page.findChild(FormField, "index").message.text() == ""

        # the page widget is renamed
        assert new_name in pages_widget.pages.keys()
        assert new_name in selected_page.findChild(QLabel).text()

        # model has changes
        assert model_config.has_changes is True
        assert model_config.parameters.exists(current_name) is False
        assert model_config.parameters.exists(new_name) is True
        assert model_config.parameters.config(new_name) == {
            "type": "constant",
            "table": "Excel table",
            "index": 8,
            "column": "Column 2",
        }

        # set duplicated name
        name_field.widget.line_edit.setText("param1")
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert "already exists" in name_field.message.text()
        assert new_name in model_config.parameters.names

    def test_delete_parameter(self, qtbot, model_config, dialog):
        """
        Tests that a parameter is deleted correctly.
        """
        deleted_parameter = "const_param_with_values"
        parameter_list_widget = dialog.parameters_list_widget
        pages_widget = dialog.pages_widget
        dialog.show()

        # select a parameter from the list
        model_index = parameter_list_widget.model.index(1, 0)
        assert model_index.data() == deleted_parameter
        parameter_list_widget.list.selectionModel().select(
            model_index, QItemSelectionModel.Select
        )

        delete_button: QPushButton = pages_widget.pages[deleted_parameter].findChild(
            QPushButton, "delete_button"
        )

        # delete button is enabled and the item is selected
        assert delete_button.isEnabled() is True
        assert (
            parameter_list_widget.list.selectedIndexes()[0].data() == deleted_parameter
        )

        # delete
        def confirm_deletion():
            widget = QApplication.activeModalWidget()
            qtbot.mouseClick(widget.findChild(QPushButton), Qt.MouseButton.LeftButton)

        QTimer.singleShot(200, confirm_deletion)
        qtbot.mouseClick(delete_button, Qt.MouseButton.LeftButton)

        assert isinstance(pages_widget.currentWidget(), ParameterEmptyPageWidget)
        assert deleted_parameter not in pages_widget.pages.keys()
        assert model_config.parameters.exists(deleted_parameter) is False
        assert deleted_parameter not in parameter_list_widget.model.parameter_names

    def test_change_param_type(self, qtbot, model_config):
        """
        Tests that when a parameter type is changed, the form is properly updated.
        """
        param_name = "param_with_valid_excel_table"
        dialog = ParametersDialog(model_config, param_name)

        selected_page = dialog.pages_widget.currentWidget()
        name_field = selected_page.findChild(FormField, "name")
        assert name_field.value() == param_name

        param_type: FormField = selected_page.findChild(FormField, "type")
        # noinspection PyTypeChecker
        param_type_widget: ParameterTypeSelectorWidget = param_type.widget
        doc_button: QPushButton = param_type_widget.doc_button

        # 1. Change the parameter type
        spy = QSignalSpy(param_type_widget.combo_box.currentIndexChanged)
        param_type_widget.combo_box.setCurrentText("Monthly profile parameter")
        assert spy.count() == 1

        # 2. The previous - FormSection is removed and a new section is added
        new_section = selected_page.findChild(MonthlyProfileParameterSection)
        assert selected_page.findChild(ConstantParameterSection) is None
        assert new_section is not None
        # button URL is updated
        assert "Monthly" in doc_button.property("url")
        # new section has no warning
        for field in new_section.findChildren(FormField):
            if field.isVisible():
                assert field.message.text() == ""

        # 3. Reset
        param_type_widget.reset()
        assert selected_page.findChild(MonthlyProfileParameterSection) is None
        assert selected_page.findChild(ConstantParameterSection) is not None
        assert "Constant" in doc_button.property("url")

    def test_missing_sections(self, qtbot):
        """
        Checks that all built-in pywr parameters have a form section.
        """
        params_data = PywrParametersData()

        missing_sections = []
        for key, info in params_data.data.items():
            pywr_class = params_data.class_from_type(key)
            if not hasattr(pywr_editor.dialogs, f"{pywr_class}Section"):
                missing_sections.append(key)

        assert len(missing_sections) == 0, missing_sections

    def test_sections(self, qtbot, model_config):
        """
        Tests that the sections do not throw any exception when loaded.
        """
        param_name = "param_with_valid_excel_table"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        form = selected_page.form

        param_type_widget: ParameterTypeSelectorWidget = form.find_field("type").widget
        for name in param_type_widget.combo_box.all_items:
            param_type_widget.combo_box.setCurrentText(name)

    @pytest.mark.parametrize("imported", [False, True])
    def test_add_new_custom_parameter(self, qtbot, model_config, dialog, imported):
        """
        Tests that a new custom parameter can be correctly added. This tests
        the validation and filter in the CustomParameterSection
        """
        pages_widget = dialog.pages_widget
        add_button: QPushButton = pages_widget.empty_page.findChild(
            QPushButton, "add_button"
        )
        qtbot.mouseClick(add_button, Qt.MouseButton.LeftButton)

        # Page widget
        selected_page = pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        selected_page.findChild(ParameterDialogForm).load_fields()
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")

        # 1. Setup parameter
        # rename parameter
        name_widget: TextWidget = selected_page.findChild(FormField, "name").widget
        name_widget.line_edit.setText("Custom parameter")

        # select not imported parameter
        type_widget: ParameterTypeSelectorWidget = selected_page.findChild(
            FormField, "type"
        ).widget
        form = type_widget.field.form

        if not imported:
            type_widget.combo_box.setCurrentText("Custom parameter (not imported)")
            param_type = "ACustomParameter"

            # change type
            # noinspection PyTypeChecker
            custom_type_field: FormField = selected_page.findChild(
                FormField, "custom_type"
            )
            qtbot.wait(0.1)  # add delay so that the widget becomes visible
            # because class is not imported, the custom type is visible
            assert custom_type_field.isVisible() is True
            # set an invalid Python class
            custom_type_field.widget.line_edit.setText("A CustomParameter")
            QTimer.singleShot(100, close_message_box)
            form_data = form.validate()
            assert form_data is False
            assert "valid Python class" in custom_type_field.message.text()

            # set a valid Python class
            custom_type_field.widget.line_edit.setText(param_type)
        else:
            param_type = "MyParameter"
            type_widget.combo_box.setCurrentText(param_type)
            # noinspection PyTypeChecker
            custom_type_field: FormField = selected_page.findChild(
                FormField, "custom_type"
            )
            param_type = "my"
            assert custom_type_field.isVisible() is False

        # 2. Save the form
        qtbot.wait(0.1)  # add delay so that the form updates
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert model_config.parameters.config("Custom parameter") == {
            "type": param_type,
            "value": 0,
        }
