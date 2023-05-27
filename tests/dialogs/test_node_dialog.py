import pytest
from PySide6.QtCore import Qt, QTimer

import pywr_editor
from pywr_editor.dialogs import NodeDialog
from pywr_editor.form import (
    EdgeColorPickerWidget,
    NodeStylePickerWidget,
    ParameterLineEditWidget,
    TextWidget,
)
from pywr_editor.model import Constants, ModelConfig, PywrNodesData
from tests.utils import close_message_box, resolve_model_path


class TestNodeDialog:
    model_file = resolve_model_path("model_dialog_node.json")

    def node_dialog(self, selected_node) -> NodeDialog:
        """
        Initialises the dialog.
        :param selected_node: The ModelConfig instance.
        :return: The ParameterDialog instance.
        """
        model_config = ModelConfig(self.model_file)
        dialog = NodeDialog(model_config=model_config, node_name=selected_node)
        dialog.show()
        return dialog

    @pytest.mark.parametrize(
        "node_name, node_type, props, is_type_enabled",
        [
            (
                "only_type",
                "Input",
                {"edge_color": None, "max_flow": "param1"},
                False,
            ),
            (
                "node_with_edge_color",
                "Input",
                {"edge_color": "sky", "max_flow": None},
                False,
            ),
            (
                "node_with_wrong_edge_color",
                "Input",
                {"edge_color": None, "max_flow": None},
                False,
            ),
            # custom node loaded in "includes"
            ("leaky_pipe", "leakypipe", {}, False),
        ],
    )
    def test_init_node(self, qtbot, node_name, node_type, props, is_type_enabled):
        """
        Tests that the nodes are loaded correctly.
        """
        dialog = self.node_dialog(node_name)
        dialog.show()
        form = dialog.form

        assert form.find_field("name").value() == node_name

        # Check type
        node_type_field = form.find_field("type")
        assert node_type_field.value() == node_type
        assert node_type_field.widget.isEnabled() == is_type_enabled

        # Check other fields
        for field_name, field_value in props.items():
            field = form.find_field(field_name)
            # check ComboBox value
            if field_name == "edge_color":
                widget: EdgeColorPickerWidget = field.widget
                text = field_value.title() if field_value else "Gray (Default)"
                assert widget.combo_box.currentText() == text
            elif field_name == "max_flow" and field_value:
                widget: ParameterLineEditWidget = field.widget
                assert widget.component_obj.name == field_value

            # check returned value
            assert field.value() == field_value

    @pytest.mark.parametrize(
        "new_name, error_message",
        [
            # the node name must be unique
            ("node_with_edge_color", "The node name already exists"),
            # the node name is mandatory
            ("", "The field cannot be empty"),
        ],
    )
    def test_node_name_validation(self, qtbot, new_name, error_message):
        """
        Tests the validation on the node name.
        """
        dialog = self.node_dialog("only_type")
        form = dialog.form

        # change value
        name_field = form.find_field("name")
        line_edit: TextWidget = name_field.widget
        line_edit.line_edit.setText(new_name)

        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == error_message

    @pytest.mark.parametrize(
        "node_name, selected_data",
        [
            ("only_type", NodeStylePickerWidget.default_str_style),
            ("node_with_custom_style", "Works"),
            (
                "node_with_wrong_custom_style",
                NodeStylePickerWidget.default_str_style,
            ),
        ],
    )
    def test_node_style_picker(self, qtbot, node_name, selected_data):
        """
        Tests the NodeStylePickerWidget.
        """
        dialog = self.node_dialog(node_name)
        form = dialog.form

        # 1. Check values
        field = form.find_field(Constants.NODE_STYLE_KEY.value)
        widget: NodeStylePickerWidget = field.widget
        assert widget.combo_box.currentData() == selected_data

        if selected_data == widget.default_str_style:
            assert field.value() is None
        else:
            assert field.value() == selected_data.lower()

        # 2. Test icon change
        if node_name == "only_type":
            index = widget.combo_box.findData("Rainfall")
            widget.combo_box.setCurrentIndex(index)
            assert field.value() == "rainfall"
            assert form.dialog.title.icon.objectName() == "Rainfall"

    def test_rename(self, qtbot):
        """
        Tests when a node is renamed.
        """
        old_name = "node_with_custom_style"
        new_name = "Node X"
        dialog = self.node_dialog(old_name)
        form = dialog.form
        type_field = form.find_field("type")

        # change name
        widget: TextWidget = form.find_field("name").widget
        widget.line_edit.setText(new_name)
        assert form.save_button.isEnabled() is True

        # send form
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)
        assert type_field.message.text() == ""

        # check nodes
        assert form.model_config.nodes.find_node_index_by_name(old_name) is None
        assert form.model_config.nodes.config(new_name) == {
            "name": new_name,
            "type": "input",
            "position": {"node_style": "works"},
        }

        # check edge and table
        assert form.model_config.json["edges"][1] == ["only_type", new_name]
        # name unchanged
        assert form.model_config.json["tables"]["Table 1"]["index"] == old_name

        # check dialog title that was changed
        assert dialog.title.title.text() == new_name

    def test_virtual_node(self, qtbot):
        """
        Tests that the edge color field is not shown when the node is virtual.
        """
        dialog = self.node_dialog("aggregated_node")
        form = dialog.form
        assert form.find_field("edge_color") is None

    def test_custom_node_type(self, qtbot):
        """
        Tests that the node type can be changed for non included nodes and
        checks field validation.
        """
        node_name = "custom_node"
        dialog = self.node_dialog(node_name)
        form = dialog.form
        form_field = form.find_field("type")
        widget: TextWidget = form_field.widget

        # 1. Change type to valid string
        new_type = "CustomNodev2"
        widget.line_edit.setText(new_type)
        assert form.save_button.isEnabled() is True

        # send form
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)

        # check nodes
        assert form.model_config.nodes.config(node_name) == {
            "name": node_name,
            "type": new_type,
            "value": 5,
            "other_node": "leaky_pipe",
        }

        # 2. Set a invalid Python class
        widget.line_edit.setText("Wrong className")
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)
        assert "must be a valid Python" in form_field.message.text()

        # 2. Set an empty type
        form_field.clear_message()
        widget.line_edit.setText("")
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)
        assert "must be a valid Python" in form_field.message.text()

    def test_missing_sections(self, qtbot):
        """
        Checks that all built-in pywr nodes have a form section.
        """
        nodes_data = PywrNodesData()

        missing_sections = []
        for key, info in nodes_data.data.items():
            pywr_class = nodes_data.class_from_type(key)
            if not hasattr(pywr_editor.dialogs, f"{pywr_class}Section"):
                missing_sections.append(key)

        assert (
            len(missing_sections) == 0
        ), f"The following sections are missing: {','.join(missing_sections)}"
