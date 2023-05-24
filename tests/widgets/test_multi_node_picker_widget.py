import pytest
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import Form, MultiNodePickerWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestMultiNodePickerWidget:
    """
    Tests the MultiNodePickerWidget.
    """

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(resolve_model_path("model_multi_node_picker_widget.json"))

    @staticmethod
    def form(
        model_config,
        node_names: list[str] | None,
        is_mandatory: bool,
        include_node_keys: list[str] | None,
    ) -> Form:
        """
        Initialises the form.
        :param model_config: The model configuration instance.
        :param node_names: The selected node names.
        :param is_mandatory: Whether at least one node should be provided or the
        field can be left empty.
        :param include_node_keys: A string or list of strings representing a node key
        to only include in the widget.
        :return: An instance of ParameterForm.
        """
        # mock widgets
        form = Form(
            fields={
                "Section": [
                    {
                        "name": "node_names",
                        "field_type": MultiNodePickerWidget,
                        "field_args": {
                            "is_mandatory": is_mandatory,
                            "include_node_keys": include_node_keys,
                        },
                        "value": node_names,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        # used by widget
        form.model_config = model_config

        form.load_fields()
        return form

    @pytest.mark.parametrize(
        "node_names, is_mandatory, validate",
        [
            # names are provided
            (["Reservoir2", "Virtual"], True, True),
            (["Reservoir2", "Virtual"], False, True),
            # empty node list
            (None, True, False),
            (None, False, True),
        ],
    )
    def test_valid(self, qtbot, model_config, node_names, is_mandatory, validate):
        """
        Tests that the nodes names are correctly set.
        """
        form = self.form(
            model_config=model_config,
            node_names=node_names,
            is_mandatory=is_mandatory,
            include_node_keys=None,
        )

        widget: MultiNodePickerWidget = form.find_field("node_names").widget

        # 1. Check values
        assert widget.combo_box.all_items == [
            "Reservoir (Storage)",
            "Reservoir2 (Storage)",
            "Virtual (Rolling virtual storage)",
            "Aggregated (Aggregated storage)",
        ]

        assert widget.field.message.text() == ""
        assert widget.get_value() == node_names

        # 2. Submit form for validation
        out = widget.validate("", "", widget.get_value())
        if validate is False:
            assert out.error_message == "The field cannot be empty"
        else:
            assert out.validation is True

    @pytest.mark.parametrize(
        "node_names, is_mandatory, validate",
        [
            # names are provided
            (["Reservoir2"], True, True),
            (["Reservoir2"], False, True),
            # empty node list
            (None, True, False),
            (None, False, True),
        ],
    )
    def test_valid_with_filters(
        self, qtbot, model_config, node_names, is_mandatory, validate
    ):
        """
        Tests that the nodes names are correctly set when a filter on the node types
        is set. The node named "Aggregated" is not included.
        """
        form = self.form(
            model_config=model_config,
            node_names=node_names,
            is_mandatory=is_mandatory,
            include_node_keys=model_config.pywr_node_data.get_keys_with_parent_class(
                "Storage"
            ),
        )

        widget: MultiNodePickerWidget = form.find_field("node_names").widget

        # 1. Check values
        assert widget.combo_box.all_items == [
            "Reservoir (Storage)",
            "Reservoir2 (Storage)",
            "Virtual (Rolling virtual storage)",
        ]

        assert widget.field.message.text() == ""
        assert widget.get_value() == node_names

        # 2. Submit form for validation
        out = widget.validate("", "", widget.get_value())
        if validate is False:
            assert out.error_message == "The field cannot be empty"
        else:
            assert out.validation is True

    @pytest.mark.parametrize(
        "node_names, selected, class_to_include, init_message",
        [
            # non existing node
            (
                ["non_existing_node", "Reservoir"],
                ["Reservoir"],
                None,
                "following node names do not exist in the model",
            ),
            # wrong node type (Aggregated) is passed, but only Storage nodes are allowed
            (["Aggregated"], None, "Storage", "their type is not allowed"),
            # wrong value type
            (
                "Reservoir",
                None,
                None,
                "node names must be a list",
            ),
            # node not a string
            (
                [1, "Reservoir"],
                None,
                None,
                "node names must be valid strings",
            ),
        ],
    )
    def test_invalid(
        self,
        qtbot,
        model_config,
        node_names,
        selected,
        class_to_include,
        init_message,
    ):
        """
        Tests the widget when invalid values are passed.
        """
        include_node_keys = None
        if class_to_include:
            include_node_keys = model_config.pywr_node_data.get_keys_with_parent_class(
                class_to_include
            )
        form = self.form(
            model_config=model_config,
            node_names=node_names,
            is_mandatory=False,
            include_node_keys=include_node_keys,
        )

        widget: MultiNodePickerWidget = form.find_field("node_names").widget
        assert init_message in widget.field.message.text()
        assert widget.get_value() == selected
