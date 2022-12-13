import pytest
from pywr_editor.model import ModelConfig, ParameterConfig, RecorderConfig
from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import (
    RecorderPageWidget,
)
from tests.utils import resolve_model_path


class TestEventRecorderTypeWidget:
    """
    Tests the EventRecorderTypeWidget.
    """

    model_file = resolve_model_path(
        "model_dialog_recorders_event_recorder_type_widget.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "recorder_name, selected_type, init_message",
        [
            # valid
            ("valid_empty", "parameter", None),
            ("valid_parameter_str", "parameter", None),
            ("valid_parameter_number", "parameter", None),
            ("valid_parameter_dict", "parameter", None),
            ("valid_parameter_custom_param", "parameter", None),
            ("valid_recorder_str", "recorder", None),
            ("valid_recorder_dict", "recorder", None),
            # invalid string
            (
                "invalid_comp_str",
                "parameter",  # default type
                "is not a model parameter or recorder",
            ),
            (
                "invalid_comp_dict",
                "parameter",  # default type
                "model component type is not a valid model parameter",
            ),
        ],
    )
    def test_widget(
        self,
        qtbot,
        model_config,
        recorder_name,
        selected_type,
        init_message,
    ):
        """
        Tests that the value is loaded correctly.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        comp_type_field = form.find_field_by_name("threshold_type")
        parameter_field = form.find_field_by_name("threshold_parameter")
        recorder_field = form.find_field_by_name("threshold_recorder")

        assert form.find_field_by_name("name").value() == recorder_name

        # 1. Check selected value in combobox
        assert comp_type_field.value() == selected_type

        # 2. Check field visibility
        assert parameter_field.isVisible() == (selected_type == "parameter")
        assert recorder_field.isVisible() == (selected_type == "recorder")

        # 3. Check field values
        # one widget is reset and only one has a value, when the passed value is valid
        if init_message is not None or recorder_name == "valid_empty":
            assert parameter_field.widget.component_obj is None
            assert recorder_field.widget.component_obj is None
        elif selected_type == "parameter":
            assert isinstance(
                parameter_field.widget.component_obj, ParameterConfig
            )
            assert recorder_field.widget.component_obj is None
        elif selected_type == "recorder":
            assert parameter_field.widget.component_obj is None
            assert isinstance(
                recorder_field.widget.component_obj, RecorderConfig
            )

        # 4. Check warning messages
        if init_message is None:
            assert comp_type_field.message.text() == ""
        else:
            assert init_message in comp_type_field.message.text()

        # 5. Set the component when the form is empty and test the
        # after_validate method
        if recorder_name == "valid_empty":
            # set a parameter
            parameter_field.widget.component_obj = ParameterConfig(
                {
                    "type": "constant",
                    "value": -99,
                }
            )
            assert form.validate() == {
                "name": recorder_name,
                "type": "event",
                "threshold": -99,
            }

    @pytest.mark.parametrize(
        "recorder_name, expected_agg_func",
        [
            ("recorder_agg_func_provided", "min"),
            ("recorder_agg_func_disabled", None),
            ("agg_func_provided", "max"),
            ("both_agg_funcs_provided", "min"),
        ],
    )
    def test_recorder_agg_func(
        self, qtbot, model_config, recorder_name, expected_agg_func
    ):
        """
        Checks that the EventAggFuncWidget correctly loads the stored value.
        The widget uses the values of the "agg_func" key if the "event_agg_func"
        value is empty and "agg_func" is provided.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        event_agg_func_field = form.find_field_by_name("event_agg_func")

        assert form.find_field_by_name("name").value() == recorder_name
        assert event_agg_func_field.value() == expected_agg_func
