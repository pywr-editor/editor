import pytest
from functools import partial
from pathlib import Path
from PySide6.QtCore import QTimer, QItemSelectionModel
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QPushButton,
    QApplication,
)
from pywr_editor.dialogs import IncludesDialog
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path, model_path, check_msg


class TestTablesIncludes:
    model_file = resolve_model_path("model_1.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "file, added_to_model, error_message",
        [
            # file not containing valid Pywr classes
            (
                "dialogs/test_dialog_metadata.py",
                True,
                "does not contain any valid pywr",
            ),
            # not parsable
            (
                "json_models/files/custom_parameter_syntax_error.py",
                False,
                "cannot be parsed",
            ),
            # non existing file
            ("data/non-existing-file.py", False, "does not exist"),
            # not .py
            (
                "json_models/files/table.csv",
                False,
                "must be a valid Python (.py) file",
            ),
            # duplicated
            (
                "json_models/files/custom_parameter.py",
                True,
                "already in the import list",
            ),
            # valid file
            ("json_models/files/custom_parameter3.py", True, None),
        ],
    )
    def test_add_files(
        self, qtbot, model_config, file, added_to_model, error_message
    ):
        """
        Tests the add_files method.
        """
        dialog = IncludesDialog(model_config)
        dialog.hide()
        all_files = list(map(str, dialog.model.files_dict.keys()))

        # always use absolute paths to emulate QFIleDialog
        file = Path(__file__).parent.parent / file

        # button is disabled
        if error_message is None:
            assert dialog.save_button.isEnabled() is False

        # add the file
        QTimer.singleShot(100, partial(check_msg, error_message))
        dialog.add_files([str(file)])

        # check for errors
        # file has no valid classes, but it is added nonetheless
        if "test_dialog_metadata.py" in str(file):
            assert file in dialog.model.files_dict

        # check if file was added to the model
        # all_files = list(map(str, dialog.model.files_dict))
        if not added_to_model:
            assert file not in dialog.model.files_dict
        else:
            assert file in dialog.model.files_dict

        # valid file
        if error_message is None:
            all_files.append(file)

            # save form
            dialog.on_save()
            qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)

            # convert to relative - all files are stored in files folder
            all_files = [f"files\\{Path(f).name}" for f in all_files]
            # this is excluded from the original list
            all_files.insert(0, "model_2.json")

            assert model_config.has_changes is True
            assert model_config.json["includes"] == all_files

        # add delay for activeModalWidget to avoid conflicts between messages and tests
        qtbot.wait(100)

    @pytest.mark.parametrize("action", ["delete", "discard"])
    def test_delete_file(self, qtbot, model_config, action):
        """
        Tests that a file is deleted correctly.
        """
        dialog = IncludesDialog(model_config)
        table = dialog.table

        # select a file from the list
        deleted_file = "custom_parameter.py"
        model_index = table.model.index(0, 0)
        assert model_index.data() == deleted_file
        table.selectionModel().select(model_index, QItemSelectionModel.Select)

        # delete button is enabled and the item is selected
        assert dialog.delete_button.isEnabled() is True
        assert table.selectionModel().isSelected(model_index) is True

        # delete file
        def confirm_deletion():
            widget = QApplication.activeModalWidget()
            assert (
                "classes that are used by 2 model components: MyParameter, "
                + "LicenseParameter"
                in widget.text()
            )
            if action == "delete":
                qtbot.mouseClick(
                    widget.findChild(QPushButton), Qt.MouseButton.LeftButton
                )
            else:
                qtbot.mouseClick(
                    widget.findChildren(QPushButton)[1],
                    Qt.MouseButton.LeftButton,
                )

        QTimer.singleShot(200, confirm_deletion)
        qtbot.mouseClick(dialog.delete_button, Qt.MouseButton.LeftButton)

        # check file in data
        full_deleted_file = model_path() / "files" / deleted_file
        if action == "delete":
            assert full_deleted_file not in dialog.model.files_dict
        else:
            assert full_deleted_file in dialog.model.files_dict
