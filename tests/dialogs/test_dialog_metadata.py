import pytest
from PySide6.QtCore import QItemSelectionModel, QTimer
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QDialogButtonBox, QPushButton

from pywr_editor.dialogs import MetadataDialog
from pywr_editor.dialogs.metadata.metadata_custom_fields_widget import (
    MetadataCustomFieldsWidget,
)
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


# noinspection PyTypeChecker
class TestMetadataDialog:
    model_file = resolve_model_path("model_1.json")

    @pytest.fixture
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.fixture
    def dialog(self, model_config) -> MetadataDialog:
        """
        Initialises the dialog.
        :param model_config: The ModelConfig instance.
        :return: The MetadataDialog instance.
        """
        QTimer.singleShot(100, close_message_box)
        dialog = MetadataDialog(model_config)
        dialog.hide()
        return dialog

    def test_change_of_basic_info(self, qtbot, dialog, model_config):
        """
        Opens the dialog and tests that the basic model information is changed
        correctly.
        """
        new_values = {
            "description": "New description",
            "minimum_version": "0.99",
        }
        for field_name, new_value in new_values.items():
            # noinspection PyTypeChecker
            form_field: FormField = dialog.findChild(FormField, field_name)
            form_field.widget.setText(new_value)

        # save the form
        save_button: QPushButton = dialog.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        for field_name, new_value in new_values.items():
            # noinspection PyTypeChecker
            form_field: FormField = dialog.findChild(FormField, field_name)
            assert form_field.message.text() == ""
            assert model_config.metadata[field_name] == new_value

    def test_wrong_version_number(self, qtbot, dialog, model_config):
        """
        Tests the validation when an invalid minimum version number is provided.
        """
        form_field: FormField = dialog.findChild(FormField, "minimum_version")
        form_field.widget.setText("a")

        # try saving the form
        QTimer.singleShot(100, close_message_box)

        save_button: QPushButton = dialog.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert model_config.has_changes is False

    def test_add_new_custom_field(self, qtbot, dialog, model_config):
        """
        Opens the dialog and tests that a new custom field is added correctly to the
        model configuration.
        """
        custom_fields_field: FormField = dialog.findChild(
            FormField, "custom_fields"
        )
        custom_fields_widget: MetadataCustomFieldsWidget = (
            custom_fields_field.widget
        )
        add_button: QPushButton = dialog.findChild(QPushButton)
        save_button: QPushButton = dialog.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        assert add_button.text() == "Add"

        # 1. Add a new item
        qtbot.mouseClick(add_button, Qt.MouseButton.LeftButton)

        # 2. Check data in the class attribute/widget model
        model_new_field = custom_fields_widget.model.fields[-1]
        last_idx = len(custom_fields_widget.model.fields)
        expected_key = f"New field #{last_idx}"
        expected_value = "New value"
        assert model_new_field == [expected_key, expected_value]

        # 3. Save the form
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        assert custom_fields_field.message.text() == ""
        assert expected_key in model_config.metadata
        assert model_config.json["metadata"][expected_key] == expected_value
        assert model_config.has_changes is True

    def test_edit_custom_field_value(self, qtbot, dialog, model_config):
        """
        Opens the dialog and tests when an existing custom field is edited
        """
        key = "maintainer"
        expected_value = "Changed value"
        custom_fields_field: FormField = dialog.findChild(
            FormField, "custom_fields"
        )
        custom_fields_widget: MetadataCustomFieldsWidget = (
            custom_fields_field.widget
        )
        save_button: QPushButton = dialog.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        model = custom_fields_widget.model

        row_id = 2
        assert model.index(row_id, 0).data(Qt.ItemDataRole.DisplayRole) == key
        row_to_change = model.index(row_id, 1)  # maintainer
        model.setData(row_to_change, expected_value, Qt.ItemDataRole.EditRole)
        # noinspection PyUnresolvedReferences
        model.layoutChanged.emit()

        # save the form
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert model_config.has_changes is True
        assert model_config.metadata[key] == expected_value

    def test_edit_empty_custom_field(self, qtbot, dialog, model_config):
        """
        Tests that the model resets the original value when a custom field is left
        empty.
        """
        key = "maintainer"
        expected_value = model_config.metadata["maintainer"]
        row_id = 2

        custom_fields_field: FormField = dialog.findChild(
            FormField, "custom_fields"
        )
        custom_fields_widget: MetadataCustomFieldsWidget = (
            custom_fields_field.widget
        )
        model = custom_fields_widget.model

        assert model.index(row_id, 0).data(Qt.ItemDataRole.DisplayRole) == key

        # set to empty
        row_to_change = model.index(row_id, 1)  # maintainer
        model.setData(row_to_change, " ", Qt.ItemDataRole.EditRole)
        # noinspection PyUnresolvedReferences
        model.layoutChanged.emit()

        assert (
            model.data(row_to_change, Qt.ItemDataRole.DisplayRole)
            == expected_value
        )

    def test_duplicated_in_custom_field(self, qtbot, dialog, model_config):
        """
        Opens the dialog and tests that when a key or values is duplicated, the
        validation fails.
        """
        # change maintainer to email which already exists
        key = "maintainer"
        row_id = 2

        custom_fields_field: FormField = dialog.findChild(
            FormField, "custom_fields"
        )
        custom_fields_widget: MetadataCustomFieldsWidget = (
            custom_fields_field.widget
        )
        model = custom_fields_widget.model

        assert model.index(row_id, 0).data(Qt.ItemDataRole.DisplayRole) == key

        # 1. Set a duplicated key
        row_to_change = model.index(row_id, 0)  # maintainer
        model.setData(row_to_change, "email", Qt.ItemDataRole.EditRole)
        # noinspection PyUnresolvedReferences
        model.layoutChanged.emit()

        # 2. Validate the form
        QTimer.singleShot(100, close_message_box)
        form_data = custom_fields_widget.form.validate()
        assert form_data is False
        assert (
            "following names are duplicated"
            in custom_fields_field.message.text()
        )

    def test_delete_custom_fields(self, qtbot, dialog, model_config):
        """
        Opens the dialog and tests that when a field is deleted, the model
        configuration is correctly updated.
        """
        key_to_delete = "maintainer"
        custom_fields_field: FormField = dialog.findChild(
            FormField, "custom_fields"
        )
        custom_fields_widget: MetadataCustomFieldsWidget = (
            custom_fields_field.widget
        )
        save_button: QPushButton = dialog.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        delete_button: QPushButton = dialog.findChildren(QPushButton)[1]
        assert delete_button.text() == "Delete"

        # delete one field
        custom_fields_widget.table.selectRow(2)
        assert (
            custom_fields_widget.table.selectedIndexes()[0].data()
            == key_to_delete
        )
        assert delete_button.isEnabled() is True
        qtbot.mouseClick(delete_button, Qt.MouseButton.LeftButton)

        # save the form
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # deleted fields
        assert key_to_delete not in model_config.metadata.keys()
        assert model_config.has_changes is True

    def test_delete_multiple_custom_fields(self, qtbot, dialog, model_config):
        """
        Opens the dialog and tests that when more fields are deleted, the model
        configuration is correctly updated.
        """
        keys_to_delete = ["maintainer", "email"]
        custom_fields_field: FormField = dialog.findChild(
            FormField, "custom_fields"
        )
        custom_fields_widget: MetadataCustomFieldsWidget = (
            custom_fields_field.widget
        )
        model = custom_fields_widget.model

        save_button: QPushButton = dialog.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        delete_button: QPushButton = dialog.findChildren(QPushButton)[1]
        assert delete_button.text() == "Delete"

        # delete multiple fields field
        for i in range(0, model.rowCount() + 1):
            row = model.index(i, 0)
            if row.data(Qt.ItemDataRole.DisplayRole) in keys_to_delete:
                custom_fields_widget.table.selectionModel().select(
                    row, QItemSelectionModel.Select | QItemSelectionModel.Rows
                )

        qtbot.mouseClick(delete_button, Qt.MouseButton.LeftButton)
        assert all([key[0] not in keys_to_delete for key in model.fields])

        # save the form
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        all([key not in model_config.metadata.keys() for key in keys_to_delete])
        assert model_config.has_changes is True
