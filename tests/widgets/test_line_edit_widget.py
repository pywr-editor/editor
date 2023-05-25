import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import ParameterPageWidget
from pywr_editor.dialogs.parameters.sections.storage_threshold_parameter_section import (  # noqa: E501
    StorageThresholdParameterSection,
)
from pywr_editor.form import (
    ColumnWidget,
    FormField,
    IndexColWidget,
    IndexWidget,
    ModelComponentPickerDialog,
    ModelComponentSourceSelectorWidget,
    MonthlyValuesWidget,
    ParameterForm,
    ParameterLineEditWidget,
    ParameterPickerWidget,
    ParameterTypeSelectorWidget,
    SourceSelectorWidget,
    StoragePickerWidget,
    TableSelectorWidget,
    UrlWidget,
    ValueWidget,
)
from pywr_editor.model import ModelConfig, ParameterConfig, PywrParametersData
from pywr_editor.widgets import ComboBox
from tests.utils import resolve_model_path


class TestDialogParameterLineEditWidget:
    """
    Tests the ParameterLineEditWidget.
    """

    model_file = resolve_model_path("model_dialog_parameter_line_edit_widget.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, threshold_param_type, expected_field_str, expected_value, expected_param_obj",  # noqa: E501
        [
            (
                "valid_model_param_constant",
                "constant",
                "constant_param",
                "constant_param",
                ParameterConfig(
                    props={"type": "constant", "value": 23},
                    name="constant_param",
                ),
            ),
            (
                "valid_model_param_monthly",
                "monthlyprofile",
                "monthly_param",
                "monthly_param",
                ParameterConfig(
                    props={
                        "type": "monthlyprofile",
                        "values": list(range(1, 13)),
                    },
                    name="monthly_param",
                ),
            ),
            (
                "valid_number",
                "constant",
                "Constant",
                10,
                ParameterConfig(props={"type": "constant", "value": 10}),
            ),
            (
                "valid_dict",
                "monthlyprofile",
                "Monthly profile",
                {"type": "monthlyprofile", "values": list(range(1, 13))},
                ParameterConfig(
                    props={
                        "type": "monthlyprofile",
                        "values": list(range(1, 13)),
                    },
                ),
            ),
            (
                "valid_custom_parameter",
                "custom",
                "customParameter",
                {"type": "customParameter", "value": 2},
                ParameterConfig(props={"type": "customParameter", "value": 2}),
            ),
        ],
    )
    def test_valid(
        self,
        qtbot,
        model_config,
        param_name,
        threshold_param_type,
        expected_field_str,
        expected_value,
        expected_param_obj,
    ):
        """
        Tests the ParameterLineEditWidget that is properly loaded when a valid
        configuration is passed.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        threshold_field = form.find_field("threshold")
        threshold_widget: ParameterLineEditWidget = threshold_field.widget
        assert form.find_field("name").value() == param_name

        # 1. Check field is loaded properly
        assert threshold_field.message.text() == ""
        assert threshold_widget.component_obj.key == threshold_param_type
        assert threshold_widget.line_edit.text() == expected_field_str
        # check component_obj
        assert threshold_widget.component_obj.props == expected_param_obj.props
        assert threshold_widget.component_obj.name == expected_param_obj.name

        # 2. Test get_value and validate()
        assert threshold_widget.get_value() == expected_value
        assert (
            threshold_widget.validate("", "", threshold_widget.get_value()).validation
            is True
        )

        # 3. Test reset
        qtbot.mouseClick(threshold_widget.clear_button, Qt.MouseButton.LeftButton)
        assert threshold_widget.line_edit.text() == "Not set"
        assert threshold_widget.component_obj is None
        assert not threshold_widget.line_edit.actions()

    @pytest.mark.parametrize(
        "param_name, message",
        [
            ("invalid_empty_dict", "is not valid"),
            ("invalid_empty_str", "is not valid"),
            ("invalid_type", "is not valid"),
            (
                "invalid_non_existing_model_param",
                "model parameter does not exist",
            ),
            ("valid_empty", ""),
        ],
    )
    def test_invalid(self, qtbot, model_config, param_name, message):
        """
        Tests the ParameterLineEditWidget when a wrong configuration is provided.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        threshold_field: FormField = selected_page.findChild(FormField, "threshold")
        # noinspection PyTypeChecker
        threshold_widget: ParameterLineEditWidget = threshold_field.widget
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Check message and value
        assert message in threshold_field.message.text()
        if param_name == "invalid_non_existing_model_param":
            assert threshold_widget.component_obj.props == {}
            assert threshold_widget.component_obj.name == "Not_found"
            assert threshold_widget.line_edit.text() == "Not_found"
            # check component_obj
            assert threshold_widget.component_obj.props == {}
            assert threshold_widget.component_obj.name == "Not_found"
        else:
            assert threshold_widget.component_obj is None
            assert threshold_widget.line_edit.text() == "Not set"
            # check component_obj
            assert threshold_widget.component_obj is None

        # 2. Test validate()
        assert threshold_widget.get_value() is None
        validation_obj = threshold_widget.validate("", "", threshold_widget.get_value())
        assert validation_obj.validation is False
        assert "must provide a valid parameter" in validation_obj.error_message

    @staticmethod
    def add_parameter_with_checks(
        qtbot, model_config
    ) -> [
        ParameterLineEditWidget,
        ModelComponentPickerDialog,
        ParametersDialog,
        ParameterPageWidget,
    ]:
        """
        Adds a new model parameter.
        :param qtbot: The qtbot instance.
        :param model_config: The ModelConfig instance.
        :return: A tuple with ParameterLineEditWidget, ModelComponentPickerDialog,
        ParametersDialog and ParameterPageWidget instances.
        """
        dialog = ParametersDialog(model_config)
        dialog.show()

        add_button: QPushButton = dialog.pages_widget.empty_page.findChild(
            QPushButton, "add_button"
        )

        # 1. Add new parameter and select ThresholdParameter
        qtbot.mouseClick(add_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        # 2. Load fields
        page = dialog.pages_widget.currentWidget()
        form = page.form
        form.load_fields()

        # 3. Check type selector and the section is loaded
        type_selector_widget: ParameterTypeSelectorWidget = form.find_field(
            "type"
        ).widget
        type_selector_widget.combo_box.setCurrentText("Storage threshold parameter")
        # noinspection PyTypeChecker
        section: StorageThresholdParameterSection = dialog.findChild(
            StorageThresholdParameterSection
        )
        assert section is not None

        # set other mandatory parameters
        # noinspection PyTypeChecker
        storage_node: StoragePickerWidget = dialog.findChild(StoragePickerWidget)
        selected_index = storage_node.combo_box.findData("Reservoir", Qt.UserRole)
        storage_node.combo_box.setCurrentIndex(selected_index)

        # 4. Add the threshold value
        param_line_edit_widget: ParameterLineEditWidget = form.find_field(
            "threshold"
        ).widget
        qtbot.mouseClick(
            param_line_edit_widget.select_button, Qt.MouseButton.LeftButton
        )

        # 5. Fill in the form
        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = dialog.findChild(
            ModelComponentPickerDialog
        )

        return param_line_edit_widget, child_dialog, dialog, page

    @staticmethod
    def save_main_form(
        qtbot, model_config: ModelConfig, page: ParameterPageWidget, value: dict
    ) -> None:
        """ "
        Saves the main form.
        :param qtbot: The qtbot instance.
        :param model_config: The ModelConfig instance.
        :param page: The ParameterPageWidget instance.
        :param value: The new parameter dictionary to validate.
        """
        # noinspection PyTypeChecker
        main_save_button: QPushButton = page.findChild(QPushButton, "save_button")
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.wait(200)
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        name = page.form.find_field("name").widget.line_edit.text()
        assert model_config.parameters.config(name) == value

    # noinspection PyTypeChecker
    def test_add_new_constant_parameter(self, qtbot, model_config):
        """
        Tests when a new constant parameter is added in the widget. The test creates a
        new child parameter in the dialog window.
        """
        # add a new storage threshold parameter
        (
            param_line_edit_widget,
            child_dialog,
            main_dialog,
            page,
        ) = self.add_parameter_with_checks(qtbot, model_config)

        # 1. Fill in the form
        # select source
        source_selector: SourceSelectorWidget = child_dialog.findChild(
            SourceSelectorWidget
        )
        source_selector.combo_box.setCurrentText(source_selector.labels["value"])
        value_widget: ValueWidget = child_dialog.findChild(ValueWidget)
        new_value = 1.4571
        value_widget.line_edit.setText(str(new_value))

        # 2. Save and close the form and then check the ParameterLineEditWidget
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # constant parameter is converted from dictionary to float
        assert param_line_edit_widget.get_value() == new_value

        # save the entire form
        self.save_main_form(
            qtbot,
            model_config,
            page,
            {
                "type": "storagethreshold",
                "storage_node": "Reservoir",
                "predicate": "LT",
                "values": [0.0, 0.0],
                "threshold": new_value,
            },
        )

        # 3. Test that, when parameter is changed, the field is updated correctly
        qtbot.mouseClick(
            param_line_edit_widget.select_button, Qt.MouseButton.LeftButton
        )

        # set model parameter
        source_widget: ModelComponentSourceSelectorWidget = child_dialog.findChild(
            ModelComponentSourceSelectorWidget
        )
        source_widget.combo_box.setCurrentText(source_widget.labels["model_component"])

        # pick last parameter
        model_param_widget: ParameterPickerWidget = child_dialog.findChild(
            ParameterPickerWidget
        )
        selected_param = model_param_widget.combo_box.all_items[-1]
        model_param_widget.combo_box.setCurrentText(selected_param)

        # save and close child dialog
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        assert param_line_edit_widget.get_value() == selected_param
        assert len(param_line_edit_widget.line_edit.actions()) == 1

        # save the entire form again
        self.save_main_form(
            qtbot,
            model_config,
            page,
            {
                "predicate": "LT",
                "type": "storagethreshold",
                "storage_node": "Reservoir",
                "values": [0.0, 0.0],
                "threshold": selected_param,
            },
        )

    def test_add_new_monthly_profile_parameter(self, qtbot, model_config):
        """
        Tests when a new monthly profile parameter is added in the widget. The test
        creates a new child parameter in the dialog window.
        """
        # add a new storage threshold parameter
        (
            param_line_edit_widget,
            child_dialog,
            main_dialog,
            page,
        ) = self.add_parameter_with_checks(qtbot, model_config)

        # 1. Fill in the form
        # select type
        # noinspection PyTypeChecker
        type_selector_widget: ParameterTypeSelectorWidget = child_dialog.findChild(
            ParameterTypeSelectorWidget
        )
        type_selector_widget.combo_box.setCurrentText("Monthly profile parameter")

        # select source
        # noinspection PyTypeChecker
        source_selector: SourceSelectorWidget = child_dialog.findChild(
            SourceSelectorWidget
        )
        source_selector.combo_box.setCurrentText(source_selector.labels["value"])
        # noinspection PyTypeChecker
        values_widget: MonthlyValuesWidget = child_dialog.findChild(MonthlyValuesWidget)
        # manually update the model
        new_values = list(range(1, 24, 2))
        values_widget.model.values = new_values
        qtbot.wait(100)

        # 2. Save and close the form and then check the ParameterLineEditWidget
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # constant parameter is converted from dictionary to float
        threshold_dict = {
            "type": "monthlyprofile",
            "values": new_values,
        }
        assert param_line_edit_widget.get_value() == threshold_dict

        # 3. Save the entire form
        self.save_main_form(
            qtbot,
            model_config,
            page,
            {
                "predicate": "LT",
                "type": "storagethreshold",
                "storage_node": "Reservoir",
                "values": [0.0, 0.0],
                "threshold": threshold_dict,
            },
        )

    # noinspection PyTypeChecker
    def test_add_new_anonymous_parameter_table(self, qtbot, model_config):
        """
        Tests when a new constant anonymous parameter from a model table is added in
        the widget. The test creates a new child parameter in the dialog window.
        """
        # add a new storage threshold parameter
        (
            param_line_edit_widget,
            child_dialog,
            main_dialog,
            page,
        ) = self.add_parameter_with_checks(qtbot, model_config)

        selected_table = "tableA"
        selected_index = 1
        selected_column = "Column 1"

        # 1. Fill in the form
        # select type
        source_selector_widget: SourceSelectorWidget = child_dialog.findChild(
            SourceSelectorWidget
        )
        source_selector_widget.combo_box.setCurrentText(
            source_selector_widget.labels["table"]
        )

        # select the table
        table_widget: TableSelectorWidget = child_dialog.findChild(TableSelectorWidget)
        assert table_widget.isHidden() is False
        table_widget.combo_box.setCurrentText(selected_table)

        # set the colum
        column_widget: ColumnWidget = child_dialog.findChild(ColumnWidget)
        column_widget.combo_box.setCurrentText(selected_column)

        # set the index value
        index_widget: IndexWidget = child_dialog.findChild(IndexWidget)
        index_combo_box: ComboBox = index_widget.findChild(ComboBox)
        index_combo_box.setCurrentText(str(selected_index))

        # 2. Save the form in the child dialog
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # 3. Check the ParameterLineEditWidget
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # constant parameter is converted from dictionary to float
        threshold_dict = {
            "type": "constant",
            "table": selected_table,
            "index": selected_index,
            "column": selected_column,
        }
        assert param_line_edit_widget.get_value() == threshold_dict

        # 4. Save the entire form
        self.save_main_form(
            qtbot,
            model_config,
            page,
            {
                "predicate": "LT",
                "type": "storagethreshold",
                "storage_node": "Reservoir",
                "values": [0.0, 0.0],
                "threshold": threshold_dict,
            },
        )

    # noinspection PyTypeChecker
    def test_add_new_anonymous_parameter_url(self, qtbot, model_config):
        """
        Tests when a new constant anonymous parameter from a URL is added in the
        widget. The test creates a new child parameter in the dialog window.
        """
        # add a new storage threshold parameter
        (
            param_line_edit_widget,
            child_dialog,
            main_dialog,
            page,
        ) = self.add_parameter_with_checks(qtbot, model_config)

        url = "files/table.csv"
        selected_index_cols = ["Column 1", "Demand centre"]
        selected_index = [1, 2]
        selected_column = "Column 3"

        # 1. Fill in the form
        # select type
        source_selector_widget: SourceSelectorWidget = child_dialog.findChild(
            SourceSelectorWidget
        )
        source_selector_widget.combo_box.setCurrentText(
            source_selector_widget.labels["anonymous_table"]
        )

        # select the table
        url_widget: UrlWidget = child_dialog.findChild(UrlWidget)
        assert url_widget.isHidden() is False
        url_widget.line_edit.setText(url)

        # set the colum
        column_widget: ColumnWidget = child_dialog.findChild(ColumnWidget)
        column_widget.combo_box.setCurrentText(selected_column)

        # set the index columns
        index_col_widget: IndexColWidget = child_dialog.findChild(IndexColWidget)
        selected_indexes = [
            index_col_widget.combo_box.all_items.index(col_name)
            for col_name in selected_index_cols
        ]
        index_col_widget.combo_box.check_items(selected_indexes)

        # set the index value
        index_widget: IndexWidget = child_dialog.findChild(IndexWidget)
        index_combo_boxes: list[ComboBox] = index_widget.findChildren(ComboBox)
        for ii, index_combo_box in enumerate(index_combo_boxes):
            index_combo_box.setCurrentText(str(selected_index[ii]))

        # 2. Save the form in the child dialog
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # 3. Check the ParameterLineEditWidget
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # constant parameter is converted from dictionary to float
        threshold_dict = {
            "type": "constant",
            "url": url,
            "index_col": selected_index_cols,
            "index": selected_index,
            "column": selected_column,
        }
        assert param_line_edit_widget.get_value() == threshold_dict

        # 4. Save the entire form
        self.save_main_form(
            qtbot,
            model_config,
            page,
            {
                "predicate": "LT",
                "type": "storagethreshold",
                "storage_node": "Reservoir",
                "values": [0.0, 0.0],
                "threshold": threshold_dict,
            },
        )

    @pytest.mark.parametrize(
        "param_dict, valid",
        [
            ({"type": "AggregatedIndexParameter"}, True),
            ({"type": "ConstantParameter"}, False),
        ],
    )
    def test_include_param_key(self, qtbot, param_dict, valid):
        """
        Tests the widget when the include_param_key is provided.
        """
        parent_widget = QWidget()
        form = ParameterForm(
            model_config=ModelConfig(),
            parameter_obj=ParameterConfig({}),
            fields={
                "Section": [
                    {
                        "name": "value",
                        "field_type": ParameterLineEditWidget,
                        "value": param_dict,
                        "field_args": {
                            "include_param_key": PywrParametersData().keys_with_parent_class(  # noqa: E501
                                "IndexParameter"
                            ),
                        },
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=parent_widget,
        )
        form.enable_optimisation_section = False
        form.load_fields()

        form_field = form.find_field("value")
        # noinspection PyTypeChecker
        widget: ParameterLineEditWidget = form_field.widget

        if valid:
            assert form_field.message.text() == ""
        else:
            assert "is not allowed" in form_field.message.text()

        # check selected parameter. Default to Aggregated index if not valid
        qtbot.mouseClick(widget.select_button, Qt.MouseButton.LeftButton)
        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = parent_widget.findChild(
            ModelComponentPickerDialog
        )
        # noinspection PyTypeChecker
        type_widget: ParameterTypeSelectorWidget = child_dialog.findChild(
            ParameterTypeSelectorWidget
        )
        assert type_widget.combo_box.currentText() == "Aggregated index parameter"
