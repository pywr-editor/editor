import pytest
from PySide6.QtCore import (
    Qt,
    QRegularExpression,
    QItemSelectionModel,
)
from PySide6.QtWidgets import QLineEdit, QPushButton, QGroupBox
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs.parameters.parameter_page_widget import (
    ParameterPageWidget,
)
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    CustomComponentExternalDataToggle,
    DictionaryItemDialogWidget,
    DataTypeDictionaryItemWidget,
    DictionaryItemFormWidget,
    DictionaryWidget,
    ModelComponentForm,
    FormField,
)
from tests.utils import resolve_model_path


class TestDialogParameterCustomParameterSection:
    """
    Tests the section for CustomParameterSection and all used widgets.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_custom_parameter_section.json"
    )

    data_type_map = {
        "value_number": "Number",
        "value_bool": "Boolean",
        "value_lst_str": "Not supported",
        "value_1d_array": "1D array",
        "value_dict": "Dictionary",
        "value_2d_array": "2D array",
        "value_3d_array": "3D array",
        "value_parameter": "Parameter",
        "value_node": "Node",
        "value_recorder": "Recorder",
        "value_scenario": "Scenario",
        "value_table": "Table",
        "value_string": "String",
    }
    expected_value_map = {
        "value_number": 300,
        "value_bool": True,
        "value_string": "Comment",
        "value_lst_str": [
            "ciao",
            "how",
            "understand",
            "ScenarioMonthlyProfile",
            "constantscenarioindex",
        ],
        "value_1d_array": {
            "Values": [
                1,
                54,
                29,
                12.5,
                45,
                12.5,
                45,
                12.5,
                12.5,
                45,
                99,
                12,
                12,
            ]
        },
        "value_dict": {
            "type": "ScenarioMonthlyProfile",
            "scenario": "scenario B",
            "values": [
                [12.5, 45, 12.5, 45, 12.5, 45, 12.5, 12.5, 45, 99, 12, 12]
            ],
        },
        "value_2d_array": {
            "Dimension 1": [
                12.5,
                45,
                12.5,
                45,
                12.5,
                45,
                12.5,
                12.5,
                45,
                99,
                12,
                12,
            ],
            "Dimension 2": [
                10,
                20,
                30,
                40,
                50,
                60,
                70,
                80,
                90,
                100,
                110,
                120,
            ],
        },
        "value_3d_array": {
            "Dimension 1": [
                12.5,
                45,
                12.5,
                45,
                12.5,
                45,
                12.5,
                12.5,
                45,
                99,
                12,
                12,
            ],
            "Dimension 2": [
                10,
                20,
                30,
                40,
                50,
                60,
                70,
                80,
                90,
                100,
                110,
                120,
            ],
            "Dimension 3": [
                100,
                200,
                300,
                400,
                500,
                600,
                700,
                800,
                900,
                1000,
                1100,
                1200,
            ],
        },
        "value_parameter": "monthly_param",
        "value_node": "Link",
        "value_recorder": "monthly_scenario_recorder",
        "value_scenario": "scenario A",
        "value_table": "Table 3",
    }

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_init(self, qtbot, model_config):
        """
        Tests the DictionaryWidget and opens the dialog to check the nested form
        widgets.
        """
        param_name = "custom_parameter"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        table_widget: DictionaryWidget = selected_page.findChild(
            DictionaryWidget
        )

        # 1. Check model implementation
        model = table_widget.model

        for ki, key in enumerate(model.dictionary.keys()):
            assert model.data(model.index(ki, 0), Qt.DisplayRole) == key
            assert (
                model.data(model.index(ki, 1), Qt.DisplayRole)
                == self.data_type_map[key]
            )

        # 2. Check external data fields that are hidden
        # noinspection PyTypeChecker
        toggle_widget: CustomComponentExternalDataToggle = (
            selected_page.findChild(CustomComponentExternalDataToggle)
        )
        assert toggle_widget.toggle.isChecked() is False

        for field_name in ["url", "table"]:
            # noinspection PyTypeChecker
            external_data_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            # NOTE: Qt returns field as visible when parent is not. Check parent
            # visibility as workaround
            assert external_data_field.parent().isHidden() is True

        # 3. Check DictionaryItemFormWidget and DataTypeDictionaryItemWidget
        # in child dialog
        edit_button = table_widget.edit_button
        for ki, key in enumerate(model.dictionary.keys()):
            # select item and open the dialog
            table_widget.table.setCurrentIndex(model.index(ki, 0))
            assert edit_button.isEnabled() is True

            qtbot.mouseClick(edit_button, Qt.MouseButton.LeftButton)

            # noinspection PyTypeChecker
            sub_dialog: DictionaryItemDialogWidget = selected_page.findChildren(
                DictionaryItemDialogWidget
            )[-1]
            # noinspection PyTypeChecker
            data_type_widget: DataTypeDictionaryItemWidget = (
                sub_dialog.findChild(DataTypeDictionaryItemWidget)
            )
            key_field = sub_dialog.form.find_field_by_name("key")

            # infer data type from parameter name
            data_type = key.replace("value_", "")
            value_field = sub_dialog.form.find_field_by_name(
                f"field_{data_type}"
            )

            # check key
            assert key_field.value() == key

            # check value
            if key == "value_lst_str":
                assert data_type_widget.combo_box.currentText() == "Number"
                assert (
                    "not supported"
                    in data_type_widget.form_field.message.text()
                )
                assert value_field is None
                # default field is selected
                # noinspection PyUnresolvedReferences
                assert (
                    sub_dialog.findChild(FormField, "field_number").isVisible()
                    is True
                )
                continue
            else:
                assert (
                    data_type_widget.combo_box.currentText()
                    == self.data_type_map[key]
                )
                assert data_type_widget.form_field.message.text() == ""

                # field exists
                assert value_field is not None

            # check field visibility. Only one field is visible
            for field in sub_dialog.findChildren(
                FormField, QRegularExpression("field_")
            ):
                if field.name != value_field.name:
                    assert field.isVisible() is False
                    # hidden fields return an empty value
                    assert not field.value() is True
                else:
                    assert value_field.isVisible() is True
                    # check value of widget
                    assert value_field.value() == self.expected_value_map[key]

            # close and remove selection to restore QTableView
            sub_dialog.close()
            sub_dialog.deleteLater()

            table_widget.table.clearSelection()
            assert edit_button.isEnabled() is False

        # 4. Validate form to test section filter
        # validation must return original parameter dict
        param_dict = model_config.parameters.get_config_from_name(
            param_name, as_dict=True
        )
        assert table_widget.form.validate() == {
            **{"name": param_name},
            **param_dict,
        }

        # 5. Reset widget
        table_widget.reset()
        assert table_widget.get_value() == {}

    def test_delete(self, qtbot, model_config):
        """
        Tests that a dictionary item is deleted from DictionaryWidget.
        """
        param_name = "custom_parameter"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        table_widget: DictionaryWidget = selected_page.findChild(
            DictionaryWidget
        )

        model = table_widget.model
        delete_button = table_widget.delete_button
        assert delete_button.isEnabled() is False

        # select item
        key_to_delete = "value_string"
        dict_item_index = model.index(2, 0)
        assert model.data(dict_item_index, Qt.DisplayRole) == key_to_delete
        table_widget.table.selectionModel().select(
            dict_item_index, QItemSelectionModel.Select
        )
        assert delete_button.isEnabled() is True

        qtbot.mouseClick(delete_button, Qt.MouseButton.LeftButton)

        assert key_to_delete not in model.dictionary

        # check final dictionary
        param_dict = model_config.parameters.get_config_from_name(
            param_name, as_dict=True
        )
        del param_dict[key_to_delete]
        assert table_widget.form.validate() == {
            **{"name": param_name},
            **param_dict,
        }

    def test_change_key(self, qtbot, model_config):
        """
        Tests when a dictionary key is renamed. This also tests when the user tries
        to set the "url" or "table" keys, which must be configured in the main form.
        """
        param_name = "custom_parameter"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        table_widget: DictionaryWidget = selected_page.findChild(
            DictionaryWidget
        )

        # 1. Select an item
        model = table_widget.model
        key_to_rename = "value_parameter"
        dict_item_index = model.index(8, 0)
        assert model.data(dict_item_index, Qt.DisplayRole) == key_to_rename
        table_widget.table.selectionModel().select(
            dict_item_index, QItemSelectionModel.Select
        )

        # 2. Open the dialog
        edit_button = table_widget.edit_button
        assert edit_button.isVisible() is True
        qtbot.mouseClick(edit_button, Qt.MouseButton.LeftButton)

        # noinspection PyTypeChecker
        child_dialog: DictionaryItemDialogWidget = selected_page.findChild(
            DictionaryItemDialogWidget
        )
        key_field = child_dialog.form.find_field_by_name("key")
        line_edit: QLineEdit = key_field.findChild(QLineEdit)

        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )
        assert save_button.text() == "Save"

        # 3. Set a forbidden key and submit form
        line_edit.setText("url")
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert (
            "configure external data using the 'url'"
            in key_field.message.text()
        )

        # 4. Set a valid key and send the child form again
        new_key_name = "My new key"
        line_edit.setText(new_key_name)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # 5. Validate main form
        param_dict = model_config.parameters.get_config_from_name(
            param_name, as_dict=True
        )
        param_dict = {
            **{"name": param_name},
            **param_dict,
        }
        param_dict[new_key_name] = param_dict[key_to_rename]
        del param_dict[key_to_rename]

        assert table_widget.form.validate() == param_dict

    def test_edit_dict_item_data_type(self, qtbot, model_config):
        """
        Tests when a dictionary item is changed
        """
        param_name = "custom_parameter"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        table_widget: DictionaryWidget = selected_page.findChild(
            DictionaryWidget
        )

        # 1. Select an item
        model = table_widget.model
        selected_key = "value_1d_array"
        dict_item_index = model.index(4, 0)
        assert model.data(dict_item_index, Qt.DisplayRole) == selected_key
        table_widget.table.selectionModel().select(
            dict_item_index, QItemSelectionModel.Select
        )

        # 2. Open the dialog
        edit_button = table_widget.edit_button
        assert edit_button.isVisible() is True
        qtbot.mouseClick(edit_button, Qt.MouseButton.LeftButton)

        # noinspection PyTypeChecker
        child_dialog: DictionaryItemDialogWidget = selected_page.findChild(
            DictionaryItemDialogWidget
        )

        # 3. Change data type and save form
        # data type
        # noinspection PyTypeChecker
        data_type_widget: DataTypeDictionaryItemWidget = child_dialog.findChild(
            DataTypeDictionaryItemWidget
        )
        data_type_widget.combo_box.setCurrentText(
            data_type_widget.labels_map["string"]
        )
        # dictionary item value
        string_field = child_dialog.form.find_field_by_name("field_string")
        line_edit: QLineEdit = string_field.findChild(QLineEdit)
        new_value = "The value was changed"
        line_edit.setText(new_value)

        # 3. Send the child form
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )
        assert save_button.text() == "Save"
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # 4. Validate main form
        param_dict = model_config.parameters.get_config_from_name(
            param_name, as_dict=True
        )
        param_dict = {
            **{"name": param_name},
            **param_dict,
            selected_key: new_value,
        }
        assert table_widget.form.validate() == param_dict

    def test_add_new_dict_item(self, qtbot, model_config):
        """
        Tests when a new dictionary item is added
        """
        param_name = "custom_parameter"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        table_widget: DictionaryWidget = selected_page.findChild(
            DictionaryWidget
        )

        # 1. Open the dialog
        qtbot.mouseClick(table_widget.add_button, Qt.MouseButton.LeftButton)

        # noinspection PyTypeChecker
        child_dialog: DictionaryItemDialogWidget = selected_page.findChild(
            DictionaryItemDialogWidget
        )

        # 2. Set the number
        # key
        string_field = child_dialog.form.find_field_by_name("key")
        line_edit: QLineEdit = string_field.findChild(QLineEdit)
        new_key = "A new number"
        line_edit.setText(new_key)

        # dictionary item value
        string_field = child_dialog.form.find_field_by_name("field_number")
        # field is visible with no error
        assert string_field.message.text() == ""
        assert string_field.isVisible() is True

        line_edit: QLineEdit = string_field.findChild(QLineEdit)
        new_value = 0.4421
        line_edit.setText(str(new_value))

        # 3. Send the child form
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )
        assert save_button.text() == "Save"
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # 4. Validate main form
        param_dict = model_config.parameters.get_config_from_name(
            param_name, as_dict=True
        )
        param_dict = {
            **{"name": param_name},
            **param_dict,
            new_key: new_value,
        }
        assert table_widget.form.validate() == param_dict

    @pytest.mark.parametrize(
        "selected_key, model_index",
        [
            ("value_1d_array", 4),
            ("value_2d_array", 6),
            ("value_3d_array", 7),
        ],
    )
    def test_edit_array(self, qtbot, model_config, selected_key, model_index):
        """
        Tests array value conversion from dictionary to list. The value from
        TableValuesWidget is a dictionary.
        """
        param_name = "custom_parameter"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        table_widget: DictionaryWidget = selected_page.findChild(
            DictionaryWidget
        )

        # 1. Select an item
        model = table_widget.model
        dict_item_index = model.index(model_index, 0)
        assert model.data(dict_item_index, Qt.DisplayRole) == selected_key
        table_widget.table.selectionModel().select(
            dict_item_index, QItemSelectionModel.Select
        )

        # 2. Open the dialog
        edit_button = table_widget.edit_button
        assert edit_button.isVisible() is True
        qtbot.mouseClick(edit_button, Qt.MouseButton.LeftButton)

        # noinspection PyTypeChecker
        child_dialog: DictionaryItemDialogWidget = selected_page.findChild(
            DictionaryItemDialogWidget
        )

        # 3. Send the child form
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )
        assert save_button.text() == "Save"
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # 4. Validate main form
        param_dict = model_config.parameters.get_config_from_name(
            param_name, as_dict=True
        )
        param_dict = {
            **{"name": param_name},
            **param_dict,
        }
        assert table_widget.form.validate() == param_dict

    def test_add_new_nested_dict(self, qtbot, model_config):
        """
        Tests when a new dictionary is added as item.
        """
        param_name = "custom_parameter"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        table_widget: DictionaryWidget = selected_page.findChild(
            DictionaryWidget
        )

        # 1. Open the dialog
        qtbot.mouseClick(table_widget.add_button, Qt.MouseButton.LeftButton)
        # noinspection PyTypeChecker
        child_dialog: DictionaryItemDialogWidget = selected_page.findChild(
            DictionaryItemDialogWidget
        )

        # 2. Set the key and data type to dictionary
        key_field = child_dialog.form.find_field_by_name("key")
        line_edit: QLineEdit = key_field.findChild(QLineEdit)
        new_key = "A new dictionary"
        line_edit.setText(new_key)

        # noinspection PyTypeChecker
        data_type_widget: DataTypeDictionaryItemWidget = child_dialog.findChild(
            DataTypeDictionaryItemWidget
        )
        data_type_widget.combo_box.setCurrentText(
            data_type_widget.labels_map["dict"]
        )

        # 2. Add nest dictionary item
        # noinspection PyTypeChecker
        child_dictionary_widget: DictionaryWidget = child_dialog.findChild(
            DictionaryWidget
        )
        # add key and number
        qtbot.mouseClick(
            child_dictionary_widget.add_button, Qt.MouseButton.LeftButton
        )

        # noinspection PyTypeChecker
        child_child_dialog: DictionaryItemDialogWidget = child_dialog.findChild(
            DictionaryItemDialogWidget
        )
        # noinspection PyTypeChecker
        child_child_form: DictionaryItemFormWidget = (
            child_child_dialog.findChild(DictionaryItemFormWidget)
        )
        key_field = child_child_form.find_field_by_name("key")
        # noinspection PyTypeChecker
        line_edit: QLineEdit = key_field.findChild(QLineEdit)
        new_sub_key = "A new number"
        line_edit.setText(new_sub_key)

        string_field = child_child_dialog.form.find_field_by_name(
            "field_number"
        )
        line_edit: QLineEdit = string_field.findChild(QLineEdit)
        new_sub_value = 0.4421
        line_edit.setText(str(new_sub_value))

        # 3. Save and close the two dialogs
        # noinspection PyTypeChecker
        save_button: QPushButton = child_child_dialog.findChild(
            QPushButton, "save_button"
        )
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_child_dialog.close()

        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # 4. Validate main form
        param_dict = model_config.parameters.get_config_from_name(
            param_name, as_dict=True
        )
        param_dict = {
            **{"name": param_name},
            **param_dict,
            new_key: {new_sub_key: new_sub_value},
        }
        assert table_widget.form.validate() == param_dict

    @pytest.mark.parametrize(
        "param_name, toggle_checked",
        [("custom_parameter", False), ("custom_param_with_table", True)],
    )
    def test_external_data_toggle(
        self, qtbot, model_config, param_name, toggle_checked
    ):
        """
        Tests visibility of external data sections when toggle status is changed and
        that the field values are correctly saved.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        toggle_widget: CustomComponentExternalDataToggle = (
            selected_page.findChild(CustomComponentExternalDataToggle)
        )

        def check_visibility(visible):
            group_boxes: list[QGroupBox] = selected_page.findChildren(QGroupBox)
            assert (not group_boxes) is False
            for group_box in selected_page.findChildren(QGroupBox):
                if group_box.objectName() in [
                    "External data",
                    ModelComponentForm.table_config_group_name,
                ]:
                    assert group_box.isVisible() == visible

        # switch it on for test
        if toggle_checked is False:
            check_visibility(False)
            toggle_widget.toggle.setChecked(True)
            check_visibility(True)
        # check external data fields
        else:
            check_visibility(True)
            assert (
                selected_page.form.find_field_by_name("table").value()
                == "Table 3"
            )
            assert (
                selected_page.form.find_field_by_name("column").value()
                == "Column 3"
            )
