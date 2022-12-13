import pytest
from PySide6.QtWidgets import QPushButton, QWidget
from pywr_editor.model import ModelConfig, ParameterConfig
from pywr_editor.form import ParameterTypeSelectorWidget, ParameterForm
from tests.utils import resolve_model_path

"""
 Test the ParameterTypeSelectorWidget.
"""


class TestDialogParameterTypeSelectorWidget:
    @staticmethod
    def form(value: dict, filtered_keys: list[str] | None) -> ParameterForm:
        """
        Initialises the form.
        :param value: The dictionary representing the parameter.
        :param filtered_keys: A list of parameter keys only to include in the widget.
        :return: An instance of ParameterForm.
        """
        if filtered_keys:
            field_args = {"include_param_key": filtered_keys}
        else:
            field_args = None

        model = ModelConfig(resolve_model_path("model_1.json"))
        form = ParameterForm(
            model_config=ModelConfig(resolve_model_path("model_1.json")),
            parameter_obj=ParameterConfig(value),
            available_fields={
                "Section": [
                    {
                        "name": "type",
                        "field_type": ParameterTypeSelectorWidget,
                        "field_args": field_args,
                        "value": model.parameters.parameter(config=value),
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()
        return form

    @pytest.mark.parametrize(
        "param_dict, param_key, combo_box_selection, filtered_keys",
        [
            # all parameter types are allowed
            (
                {"type": "constant", "value": 23},
                "constant",
                "Constant parameter",
                None,
            ),
            (
                {"type": "constantparameter", "value": 23},
                "constant",
                "Constant parameter",
                None,
            ),
            (
                {"type": "monthlyprofile", "values": list(range(1, 13))},
                "monthlyprofile",
                "Monthly profile parameter",
                None,
            ),
            # parameter type is not provided. Default is set w/o warning message
            ({}, None, "Constant parameter", None),
            # empty type. Default is set w/o warning message
            ({"type": ""}, None, "Constant parameter", None),
            # only Monthly profile is allowed
            (
                {"type": "monthlyprofile", "values": list(range(1, 13))},
                "monthlyprofile",
                "Monthly profile parameter",
                ["monthlyprofile"],
            ),
            # custom parameter in model "includes"
            (
                {"type": "MyParameter", "values": [0, 1]},
                "my",
                "MyParameter",
                None,
            ),
            # custom parameter in model "includes" with filters
            (
                {"type": "MyParameter", "values": [0, 1]},
                "my",
                "MyParameter",
                ["my"],
            ),
            # custom parameter NOT in model "includes"
            (
                {"type": "MyShinyParameter", "values": [0, 1]},
                "myshiny",
                "Custom parameter (not imported)",
                None,
            ),
            # custom parameter NOT in model "includes" with filters
            # parameter is included
            (
                {"type": "MyShinyParameter", "values": [0, 1]},
                "myshiny",
                "Custom parameter (not imported)",
                ["monthlyprofile"],
            ),
        ],
    )
    def test_valid_param_types(
        self, qtbot, param_dict, param_key, combo_box_selection, filtered_keys
    ):
        """
        Tests the widget when a valid parameter type is used.
        """
        form = self.form(param_dict, filtered_keys)
        param_type_field = form.find_field_by_name("type")
        # noinspection PyTypeChecker
        param_type_widget: ParameterTypeSelectorWidget = param_type_field.widget

        assert param_type_field.message.text() == ""
        assert param_type_widget.combo_box.currentText() == combo_box_selection

        # always includes Custom parameter
        if filtered_keys:
            assert (
                len(param_type_widget.combo_box.all_items)
                == len(filtered_keys) + 1
            )

    @pytest.mark.parametrize(
        "param_dict, selected_param_type_name, filtered_keys",
        [
            # only constant is allowed, but monthly profile is set
            (
                {"type": "monthlyProfile", "values": list(range(1, 13))},
                "Constant parameter",
                ["constant"],
            ),
            # constant is set but only profiles are allowed. Default widget is first
            # item in filter list
            (
                {"type": "constant", "value": 981},
                "Weekly profile parameter",
                ["weeklyprofile", "dailyprofile"],
            ),
            # custom parameter
            (
                {"type": "MyParameter", "values": [0, 1]},
                "Constant parameter",
                ["constant"],
            ),
        ],
    )
    def test_invalid_param_types(
        self, qtbot, param_dict, selected_param_type_name, filtered_keys
    ):
        """
        Tests the widget when only certain parameter types are allowed, but the passed
        parameter is not.
        """
        form = self.form(param_dict, filtered_keys)
        param_type_field = form.find_field_by_name("type")
        # noinspection PyTypeChecker
        param_type_widget: ParameterTypeSelectorWidget = param_type_field.widget

        assert param_type_widget.combo_box.findData(param_dict["type"]) == -1

        assert "is not allowed" in param_type_field.message.text()
        # select new default
        assert (
            param_type_widget.combo_box.currentText()
            == selected_param_type_name
        )
        # always includes Custom parameter
        assert (
            len(param_type_widget.combo_box.all_items) == len(filtered_keys) + 1
        )
