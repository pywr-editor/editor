import pytest
from PySide6.QtCore import QItemSelectionModel, Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QWidget

import pywr_editor
from pywr_editor.dialogs import RecorderDialogForm, RecordersDialog
from pywr_editor.dialogs.recorders.recorder_empty_page import RecorderEmptyPage
from pywr_editor.form import FormField, RecorderTypeSelectorWidget
from pywr_editor.model import ModelConfig, PywrRecordersData
from tests.utils import close_message_box, resolve_model_path


class TestRecordersDialog:
    """
    Tests the general behaviour of the recorder dialog (when adding or deleting
    recorder, etc.)
    """

    model_file = resolve_model_path("model_dialog_recorders.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.fixture()
    def dialog(self, model_config) -> RecordersDialog:
        """
        Initialises the dialog.
        :param model_config: The ModelConfig instance.
        :return: The RecordersDialog instance.
        """
        dialog = RecordersDialog(model_config)
        dialog.show()
        return dialog

    def test_add_new_recorder(self, qtbot, model_config, dialog):
        """
        Tests that a new recorder can be correctly added.
        """
        pages = dialog.pages
        empty_page = pages.findChild(QWidget, "empty_page")

        add_button: QPushButton = empty_page.findChild(QPushButton, "add_button")
        qtbot.mouseClick(add_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        # new name is random
        new_name = dialog.list_model.recorder_names[-1]
        assert "Recorder " in new_name

        # Recorder model
        # the recorder is added to the model internal list
        assert new_name in dialog.list_model.recorder_names
        # the recorder appears in the recorder list on the left-hand side of the dialog
        new_model_index = dialog.list_model.index(model_config.recorders.count - 1, 0)
        assert new_model_index.data() == new_name

        # the item is selected
        assert dialog.list.table.selectedIndexes()[0].data() == new_name

        # Page widget
        selected_page = pages.currentWidget()
        selected_page.findChild(RecorderDialogForm).load_fields()
        assert new_name in selected_page.findChild(QLabel).text()
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        # button is disabled
        assert save_button.isEnabled() is False

        # the recorder is in the widgets list
        assert new_name in dialog.list_model.recorder_names
        # the form page is selected
        assert selected_page.objectName() == new_name
        name_field = selected_page.findChild(FormField, "name")
        type_field: FormField = selected_page.findChild(FormField, "type")
        # noinspection PyUnresolvedReferences
        node_widget: pywr_editor.NodePickerWidget = selected_page.findChild(
            FormField, "node"
        ).widget
        # the form is filled with the name and type is NodeRecorder
        # noinspection PyUnresolvedReferences
        assert name_field.value() == new_name
        assert type_field.value() == "node"

        # the model is updated
        assert model_config.has_changes is True
        assert model_config.recorders.exists(new_name) is True
        assert model_config.recorders.config(new_name) == {
            "type": "node",
        }

        # rename and save
        node_widget.combo_box.setCurrentText("Reservoir (Storage)")
        renamed_recorder_name = "A new shiny name"
        name_field.widget.line_edit.setText(renamed_recorder_name)

        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""
        assert node_widget.field.message.text() == ""

        # the page widget is renamed
        assert renamed_recorder_name in dialog.list_model.recorder_names
        assert renamed_recorder_name in selected_page.findChild(QLabel).text()

        # model configuration
        assert model_config.recorders.exists(new_name) is False
        assert model_config.recorders.exists(renamed_recorder_name) is True
        assert model_config.recorders.config(renamed_recorder_name) == {
            "type": "node",
            "node": "Reservoir",
        }

    def test_clone_recorder(self, qtbot, model_config, dialog):
        """
        Tests the clone recorder button.
        """
        pages = dialog.pages
        current_recorder = "node_aggregated_rec"

        # Page widget
        pages.set_page_by_name(current_recorder)
        selected_page = pages.currentWidget()
        # noinspection PyUnresolvedReferences
        selected_page.findChild(RecorderDialogForm).load_fields()

        assert selected_page.name == current_recorder

        # Clone the recorder
        # noinspection PyTypeChecker
        clone_button: QPushButton = selected_page.findChild(QPushButton, "clone_button")
        qtbot.mouseClick(clone_button, Qt.MouseButton.LeftButton)

        # new name is random
        new_name = dialog.list_model.recorder_names[-1]
        assert "Recorder " in new_name
        # the recorder is in the widgets list
        assert new_name in dialog.list_model.recorder_names

        # the form page is selected
        assert pages.currentWidget().objectName() == new_name

        # the model is updated
        assert model_config.has_changes is True
        assert model_config.recorders.exists(new_name) is True
        assert model_config.recorders.config(new_name) == {
            "type": "AggregatedRecorder",
            "recorders": ["node_numpy_rec_dict", "node_link_rec"],
        }

    def test_rename_recorder(self, qtbot, model_config, dialog):
        """
        Tests that a recorder is renamed correctly.
        """
        current_name = "node_link_rec"
        new_name = "Node link recorder"
        pages = dialog.pages

        # select the recorder
        pages.set_page_by_name(current_name)
        selected_page = pages.currentWidget()
        # noinspection PyUnresolvedReferences
        form: RecorderDialogForm = selected_page.form

        form.load_fields()
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        name_field = form.find_field("name")

        # Change the name and save
        assert name_field.value() == current_name
        name_field.widget.line_edit.setText(new_name)

        qtbot.wait(200)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""

        # the page widget is renamed
        assert new_name in dialog.list_model.recorder_names
        assert new_name in selected_page.findChild(QLabel).text()

        # model has changes
        assert model_config.has_changes is True
        assert model_config.recorders.exists(current_name) is False
        assert model_config.recorders.exists(new_name) is True

        assert model_config.recorders.config(new_name) == {
            "type": "node",
            "node": "Link",
        }

        # check recorder depending on renamed item
        assert model_config.recorders.config("node_aggregated_rec") == {
            "type": "AggregatedRecorder",
            "recorders": ["node_numpy_rec_dict", new_name],
        }

        # set duplicated name
        name_field.widget.line_edit.setText("node_storage_rec")
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert "already exists" in name_field.message.text()
        assert new_name in model_config.recorders.names

    def test_delete_recorder(self, qtbot, model_config, dialog):
        """
        Tests that a recorder is deleted correctly.
        """
        deleted_recorder = "node_storage_rec"
        pages = dialog.pages
        dialog.show()

        # select a recorder from the list
        model_index = dialog.list_model.index(1, 0)
        assert model_index.data() == deleted_recorder
        dialog.list.table.selectionModel().select(
            model_index, QItemSelectionModel.Select
        )

        # delete button is enabled and the item is selected
        delete_button: QPushButton = pages.findChild(
            QWidget, deleted_recorder
        ).findChild(QPushButton, "delete_button")
        assert delete_button.isEnabled() is True
        assert dialog.list.table.selectedIndexes()[0].data() == deleted_recorder

        # delete
        def confirm_deletion():
            widget = QApplication.activeModalWidget()
            qtbot.mouseClick(widget.findChild(QPushButton), Qt.MouseButton.LeftButton)

        QTimer.singleShot(100, confirm_deletion)
        qtbot.mouseClick(delete_button, Qt.MouseButton.LeftButton)

        assert isinstance(pages.currentWidget(), RecorderEmptyPage)
        assert model_config.recorders.exists(deleted_recorder) is False
        assert deleted_recorder not in dialog.list_model.recorder_names

    def test_missing_sections(self, qtbot):
        """
        Checks that all built-in pywr recorders have a form section.
        """
        recorders_data = PywrRecordersData()

        missing_sections = []
        for key, info in recorders_data.data.items():
            pywr_class = recorders_data.class_from_type(key)
            if not hasattr(pywr_editor.dialogs, f"{pywr_class}Section"):
                missing_sections.append(key)

        assert (
            len(missing_sections) == 0
        ), f"The following sections are missing: {','.join(missing_sections)}"

    def test_sections(self, qtbot, model_config, dialog):
        """
        Tests that the sections do not throw any exception when loaded.
        """
        param_name = "node_storage_rec"
        dialog = RecordersDialog(model_config, param_name)

        selected_page = dialog.pages.currentWidget()
        form = selected_page.form

        recorder_type_widget: RecorderTypeSelectorWidget = form.find_field(
            "type"
        ).widget
        for name in recorder_type_widget.combo_box.all_items:
            recorder_type_widget.combo_box.setCurrentText(name)
