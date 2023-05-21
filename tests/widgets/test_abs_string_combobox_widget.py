import pytest
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import AbstractStringComboBoxWidget, FormField, ParameterForm
from pywr_editor.model import ModelConfig, ParameterConfig

default_labels_map = {"apple": "Apple", "cider": "Cider", "pear": "Pear"}


class TestAbstractStringComboBoxWidget:
    """
    Tests the AbstractStringComboBoxWidget.
    """

    @staticmethod
    def widget(
        labels_map: dict[str, str],
        default_value: str,
        value: str | None,
        keep_default: bool = True,
    ) -> AbstractStringComboBoxWidget:
        """
        Initialises the form and returns the widget.
        :param labels_map: A dictionary containing the values as keys and their
        labels as values.
        :param default_value: The default string.
        :param value: A dictionary containing the variable names as key and their
        values as values.
        :param keep_default: Return None if the value matches the default option.
        Default to False.
        :return: An instance of ParameterForm.
        """
        form = ParameterForm(
            model_config=ModelConfig(),
            parameter_obj=ParameterConfig({}),
            available_fields={
                "Section": [
                    {
                        "name": "options",
                        "field_type": AbstractStringComboBoxWidget,
                        # mock the widget
                        "field_args": {
                            "labels_map": labels_map,
                            "default_value": default_value,
                            "keep_default": keep_default,
                            "log_name": "widget",
                        },
                        "value": value,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()

        form_field = form.find_field_by_name("options")
        return form_field.widget

    @pytest.mark.parametrize(
        "labels_map, default_value, keep_default, selected",
        [
            (
                default_labels_map,
                "pear",
                True,
                "cider",
            ),
            (
                default_labels_map,
                "pear",
                True,
                "Cider",
            ),
            (
                default_labels_map,
                "pear",
                True,
                "CiDeR",
            ),
            # selected is None or empty string
            (
                default_labels_map,
                "pear",
                True,
                None,
            ),
            (
                default_labels_map,
                "pear",
                False,
                "pear",
            ),
        ],
    )
    def test_valid(self, qtbot, labels_map, default_value, keep_default, selected):
        """
        Tests that the field is loaded correctly.
        """
        widget = self.widget(
            value=selected,
            labels_map=labels_map,
            default_value=default_value,
            keep_default=keep_default,
        )
        form_field: FormField = widget.form_field

        assert form_field.message.text() == ""

        # 1. Check widget values
        assert widget.combo_box.all_items == list(labels_map.values())
        if selected:
            assert widget.combo_box.currentText() == selected.title()
            if selected == default_value and not keep_default:
                assert widget.get_value() is None
            else:
                assert widget.get_value() == selected.lower()
        # selected is None
        else:
            assert widget.combo_box.currentText() == default_value.title()
            if selected == default_value and not keep_default:
                assert widget.get_value() is None
            else:
                assert widget.get_value() == default_value

        # 2. Test reset
        widget.reset()
        if selected == default_value and not keep_default:
            assert widget.get_value() is None
        else:
            assert widget.get_value() == default_value

    @pytest.mark.parametrize(
        "labels_map, default_value, selected, message",
        [
            # invalid type
            (default_labels_map, "pear", 1, "is not a valid type"),
            # option not available
            (default_labels_map, "pear", "orange", "does not exist"),
            (
                default_labels_map,
                "pear",
                "",
                "is not a valid type",
            ),
        ],
    )
    def test_invalid(self, qtbot, labels_map, default_value, selected, message):
        """
        Tests that the form displays a warning message when the provided value is
        invalid.
        """
        widget = self.widget(
            value=selected, labels_map=labels_map, default_value=default_value
        )
        form_field: FormField = widget.form_field

        assert message in form_field.message.text()
        # default value is selected
        assert widget.combo_box.currentText() == default_value.title()
        assert widget.get_value() == default_value
