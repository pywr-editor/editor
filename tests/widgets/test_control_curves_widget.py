import pytest
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import ControlCurvesWidget, FormField, ParameterForm
from pywr_editor.model import ModelConfig, ParameterConfig


class TestDialogParameterControlCurvesWidget:
    """
    Tests the ControlCurvesWidget.
    """

    @staticmethod
    def widget(
        value: list[int | float] | dict | None,
    ) -> ControlCurvesWidget:
        """
        Initialises the form and returns the widget.
        :param value: The widget value.
        :return: An instance of InterpFillValueWidget.
        """
        # mock widgets
        form = ParameterForm(
            model_config=ModelConfig(),
            parameter_obj=ParameterConfig({}),
            fields={
                "Section": [
                    {
                        "name": "control_curves",
                        "field_type": ControlCurvesWidget,
                        "value": value,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()

        form_field = form.find_field("control_curves")
        # noinspection PyTypeChecker
        return form_field.widget

    @pytest.mark.parametrize(
        "value_dict",
        [
            # one curve
            {
                "control_curve": {"type": "constant", "value": 27},
                "control_curves": None,
            },
            # a list of curves
            {
                "control_curve": None,
                "control_curves": [
                    {"type": "constant", "value": 27},
                    {"type": "monthlyprofile", "values": list(range(1, 13))},
                ],
            },
        ],
    )
    def test_valid(self, qtbot, value_dict):
        """
        Tests that the input data are converted correctly depending on the set key.
        Checks also that the parent widget always gets a list of parameters.
        """
        widget = self.widget(
            value=value_dict,
        )
        form_field: FormField = widget.field

        if value_dict["control_curve"] is not None:
            expected_value = [value_dict["control_curve"]]
        else:
            expected_value = value_dict["control_curves"]

        assert widget.get_value() == expected_value
        assert form_field.message.text() == ""
