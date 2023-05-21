import pytest
from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget

from pywr_editor.form import FormField, InterpFillValueWidget, ParameterForm
from pywr_editor.model import ModelConfig, ParameterConfig


class TestDialogParameterInterpFillValueWidget:
    """
    Tests the InterpFillValueWidget.
    """

    @staticmethod
    def widget(
        value: list[int | float] | int | float | str | None,
    ) -> InterpFillValueWidget:
        """
        Initialises the form and returns the widget.
        :param value: A dictionary containing the variable names as key and their
        values as values.
        :return: An instance of InterpFillValueWidget.
        """
        # mock widgets
        form = ParameterForm(
            model_config=ModelConfig(),
            parameter_obj=ParameterConfig({}),
            available_fields={
                "Section": [
                    {
                        "name": "fill_value",
                        "field_type": InterpFillValueWidget,
                        "value": value,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()

        fill_value_field = form.find_field_by_name("fill_value")
        # noinspection PyTypeChecker
        return fill_value_field.widget

    @pytest.mark.parametrize(
        "value, combo_box_key, final_value",
        [
            # number converted to list
            (1, "fill", [1, 1]),
            ([872, 123], "fill", [872, 123]),
            ("extrapolate", "extrapolate", "extrapolate"),
            # default to no extrapolation (None)
            (None, "no_extrapolation", None),
            # empty string equates to None
            ("", "no_extrapolation", None),
        ],
    )
    def test_valid(self, qtbot, value, combo_box_key, final_value):
        """
        Tests that the field is loaded correctly.
        """
        fill_value_widget = self.widget(
            value=value,
        )
        fill_value_field: FormField = fill_value_widget.form_field

        # register app to test field visibility
        app = QMainWindow()
        app.setCentralWidget(fill_value_widget)
        qtbot.addWidget(app)
        app.show()
        qtbot.waitForWindowShown(app)

        # 1. Check field
        assert fill_value_field.message.text() == ""
        assert (
            fill_value_widget.combo_box.currentText()
            == fill_value_widget.labels_map[combo_box_key]
        )
        assert fill_value_widget.get_value() == final_value

        # 2. Check QLineEdit
        line_edit = fill_value_widget.line_edit
        if combo_box_key == "fill":
            list_to_str = list(map(float, final_value))
            list_to_str = list(map(str, list_to_str))
            list_to_str = ", ".join(list_to_str)
            assert line_edit.text() == list_to_str
            assert line_edit.isVisible() is True
        else:
            assert line_edit.isVisible() is False

        # 3. Validation
        out = fill_value_widget.validate("", "", fill_value_widget.get_value())
        assert out.validation is True

        # 4. Test reset
        fill_value_widget.reset()
        assert line_edit.text() == ""
        assert (
            fill_value_widget.combo_box.currentText()
            == fill_value_widget.labels_map["no_extrapolation"]
        )

    @pytest.mark.parametrize(
        "value, expected_value, combo_box_key, init_message",
        [
            # empty string defaults to no extrapolation
            ("a", "extrapolate", "extrapolate", "is not valid"),
            # default to fill if type is wrong
            (False, None, "fill", "is not valid"),
            # invalid size
            ([1], None, "fill", "1 value was given"),
            ([1, 2, 4], None, "fill", "3 values were given"),
        ],
    )
    def test_invalid(self, qtbot, value, expected_value, combo_box_key, init_message):
        """
        Tests that the form displays a warning message when the provided value is
        invalid.
        """
        fill_value_widget = self.widget(
            value=value,
        )
        fill_value_field: FormField = fill_value_widget.form_field

        # register app to test field visibility
        app = QMainWindow()
        app.setCentralWidget(fill_value_widget)
        qtbot.addWidget(app)
        app.show()
        qtbot.waitForWindowShown(app)

        # 1. Check field
        assert init_message in fill_value_field.message.text()
        assert (
            fill_value_widget.combo_box.currentText()
            == fill_value_widget.labels_map[combo_box_key]
        )
        assert fill_value_widget.get_value() == expected_value

        # 2. Check QLineEdit
        line_edit = fill_value_widget.line_edit
        if combo_box_key == "fill":
            assert line_edit.text() == ""
            assert line_edit.isVisible() is True
        else:
            assert line_edit.isVisible() is False

        # 3. Validation
        out = fill_value_widget.validate("", "", fill_value_widget.get_value())
        if combo_box_key == "fill":
            assert out.validation is False
        else:
            assert out.validation is True

        # 4. When "fill", empty QLineEdit and validate again
        if combo_box_key == "fill":
            line_edit.setText("")
            out = fill_value_widget.validate("", "", fill_value_widget.get_value())
            assert "must provide a value" in out.error_message
            assert out.validation is False
