import pytest
from PySide6.QtCore import QItemSelectionModel, Qt, QTimer
from PySide6.QtWidgets import QPushButton

from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import RecorderPageWidget
from pywr_editor.form import (
    FloatWidget,
    NodePickerWidget,
    NodesAndFactorsDialog,
    NodesAndFactorsTableWidget,
)
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestAnnualTotalFlowSection:
    """
    Tests the NodesListWidget and AnnualTotalFlowSection.
    """

    model_file = resolve_model_path(
        "model_dialog_recorders_annual_tot_flow_section.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "recorder_name, expected_dict, validation_message",
        [
            # empty values but validation does not pass, all fields are mandatory
            (
                "valid_no_values",
                {
                    "nodes": [],
                    "factors": [],
                },
                "must provide one or more nodes",
            ),
            # values with valid nodes but without factors
            (
                "valid_value_with_nodes",
                {
                    "nodes": ["Link", "Output"],
                    "factors": [],
                },
                None,
            ),
            # values with valid nodes and factors
            (
                "valid_value_with_nodes_and_factors",
                {
                    "nodes": ["Link", "Output"],
                    "factors": [11, -18],
                },
                None,
            ),
            # when all factors are ones, list is not returned due to default value
            (
                "valid_value_with_nodes_and_one_factors",
                {
                    "nodes": ["Link", "Output"],
                    "factors": [],
                },
                None,
            ),
        ],
    )
    def test_valid_recorder(
        self,
        qtbot,
        model_config,
        recorder_name,
        expected_dict,
        validation_message,
    ):
        """
        Tests when the widget and section contains valid data.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        field = form.find_field("nodes_and_factors")
        widget: NodesAndFactorsTableWidget = field.widget

        # 1. Check message and value
        assert field.message.text() == ""

        # check model
        assert widget.model.nodes == expected_dict["nodes"]
        if expected_dict["factors"]:
            assert widget.model.factors == expected_dict["factors"]
        else:
            assert widget.model.factors == [1] * len(expected_dict["nodes"])

        # check value returned by the widget
        assert field.value() == expected_dict

        # 2. Validate form
        QTimer.singleShot(100, close_message_box)
        form_data = form.validate()

        if validation_message is not None:
            assert validation_message in field.message.text()
        # validate form and test section filter
        else:
            expected_form_data = {
                "name": recorder_name,
                "type": "annualtotalflow",
                "nodes": expected_dict["nodes"],
            }
            if expected_dict["factors"]:
                expected_form_data["factors"] = expected_dict["factors"]

            assert form_data == expected_form_data

        # 3. Test reset
        widget.reset()
        assert widget.get_value() == widget.get_default_value()

    @pytest.mark.parametrize(
        "recorder_name, init_message",
        [
            ("invalid_nodes_not_list", "must be valid lists"),
            ("invalid_factors_not_list", "must be valid lists"),
            ("invalid_list_size", "match the number of factors"),
            ("invalid_node_type", "contain only strings"),
            ("invalid_non_existing_node", "model configuration do not exist"),
            ("invalid_factor_type", "must contain only number"),
        ],
    )
    def test_invalid_recorder(
        self,
        qtbot,
        model_config,
        recorder_name,
        init_message,
    ):
        """
        Tests when the widget contains invalid data.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        field = form.find_field("nodes_and_factors")
        widget: NodesAndFactorsTableWidget = field.widget

        # check message and values
        assert init_message in field.message.text()
        assert widget.model.nodes == []
        assert widget.model.factors == []
        assert widget.get_value() == {
            "nodes": [],
            "factors": [],
        }

    def test_delete_row(self, qtbot, model_config):
        """
        Tests that a row is deleted correctly.
        """
        dialog = RecordersDialog(model_config, "valid_value_with_nodes_and_factors")
        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()

        field = selected_page.form.find_field("nodes_and_factors")
        widget: NodesAndFactorsTableWidget = field.widget
        table = widget.table

        # select a file from the list
        deleted_node = "Output"
        model_index = table.model.index(1, 0)
        assert model_index.data() == deleted_node
        table.selectionModel().select(model_index, QItemSelectionModel.Select)

        # delete button is enabled and the item is selected
        assert widget.delete_button.isEnabled() is True
        assert table.selectionModel().isSelected(model_index) is True

        # delete file
        qtbot.mouseClick(widget.delete_button, Qt.MouseButton.LeftButton)

        # check model data
        assert widget.model.nodes == ["Link"]
        assert widget.model.factors == [11]

    def test_add_new_row(self, qtbot, model_config):
        """
        Tests when a new row is added.
        """
        dialog = RecordersDialog(model_config, "valid_value_with_nodes_and_factors")
        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()

        field = selected_page.form.find_field("nodes_and_factors")
        widget: NodesAndFactorsTableWidget = field.widget

        qtbot.mouseClick(widget.add_button, Qt.MouseButton.LeftButton)
        # noinspection PyTypeChecker
        child_dialog: NodesAndFactorsDialog = selected_page.findChild(
            NodesAndFactorsDialog
        )
        # noinspection PyTypeChecker
        node_widget: NodePickerWidget = child_dialog.findChild(NodePickerWidget)

        # 1. Check that already-added nodes are not in the ComboBox
        assert "Link" not in node_widget.combo_box.all_items
        assert "Output" not in node_widget.combo_box.all_items

        # 2. Add a new entry and save the form
        node_widget.combo_box.setCurrentText("Reservoir2 (Storage)")
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # 3. Check the model
        assert widget.get_value() == {
            "nodes": ["Link", "Output", "Reservoir2"],
            "factors": [11, -18, 1],
        }

    def test_edit_row(self, qtbot, model_config):
        """
        Tests when a new row is added.
        """
        dialog = RecordersDialog(model_config, "valid_value_with_nodes_and_factors")
        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()

        field = selected_page.form.find_field("nodes_and_factors")
        widget: NodesAndFactorsTableWidget = field.widget
        table = widget.table

        # 1. Select item first
        node_to_edit = "Output"
        model_index = table.model.index(1, 0)
        assert model_index.data() == node_to_edit
        table.selectionModel().select(model_index, QItemSelectionModel.Select)
        qtbot.mouseClick(widget.edit_button, Qt.MouseButton.LeftButton)

        # 2. Check the value
        # noinspection PyTypeChecker
        child_dialog: NodesAndFactorsDialog = selected_page.findChild(
            NodesAndFactorsDialog
        )
        # noinspection PyTypeChecker
        node_widget: NodePickerWidget = child_dialog.findChild(NodePickerWidget)
        # noinspection PyTypeChecker
        factor_widget: FloatWidget = child_dialog.findChild(FloatWidget)
        assert node_to_edit in node_widget.combo_box.currentText()
        assert factor_widget.get_value() == -18

        # 3. Change the value and send form
        factor_widget.line_edit.setText("500")
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(QPushButton, "save_button")
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # 3. Check the model
        assert widget.get_value() == {
            "nodes": ["Link", "Output"],
            "factors": [11, 500],
        }
