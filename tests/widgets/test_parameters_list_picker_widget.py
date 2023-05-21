import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    FormField,
    IndexParametersListPickerWidget,
    ModelComponentPickerDialog,
    ModelComponentSourceSelectorWidget,
    ModelParameterPickerWidget,
    ParameterForm,
    ParameterLineEditWidget,
    ParameterPickerWidget,
    ParametersListPickerWidget,
    ParameterTypeSelectorWidget,
    StoragePickerWidget,
    ValueWidget,
)
from pywr_editor.model import ModelConfig, ParameterConfig
from tests.utils import resolve_model_path


class TestDialogParameterParametersListPickerWidget:
    """
    Tests the AbstractModelComponentsListPickerWidget, ParametersListPickerWidget,
    IndexParametersListPickerWidget and any related widgets.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_parameters_list_picker_widget.json"
    )
    general_anonymous_param_name = "param"
    general_anonymous_param_value = [
        {"type": "constant", "value": 345.6},
        {"type": "weeklyprofile", "values": [1, 2, 3, 4, 5, 6, 7]},
        {"type": "constant", "value": 91.23},
        {
            "type": "monthlyprofile",
            "values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        },
    ]

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, field_name, value",
        [
            (
                "valid_dicts",
                "thresholds",
                [
                    {"type": "constant", "value": 345.6},
                    {"type": "weeklyprofile", "values": [1, 2, 3, 4, 5, 6, 7]},
                ],
            ),
            # constant is declared as float instead of dict
            (
                "valid_with_float",
                "thresholds",
                [
                    {"type": "constant", "value": 345.6},
                    {"type": "weeklyprofile", "values": [1, 2, 3, 4, 5, 6, 7]},
                ],
            ),
            # only floats provided
            (
                "valid_with_only_floats",
                "thresholds",
                [
                    {"type": "constant", "value": 345.6},
                    {"type": "constant", "value": 34},
                ],
            ),
            # list with an existing model parameter
            (
                "valid_with_str",
                "thresholds",
                [
                    {"type": "constant", "value": 345.6},
                    "constant",
                    {"type": "weeklyprofile", "values": [1, 2, 3, 4, 5, 6, 7]},
                ],
            ),
            # thresholds key not provided
            ("valid_no_key", "thresholds", []),
            # thresholds key is an empty list
            ("valid_empty_list", "thresholds", []),
            # valid custom parameter - AggregatedIndexParameter wants an IndexParameter
            (
                "valid_with_custom_parameter",
                "parameters",
                [{"type": "my", "value": 5}],
            ),
            # valid - parameters are filtered by IndexParameter
            (
                "index_valid",
                "parameters",
                [
                    {
                        "type": "ControlCurveIndex",
                        "storage_node": "Reservoir1",
                        "control_curves": [],
                    },
                ],
            ),
            (
                "index_valid_with_model_param",
                "parameters",
                [
                    {
                        "type": "ControlCurveIndex",
                        "storage_node": "Reservoir1",
                        "control_curves": [],
                    },
                    "control_curve_index",
                ],
            ),
        ],
    )
    def test_valid_values(self, qtbot, model_config, param_name, field_name, value):
        """
        Tests that the values are loaded correctly for ParametersListPickerWidget and
        IndexParametersListPickerWidget.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        field: FormField = selected_page.findChild(FormField, field_name)
        # noinspection PyTypeChecker
        widget: ParametersListPickerWidget | IndexParametersListPickerWidget = (
            field.widget
        )

        # check model
        assert widget.model.values == value

        # check table view name
        for di, param_value in enumerate(value):
            idx = widget.model.index(di, 0)
            if isinstance(param_value, dict):
                param_obj = ParameterConfig(param_value)
                assert (
                    widget.model.data(idx, Qt.DisplayRole) == param_obj.humanised_type
                )
            elif isinstance(param_value, str):
                param_obj = model_config.parameters.config(param_value, as_dict=False)
                assert (
                    widget.model.data(idx, Qt.DisplayRole)
                    == f"{param_obj.name} ({param_obj.humanised_type})"
                )
            else:
                raise TypeError("Invalid type")

        # check warning and validation
        assert field.message.text() == ""

        output = widget.validate("", "", widget.get_value())
        if not value:
            assert output.validation is False
        else:
            assert output.validation is True

        # check value
        assert widget.get_value() == value

        # reset
        widget.reset()
        assert widget.get_value() == []

    @pytest.mark.parametrize(
        "param_name, field_name, init_message, validation_message, value",
        [
            (
                "invalid_type",
                "thresholds",
                "is not valid",
                "cannot be empty",
                [],
            ),
            (
                "invalid_type_in_list",
                "thresholds",
                "can contain only numbers or valid parameter configurations",
                "cannot be empty",
                [],
            ),
            (
                "invalid_wrong_param_dict",
                "thresholds",
                "must contain valid parameter configurations",
                "cannot be empty",
                [],
            ),
            # empty message but validation fails
            (
                "invalid_non_existing_param_name",
                "thresholds",
                "model parameters do not exist",
                "",
                [
                    {"type": "constant", "value": 345.6},
                    {"type": "constant", "value": 34},
                ],
            ),
            # picker with filter - validation passes
            (
                "index_invalid_type",
                "parameters",
                "is not valid and these were",
                "",
                [
                    {
                        "type": "ControlCurveIndex",
                        "storage_node": "Reservoir1",
                        "control_curves": [],
                    }
                ],
            ),
            (
                "index_all_invalid",
                "parameters",
                "is not valid and these were",
                "cannot be empty",
                [],
            ),
            (
                "index_invalid_model_param_type",
                "parameters",
                "is not valid and these were",
                "",
                [
                    {
                        "type": "ControlCurveIndex",
                        "storage_node": "Reservoir1",
                        "control_curves": [],
                    },
                ],
            ),
            (
                "index_invalid_non_existing_model_param",
                "parameters",
                "is not valid and these were",
                "",
                [
                    {
                        "type": "ControlCurveIndex",
                        "storage_node": "Reservoir1",
                        "control_curves": [],
                    },
                ],
            ),
            # invalid custom parameter - AggregatedIndexParameter wants an
            # IndexParameter but Parameter was given
            (
                "invalid_with_wrong_custom_parameter_type",
                "parameters",
                "one or more parameters is not valid",
                "cannot be empty",
                [],
            ),
            # custom parameter is not imported and type flagged as not valid
            (
                "invalid_with_non_imported_custom_parameter",
                "parameters",
                "one or more parameters is not valid",
                "cannot be empty",
                [],
            ),
        ],
    )
    def test_invalid_values(
        self,
        qtbot,
        model_config,
        param_name,
        field_name,
        init_message,
        validation_message,
        value,
    ):
        """
        Tests that the warning message is shown when the values are not valid for
        ParametersListPickerWidget and IndexParametersListPickerWidget.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        field: FormField = selected_page.findChild(FormField, field_name)
        # noinspection PyTypeChecker
        widget: ParametersListPickerWidget | IndexParametersListPickerWidget = (
            field.widget
        )

        # check warning and validation
        assert init_message in field.message.text()

        # check model and widget value
        assert widget.model.values == value
        assert widget.get_value() == value

        output = widget.validate("", "", widget.get_value())
        if validation_message != "":
            assert output.validation is False
            assert validation_message in output.error_message
        else:
            assert output.validation is True

    @staticmethod
    def select_row(widget: ParametersListPickerWidget, row_id: int) -> None:
        """
        Selects a row in the ListView.
        :param widget: The widget instance.
        :param row_id: The row number ot select.
        :return: None
        """
        widget.list.clearSelection()
        row = widget.model.index(row_id, 0)
        widget.list.selectionModel().select(row, QItemSelectionModel.Select)

    def test_sorting(self, qtbot, model_config):
        """
        Tests parameter sorting (when a parameter is moved up or down and the button
        status)
        """
        dialog = ParametersDialog(model_config, self.general_anonymous_param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value()
            == self.general_anonymous_param_name
        )

        # noinspection PyTypeChecker
        thresholds_field: FormField = selected_page.findChild(FormField, "thresholds")
        # noinspection PyTypeChecker
        thresholds_widget: ParametersListPickerWidget = thresholds_field.widget
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")

        # 1. Sorting buttons are disabled
        assert thresholds_widget.list.selectionModel().selection().count() == 0
        assert thresholds_widget.move_up.isEnabled() is False
        assert thresholds_widget.move_down.isEnabled() is False
        assert save_button.isEnabled() is False

        # 2. Select first parameter. Button up is still disabled
        self.select_row(thresholds_widget, 0)
        assert thresholds_widget.move_up.isEnabled() is False
        assert thresholds_widget.move_down.isEnabled() is True

        # 3. Select last parameter. Button down is still disabled
        self.select_row(thresholds_widget, 3)
        assert thresholds_widget.move_up.isEnabled() is True
        assert thresholds_widget.move_down.isEnabled() is False

        # 4. Move one item up and check value
        self.select_row(thresholds_widget, 2)
        qtbot.mouseClick(thresholds_widget.move_up, Qt.MouseButton.LeftButton)
        new_value = [
            self.general_anonymous_param_value[0],
            self.general_anonymous_param_value[2],
            self.general_anonymous_param_value[1],
            self.general_anonymous_param_value[3],
        ]
        assert thresholds_widget.get_value() == new_value

        # the form save button is enabled
        assert save_button.isEnabled() is True

        # 5. Move one item down and check value
        self.select_row(thresholds_widget, 0)
        qtbot.mouseClick(thresholds_widget.move_down, Qt.MouseButton.LeftButton)
        new_value = [
            self.general_anonymous_param_value[2],
            self.general_anonymous_param_value[0],
            self.general_anonymous_param_value[1],
            self.general_anonymous_param_value[3],
        ]
        assert thresholds_widget.get_value() == new_value

        # 6. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.config(self.general_anonymous_param_name) == {
            "type": "multiplethresholdindex",
            "node": "Reservoir2",
            "thresholds": new_value,
        }

    def test_delete(self, qtbot, model_config):
        """
        Tests parameter deletion
        """
        dialog = ParametersDialog(model_config, self.general_anonymous_param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value()
            == self.general_anonymous_param_name
        )

        # noinspection PyTypeChecker
        thresholds_field: FormField = selected_page.findChild(FormField, "thresholds")
        # noinspection PyTypeChecker
        thresholds_widget: ParametersListPickerWidget = thresholds_field.widget
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")

        # 1. delete button is disabled
        assert thresholds_widget.list.selectionModel().selection().count() == 0
        assert thresholds_widget.delete_button.isEnabled() is False
        assert save_button.isEnabled() is False

        # 2. Delete second parameter. Button up is still disabled
        self.select_row(thresholds_widget, 1)
        assert thresholds_widget.delete_button.isEnabled() is True
        qtbot.mouseClick(thresholds_widget.delete_button, Qt.MouseButton.LeftButton)
        new_value = [
            self.general_anonymous_param_value[0],
            self.general_anonymous_param_value[2],
            self.general_anonymous_param_value[3],
        ]
        assert thresholds_widget.get_value() == new_value

        # 3. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.config(self.general_anonymous_param_name) == {
            "type": "multiplethresholdindex",
            "node": "Reservoir2",
            "thresholds": new_value,
        }

    @pytest.mark.parametrize(
        "mode",
        ["add", "edit"],
    )
    def test_add_edit_child_anonymous_parameter(self, qtbot, model_config, mode):
        """
        Tests when a constant parameter is added or edited in the parameter list of a
        MultipleThresholdIndexParameter. All the parameters are anonymous.
        """
        dialog = ParametersDialog(model_config, self.general_anonymous_param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value()
            == self.general_anonymous_param_name
        )

        # noinspection PyTypeChecker
        thresholds_field: FormField = selected_page.findChild(FormField, "thresholds")
        # noinspection PyTypeChecker
        thresholds_widget: ParametersListPickerWidget = thresholds_field.widget

        # 1. Open the dialog
        index = None
        if mode == "edit":
            index = 2
            self.select_row(thresholds_widget, index)
            qtbot.mouseClick(thresholds_widget.edit_button, Qt.MouseButton.LeftButton)
        elif mode == "add":
            qtbot.mouseClick(thresholds_widget.add_button, Qt.MouseButton.LeftButton)
        else:
            raise ValueError("Mode not supported")

        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = selected_page.findChild(
            ModelComponentPickerDialog
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")

        # 2. Configure a new or already existing constant parameter and save the changes
        # noinspection PyTypeChecker
        type_widget: ParameterTypeSelectorWidget = child_dialog.findChild(
            ParameterTypeSelectorWidget
        )
        assert type_widget.get_value() == "constant"

        new_float = 129.78
        # noinspection PyTypeChecker
        value_widget: ValueWidget = child_dialog.findChild(ValueWidget)
        value_widget.line_edit.setText(str(new_float))
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        # manually close the dialog
        child_dialog.close()

        # 3. Check the threshold values
        new_value = self.general_anonymous_param_value.copy()
        if mode == "add":
            new_value.append({"type": "constant", "value": new_float})
        else:
            new_value[index]["value"] = new_float

        assert thresholds_widget.get_value() == new_value

        # 4. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.config(self.general_anonymous_param_name) == {
            "type": "multiplethresholdindex",
            "node": "Reservoir2",
            "thresholds": new_value,
        }

    @pytest.mark.parametrize(
        "mode",
        ["add", "edit"],
    )
    def test_add_edit_child_anonymous_parameter_with_filter(
        self, qtbot, model_config, mode
    ):
        """
        Tests when a new child parameter is added to the list of an anonymous
        AggregatedIndexParameter. The parameter only allows certain parameter types by
        setting a filter on ParametersListPickerWidget.
        """
        param_name = "agg_param"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        parameters_list_field: FormField = selected_page.findChild(
            FormField, "parameters"
        )
        # noinspection PyTypeChecker
        parameters_list_widget: ParametersListPickerWidget = (
            parameters_list_field.widget
        )

        # 1. Open the dialog
        if mode == "edit":
            index = 0
            self.select_row(parameters_list_widget, index)
            qtbot.mouseClick(
                parameters_list_widget.edit_button, Qt.MouseButton.LeftButton
            )
        elif mode == "add":
            qtbot.mouseClick(
                parameters_list_widget.add_button, Qt.MouseButton.LeftButton
            )
        else:
            raise ValueError("Mode not supported")

        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = selected_page.findChild(
            ModelComponentPickerDialog
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")

        # the first (default) parameter type is selected, change it
        if mode == "add":
            # noinspection PyTypeChecker
            type_widget: ParameterTypeSelectorWidget = child_dialog.findChild(
                ParameterTypeSelectorWidget
            )
            assert type_widget.combo_box.currentText() == "Aggregated index parameter"
            # change default type
            type_widget.combo_box.setCurrentText("Storage threshold parameter")

        # 2. Configure a new or already existing storage threshold parameter and save
        # the changes
        # noinspection PyTypeChecker
        storage_node: StoragePickerWidget = child_dialog.findChild(StoragePickerWidget)
        selected_index = storage_node.combo_box.findData("Reservoir2", Qt.UserRole)
        storage_node.combo_box.setCurrentIndex(selected_index)
        qtbot.wait(100)

        # noinspection PyTypeChecker
        param_line_edit: ParameterLineEditWidget = child_dialog.findChild(
            ParameterLineEditWidget
        )
        param_line_edit.component_obj = ParameterConfig(
            {"type": "constant", "value": 2663}
        )
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # manually close the dialog
        child_dialog.close()

        # 3. Check the parameter list
        existing_params_list = [
            {
                "threshold": 23,
                "type": "storagethreshold",
                "values": [1.432, 53.033],
            }
        ]

        # add new child parameter
        if mode == "add":
            existing_params_list.append(
                {
                    "type": "storagethreshold",
                    "threshold": param_line_edit.get_value(),
                    "predicate": "LT",
                    # new value
                    "storage_node": storage_node.get_value(),
                    "values": [0.0, 0.0],
                }
            )
            # first parameter is not changed
            existing_params_list[0]["type"] = "StorageThresholdParameter"
        # change existing values
        else:
            # predicate is added and set to default. In Pywr is optional
            existing_params_list[0]["predicate"] = "LT"
            existing_params_list[0]["threshold"] = param_line_edit.get_value()
            existing_params_list[0]["storage_node"] = storage_node.get_value()
        assert parameters_list_widget.get_value() == existing_params_list

        # 4. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.config(param_name) == {
            "type": "aggregatedindex",
            "agg_func": "sum",
            "parameters": existing_params_list,
        }

    def test_edit_child_model_parameter(self, qtbot, model_config):
        """
        Tests when a different model parameter is selected in the parameter list (using
        MultipleThresholdIndexParameter). All parameters are allowed.
        """
        param_name = "param_with_child_model_param"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        thresholds_field: FormField = selected_page.findChild(FormField, "thresholds")
        # noinspection PyTypeChecker
        thresholds_widget: ParametersListPickerWidget = thresholds_field.widget

        # 1. Open the dialog
        index = 0
        self.select_row(thresholds_widget, index)
        qtbot.mouseClick(thresholds_widget.edit_button, Qt.MouseButton.LeftButton)

        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = selected_page.findChild(
            ModelComponentPickerDialog
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")

        # 2. Change the parameter
        new_str = "param_threshold"
        # noinspection PyTypeChecker
        param_widget: ParameterPickerWidget = child_dialog.findChild(
            ParameterPickerWidget
        )
        # 27  + "None"
        assert len(param_widget.combo_box.all_items) == 28

        param_widget.combo_box.setCurrentText(new_str)
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        # manually close the dialog
        child_dialog.close()

        # 3. Check the threshold values
        new_value = [
            "control_curve_index",
            {
                "type": "monthlyprofile",
                "values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            },
        ]
        new_value[index] = new_str

        assert thresholds_widget.get_value() == new_value

        # 4. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.config(param_name) == {
            "type": "multiplethresholdindex",
            "node": "Reservoir2",
            "thresholds": new_value,
        }

    @pytest.mark.parametrize(
        "mode",
        ["add", "edit"],
    )
    def test_edit_child_model_parameter_with_filter(self, qtbot, model_config, mode):
        """
        Tests when a model parameter of type AggregatedIndexParameter is selected in
        the parameter list. The parameter only allows certain parameter types by
        setting a filter on ParametersListPickerWidget.
        """
        param_name = "agg_param_with_model_param"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        parameters_list_field: FormField = selected_page.findChild(
            FormField, "parameters"
        )
        # noinspection PyTypeChecker
        parameters_list_widget: ParametersListPickerWidget = (
            parameters_list_field.widget
        )

        # 1. Open the dialog
        if mode == "edit":
            index = 0
            self.select_row(parameters_list_widget, index)
            qtbot.mouseClick(
                parameters_list_widget.edit_button, Qt.MouseButton.LeftButton
            )
        elif mode == "add":
            qtbot.mouseClick(
                parameters_list_widget.add_button, Qt.MouseButton.LeftButton
            )
        else:
            raise ValueError("Mode not supported")

        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = selected_page.findChild(
            ModelComponentPickerDialog
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")

        # the picker dialog defaults to anonymous parameters, change source
        if mode == "add":
            # noinspection PyTypeChecker
            source_widget: ModelComponentSourceSelectorWidget = child_dialog.findChild(
                ModelComponentSourceSelectorWidget
            )
            # trigger Slot
            source_widget.combo_box.setCurrentText(
                source_widget.labels["model_component"]
            )

        # 2. Configure a new or already existing parameter (inheriting from
        # IndexParameter) and save the changes
        new_param_name = "control_curve_index"
        # noinspection PyTypeChecker
        model_param_widget: ModelParameterPickerWidget = child_dialog.findChild(
            ModelParameterPickerWidget
        )
        # 27 - 2 constant parameters + "None"
        assert len(model_param_widget.combo_box.all_items) == 26

        # change name
        assert new_param_name in model_param_widget.combo_box.all_items
        model_param_widget.combo_box.setCurrentText(new_param_name)
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        # manually close the dialog
        child_dialog.close()

        # 3. Check the parameter list
        existing_params_list = ["param_threshold"]

        # add new child parameter
        if mode == "add":
            existing_params_list.append(new_param_name)
        # change existing values
        else:
            existing_params_list = [new_param_name]

        assert parameters_list_widget.get_value() == existing_params_list

        # 4. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.config(param_name) == {
            "type": "aggregatedindex",
            "agg_func": "sum",
            "parameters": existing_params_list,
        }

    @pytest.mark.parametrize("is_mandatory", [True, False])
    def test_is_mandatory(self, qtbot, is_mandatory):
        """
        Tests the widget when it is optional
        """
        # mock widgets
        form = ParameterForm(
            model_config=ModelConfig(),
            parameter_obj=ParameterConfig({}),
            available_fields={
                "Section": [
                    {
                        "name": "parameters",
                        "field_type": ParametersListPickerWidget,
                        "field_args": {"is_mandatory": is_mandatory},
                        "value": [],
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()

        form_field = form.find_field_by_name("parameters")
        # noinspection PyTypeChecker
        widget: ParametersListPickerWidget = form_field.widget

        out = widget.validate("", "", widget.get_value())
        if is_mandatory:
            assert out.validation is False
        else:
            assert out.validation is True
