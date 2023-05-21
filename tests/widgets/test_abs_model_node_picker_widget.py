import pytest
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import AbstractModelNodePickerWidget, ParameterForm
from pywr_editor.model import ModelConfig, ParameterConfig
from tests.utils import resolve_model_path


class TestDialogAbstractModelNodePickerWidget:
    """
    Tests AbstractModelNodePickerWidget.
    """

    @staticmethod
    def model_config(
        config_file: str,
    ) -> ModelConfig:
        """
        Initialises the model configuration.
        :param config_file: The config file name.
        :return: The ModelConfig instance.
        """
        return ModelConfig(resolve_model_path(config_file))

    def form(
        self,
        value: str | None,
        is_mandatory: bool,
        include_node_types: list[str] | None,
        exclude_node_types: list[str] | None,
        config_file: str = "model_dialog_parameter_abs_model_node_picker_widget.json",
    ) -> ParameterForm:
        """
        Initialises the form.
        :param value: The selected node name.
        :param is_mandatory: Whether at least one parameter should be provided or the
        field can be left empty.
        :param include_node_types: A string or list of strings representing a node key
        to only include in the widget.
        For example storage for the Storage node to include only storage nodes, all
        other node types will not be shown.
        :param exclude_node_types: A string or list of strings representing a node key
        to exclude from the widget.
        :param config_file: The config file name.
        :return: An instance of ParameterForm.
        """
        # mock widgets
        field_args = {
            "log_name": "AbstractModelNodePickerWidget",
            "is_mandatory": is_mandatory,
        }
        if include_node_types:
            field_args["include_node_types"] = include_node_types
        if exclude_node_types:
            field_args["exclude_node_types"] = exclude_node_types

        form = ParameterForm(
            model_config=self.model_config(config_file),
            parameter_obj=ParameterConfig({}),
            available_fields={
                "Section": [
                    {
                        "name": "node_name",
                        "field_type": AbstractModelNodePickerWidget,
                        "field_args": field_args,
                        "value": value,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()
        return form

    def test_empty_model_nodes(self, qtbot):
        """
        Tests the widget when the model does not contain any parameters.
        :return:
        """
        form = self.form(
            value=None,
            include_node_types=None,
            exclude_node_types=None,
            is_mandatory=True,
            config_file="model_wo_nodes.json",
        )
        model_params_field = form.find_field_by_name("node_name")
        # noinspection PyTypeChecker
        model_nodes_widget: AbstractModelNodePickerWidget = model_params_field.widget

        assert "are no nodes available" in model_params_field.message.text()
        assert len(model_nodes_widget.combo_box.all_items) == 1

    @pytest.mark.parametrize(
        "node_name, include_node_types, exclude_node_types, is_mandatory, total_nodes",
        [
            # all node types are allowed
            ("Reservoir1", None, None, True, 3),
            # node name is not provided. Default set to None, validation fails
            (None, None, None, True, 3),
            # node name is not provided. Default set to None, validation passes
            (None, None, None, False, 3),
            # only storage nodes are allowed
            ("Reservoir1", ["storage"], None, True, 1),
            # exclude output nodes
            ("Reservoir1", None, ["output"], True, 2),
            # only some types are allowed
            ("Reservoir2", ["storage", "reservoir"], None, True, 2),
        ],
    )
    def test_valid_types(
        self,
        qtbot,
        node_name,
        include_node_types,
        exclude_node_types,
        is_mandatory,
        total_nodes,
    ):
        """
        Tests the widget when a valid node name is used.
        """
        form = self.form(
            value=node_name,
            include_node_types=include_node_types,
            exclude_node_types=exclude_node_types,
            is_mandatory=is_mandatory,
        )
        model_params_field = form.find_field_by_name("node_name")
        # noinspection PyTypeChecker
        model_nodes_widget: AbstractModelNodePickerWidget = model_params_field.widget

        # 1. Check ComboBox
        assert model_params_field.message.text() == ""
        if node_name is not None:
            assert node_name in model_nodes_widget.combo_box.currentText()
            assert model_nodes_widget.get_value() == node_name
            # name is in the ComboBox
            assert any(
                [node_name in value for value in model_nodes_widget.combo_box.all_items]
            )
        # no node is selected
        else:
            assert model_nodes_widget.combo_box.currentText() == "None"

        # check total elements in widget
        assert len(model_nodes_widget.combo_box.all_items) == total_nodes + 1

        # 2. Validation
        out = model_nodes_widget.validate(
            "name", "Name", model_nodes_widget.get_value()
        )
        if node_name is not None and is_mandatory:
            assert out.validation is True
        elif is_mandatory is False:
            assert out.validation is True
        else:
            assert out.validation is False
            assert out.error_message == "You must select a model node"

    @pytest.mark.parametrize(
        "node_name, include_node_types, exclude_node_types, is_mandatory, init_message, total_nodes",  # noqa: E501
        [
            # only output is allowed, but reservoir node is set
            ("Reservoir2", ["output"], None, True, "is not valid", 1),
            # same as above but validation passes (field is optional)
            ("Reservoir2", ["output"], None, False, "is not valid", 1),
            # set node type is excluded
            (
                "Reservoir1",
                None,
                ["reservoir", "storage"],
                True,
                "is not valid",
                1,
            ),
            # non-existing name
            ("non_existing_name", None, None, True, "does not exist", 3),
            # non-existing name, validation passes (field is optional)
            ("non_existing_name", None, None, False, "does not exist", 3),
            # invalid type
            (
                123,
                None,
                False,
                True,
                "must be a string",
                3,
            ),
        ],
    )
    def test_invalid_types(
        self,
        qtbot,
        node_name,
        include_node_types,
        exclude_node_types,
        is_mandatory,
        init_message,
        total_nodes,
    ):
        """
        Tests the widget when the provided node name is not valid (only certain node
        types are allowed or the node does not exist).
        """
        form = self.form(
            value=node_name,
            include_node_types=include_node_types,
            exclude_node_types=exclude_node_types,
            is_mandatory=is_mandatory,
        )
        model_params_field = form.find_field_by_name("node_name")
        # noinspection PyTypeChecker
        model_nodes_widget: AbstractModelNodePickerWidget = model_params_field.widget

        # 1. Check init message
        assert init_message in model_params_field.message.text()

        # 2. Validation
        out = model_nodes_widget.validate(
            "name", "Name", model_nodes_widget.combo_box.currentText()
        )
        if is_mandatory:
            assert out.validation is False
        else:
            assert out.validation is True

        # 3. Check ComboBox
        assert model_nodes_widget.combo_box.currentText() == "None"
        assert model_nodes_widget.get_value() is None
        assert node_name not in model_nodes_widget.combo_box.all_items
        assert len(model_nodes_widget.combo_box.all_items) == total_nodes + 1
