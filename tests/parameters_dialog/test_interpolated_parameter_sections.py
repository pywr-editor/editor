from random import random

from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.dialogs.parameters.sections.interpolated_parameter_section import (
    InterpolatedParameterSection,
)
from pywr_editor.form import ParameterForm, ParameterLineEditWidget, TableValuesWidget
from pywr_editor.model import ModelConfig, ParameterConfig


class TestDialogInterpolatedParameterSection:
    """
    Tests the sections for the InterpolatedParameter section.
    """

    @staticmethod
    def form() -> ParameterForm:
        """
        Initialises the form and section.
        :return: An instance of ParameterForm.
        """
        form = ParameterForm(
            model_config=ModelConfig(),
            parameter_obj=ParameterConfig({}),
            fields={},
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.add_section_from_class(InterpolatedParameterSection, {})
        form.enable_optimisation_section = False
        form.load_fields()

        return form

    def test_filter(self, qtbot):
        """
        Tests that the section filter.
        """
        form = self.form()
        xy_values_field = form.find_field("x_y_values")
        # noinspection PyTypeChecker
        xy_values_widget: TableValuesWidget = xy_values_field.widget

        # mock value insertion by manipulating the model
        values = [
            [random() for _ in range(0, 6)],
            [random() for _ in range(0, 6)],
        ]
        xy_values_widget.model.values = values

        assert xy_values_widget.get_value() == {"x": values[0], "y": values[1]}

        # add the parameter
        parameter_field = form.find_field("parameter")
        parameter_widget: ParameterLineEditWidget = parameter_field.widget
        parameter_widget.component_obj = ParameterConfig(
            {"type": "constant", "value": -999}
        )

        # validate to apply section filter
        form_data = form.validate()
        assert form_data["x"] == values[0]
        assert form_data["y"] == values[1]
        assert "x_y_values" not in form_data
