import pytest
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import FileBrowserWidget, RecorderForm
from pywr_editor.model import ModelConfig, RecorderConfig
from tests.utils import resolve_model_path


class TestFileBrowserWidget:
    """
    Tests the FileBrowserWidget.
    """

    @staticmethod
    def widget(
        value: str | None,
    ) -> FileBrowserWidget:
        """
        Initialises the form and returns the widget.
        :param value: The dictionary containing the set file path.
        :return: An instance of FileBrowserWidget.
        """
        # mock widgets
        form = RecorderForm(
            model_config=ModelConfig(resolve_model_path("model_tables.json")),
            recorder_obj=RecorderConfig({}),
            fields={
                "Section": [
                    {
                        "name": "url",
                        "field_type": FileBrowserWidget,
                        "field_args": {"file_extension": "csv"},
                        "value": value,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.load_fields()

        form_field = form.find_field("url")
        return form_field.widget

    @pytest.mark.parametrize(
        "value, expected_value, init_message, validation_message",
        [
            (
                "json_models/files/table.csv",
                "json_models/files/table.csv",
                None,
                None,
            ),
            # not set
            ("", None, None, "must provide a file path"),
            (None, None, None, "must provide a file path"),
            # not a string
            (1, None, "must be a valid string", "must provide a file path"),
            # wrong extension
            (
                "json_models/files/table.txt",
                "json_models/files/table.txt",
                "file extension must be CSV",
                "file extension must be CSV",
            ),
        ],
    )
    def test_widget(
        self, qtbot, value, expected_value, init_message, validation_message
    ):
        """
        Tests that the field is loaded correctly and warning messages at init
        or during form validation are shown.
        """
        widget = self.widget(value=value)
        form_field = widget.field

        # 1. Check field
        assert widget.get_value() == expected_value

        if init_message is None:
            assert form_field.message.text() == ""

        # 2. Validation
        out = widget.validate("", "", widget.get_value())
        if validation_message is None:
            assert out.validation is True
        else:
            assert validation_message in out.error_message

        # 3. Test reset
        widget.reset()
        assert widget.line_edit.text() == ""
