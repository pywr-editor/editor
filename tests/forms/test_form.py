import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout

from pywr_editor.form import (
    BooleanWidget,
    FieldConfig,
    Form,
    FormCustomWidget,
    FormField,
    Validation,
)
from tests.utils import close_message_box


@pytest.fixture
def window() -> QWindow:
    """
    Initialises the window.
    :return: The QWindow instance.
    """
    QTimer.singleShot(100, close_message_box)
    app = QApplication()
    return QWindow(app)


def test_save(qtbot):
    """
    Checks that the values are saved correctly.
    """
    form = Form(
        {
            "Section": [
                FieldConfig(
                    name="fruit",
                    value="Apple",
                ),
                FieldConfig(
                    name="Vegetable",
                    value="Carrot",
                ),
                FieldConfig(
                    name="Tool",
                    value=False,
                    field_type=BooleanWidget,
                ),
            ],
        }
    )
    form.load_fields()
    qtbot.addWidget(form)

    assert form.validate() == {
        "fruit": "Apple",
        "Vegetable": "Carrot",
        "Tool": False,
    }


def test_default_value(qtbot):
    """
    Checks that the value of a field is not exported/saved if it equals the
    default value.
    """
    form = Form(
        {
            "Section": [
                FieldConfig(
                    name="fruit",
                    value="Apple",
                    help_text="Field 1",
                    default_value="Apple",
                ),
                FieldConfig(
                    name="Vegetable",
                    value="Carrot",
                    default_value="Onion",
                ),
                FieldConfig(
                    name="Tool",
                    value=False,
                    default_value=False,
                    field_type=BooleanWidget,
                ),
            ],
        }
    )
    form.load_fields()
    qtbot.addWidget(form)

    assert form.validate() == {
        "Vegetable": "Carrot",
    }


def test_boolean_value(qtbot):
    """
    Checks that the value of a QComboBox are properly set and exported
    """
    form = Form(
        {
            "Section": [
                FieldConfig(name="Fruit", value=True, field_type=BooleanWidget),
                FieldConfig(name="Vegetable", value=False, field_type=BooleanWidget),
                FieldConfig(
                    name="Sweet",
                    default_value=True,
                    value=None,
                    field_type=BooleanWidget,
                ),
            ],
        }
    )
    form.load_fields()
    qtbot.addWidget(form)

    # sweet omitted because value is default
    assert form.validate() == {"Fruit": True, "Vegetable": False}

    # change one field
    for child in form.sections["Section"].findChildren(FormField):
        toggle = child.widget.toggle
        if child.objectName() in ["Fruit", "Sweet"]:
            assert toggle.text() == "Yes"
            assert toggle.checkState() == Qt.Checked
            # change status (show form to register click)
            form.show()
            qtbot.mouseClick(toggle, Qt.MouseButton.LeftButton)
            assert toggle.text() == "No"
            assert toggle.checkState() == Qt.Unchecked
        else:
            assert toggle.text() == "No"
            assert toggle.checkState() == Qt.Unchecked

    assert form.validate() == {
        "Fruit": False,
        "Vegetable": False,
        "Sweet": False,
    }


def test_allow_empty_check(qtbot):
    """
    Checks that the "allow_empty" validation check works.
    """
    form = Form(
        {
            "Section": [
                FieldConfig(name="Fruit", value="Apple", allow_empty=True),
                FieldConfig(
                    name="Vegetable", value="", allow_empty=False, default_value=None
                ),
            ],
        }
    )
    form.load_fields()
    form.find_field("Vegetable").widget.line_edit.setText("")
    qtbot.addWidget(form)

    QTimer.singleShot(100, close_message_box)
    assert form.validate() is False


def test_validate_fun_option(qtbot):
    """
    Checks that the "validate_fun" option check works.
    """

    def validate_fun(name: str, label: str, value: str) -> Validation:
        if value != "Apple":
            return Validation(
                error_message=f"{label} must be Apple instead of {name}",
            )
        return Validation()

    form = Form(
        {
            "Section": [
                FieldConfig(name="Fruit", value="Orange", validate_fun=validate_fun),
            ]
        }
    )
    form.load_fields()
    qtbot.addWidget(form)

    QTimer.singleShot(100, close_message_box)
    assert form.validate() is False

    form = Form(
        {
            "Section": [
                FieldConfig(name="Fruit", value="Apple", validate_fun=validate_fun),
            ]
        }
    )
    form.load_fields()
    qtbot.addWidget(form)

    assert form.validate() == {"Fruit": "Apple"}


def test_custom_widget(qtbot):
    """
    Checks that the "widget" option works.
    """

    class CustomWidget(FormCustomWidget):
        def __init__(self, name, value, parent=None):
            super().__init__(name, value, parent)
            layout = QVBoxLayout(self)
            self.widget = QTextEdit(value)
            layout.addWidget(self.widget)

        def get_value(self) -> str:
            return self.widget.toPlainText()

    form = Form(
        {
            "Section": [
                FieldConfig(name="Custom field", value="XX", field_type=CustomWidget),
            ]
        }
    )
    form.load_fields()
    qtbot.addWidget(form)

    assert form.validate() == {"Custom field": "XX"}
