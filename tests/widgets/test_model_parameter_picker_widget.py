import pytest
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import ModelParameterPickerWidget, ParameterForm
from pywr_editor.model import ModelConfig, ParameterConfig
from tests.utils import resolve_model_path


class TestDialogModelParameterPickerWidget:
    """
    Tests ModelParameterPickerWidget.
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
        filtered_keys: list[str] | None,
        config_file: str = "model_dialog_parameter_model_param_picker_widget.json",
    ) -> ParameterForm:
        """
        Initialises the form.
        :param value: The selected parameter name.
        :param filtered_keys: A list of parameter keys only to include in the widget.
        :param config_file: The config file name.
        :return: An instance of ParameterForm.
        """
        if filtered_keys:
            field_args = {"include_param_key": filtered_keys}
        else:
            field_args = None
        form = ParameterForm(
            model_config=self.model_config(config_file),
            parameter_obj=ParameterConfig({}),
            available_fields={
                "Section": [
                    {
                        "name": "type",
                        "field_type": ModelParameterPickerWidget,
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

    def test_empty_model_parameter(self, qtbot):
        """
        Tests the widget when the model does not contain any parameters.
        :return:
        """
        form = self.form(
            value=None,
            filtered_keys=None,
            config_file="test_coordinates.json",
        )
        model_params_field = form.find_field_by_name("type")
        # noinspection PyTypeChecker
        model_params_widget: ModelParameterPickerWidget = (
            model_params_field.widget
        )
        assert "no parameters available" in model_params_field.message.text()
        assert len(model_params_widget.combo_box.all_items) == 1

    @pytest.mark.parametrize(
        "param_name, filtered_keys, total_params",
        [
            # all parameter types are allowed
            ("constant_param", None, 4),
            # parameter name is not provided. Default set to None
            (None, None, 4),
            # only monthly profile is allowed
            ("monthly_param", ["monthlyprofile"], 1),
            # only some profiles are allowed
            ("monthly_param", ["monthlyprofile", "weeklyprofile"], 2),
            # custom parameter with and without filter
            ("custom_param", None, 4),
            ("custom_param", ["my", "aggregatedindex"], 1),
        ],
    )
    def test_valid_param_types(
        self, qtbot, param_name, filtered_keys, total_params
    ):
        """
        Tests the widget when a valid parameter name is used.
        """
        form = self.form(param_name, filtered_keys)
        model_params_field = form.find_field_by_name("type")
        # noinspection PyTypeChecker
        model_params_widget: ModelParameterPickerWidget = (
            model_params_field.widget
        )

        assert model_params_field.message.text() == ""
        out = model_params_widget.validate(
            "name", "Name", model_params_widget.combo_box.currentText()
        )
        if param_name is not None:
            assert model_params_widget.combo_box.currentText() == param_name
            # name is in the ComboBox
            assert param_name in model_params_widget.combo_box.all_items
            assert out.validation is True
        # no parameter is selected
        else:
            assert model_params_widget.combo_box.currentText() == "None"
            assert out.validation is False

        # check total elements in widget
        assert len(model_params_widget.combo_box.all_items) == total_params + 1

    @pytest.mark.parametrize(
        "param_name, filtered_keys, message, total_params",
        [
            # only constant is allowed, but monthly profile is set
            ("monthly_param", ["constant"], "is not allowed", 1),
            # constant is set but only profiles are allowed
            (
                "constant_param",
                ["weeklyprofile", "dailyprofile", "monthlyprofile"],
                "is not allowed",
                2,
            ),
            # non existing name
            ("non_existing_name", None, "does not exist", 4),
            # custom parameter with filter
            ("custom_param", ["constant"], "is not allowed", 1),
            # selected parameter has invalid type (not str)
            (123, None, "must be a string", 4),
        ],
    )
    def test_invalid_param(
        self, qtbot, param_name, filtered_keys, message, total_params
    ):
        """
        Tests the widget when the provided parameter name is not valid (only certain
        parameter types are allowed or the parameter does not exist).
        """
        form = self.form(param_name, filtered_keys)
        model_params_field = form.find_field_by_name("type")
        # noinspection PyTypeChecker
        model_params_widget: ModelParameterPickerWidget = (
            model_params_field.widget
        )

        assert message in model_params_field.message.text()
        out = model_params_widget.validate(
            "name", "Name", model_params_widget.combo_box.currentText()
        )
        assert out.validation is False

        # check ComboBox
        assert model_params_widget.combo_box.currentText() == "None"
        assert param_name not in model_params_widget.combo_box.all_items
        assert len(model_params_widget.combo_box.all_items) == total_params + 1
