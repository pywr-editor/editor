from typing import Any

import pytest

from pywr_editor.form import AbstractFloatListWidget, Form, FormField


class OnlyListFloatIntWidget(AbstractFloatListWidget):
    def __init__(self, name, value, parent=None):
        super().__init__(
            name=name,
            value=value,
            items_count=None,
            allowed_item_types=(float, int),
            only_list=True,
            final_type=float,
            allowed_empty=True,
            parent=parent,
        )


class OnlyListIntWidget(AbstractFloatListWidget):
    def __init__(self, name, value, parent=None):
        super().__init__(
            name=name,
            value=value,
            items_count=None,
            allowed_item_types=int,
            only_list=True,
            final_type=int,
            allowed_empty=True,
            parent=parent,
        )


class OnlyListNotEmptyWidget(AbstractFloatListWidget):
    def __init__(self, name, value, parent=None):
        super().__init__(
            name=name,
            value=value,
            items_count=None,
            allowed_item_types=(float, int),
            only_list=True,
            final_type=float,
            allowed_empty=False,
            parent=parent,
        )


class NotEmptyWidget(AbstractFloatListWidget):
    def __init__(self, name, value, parent=None):
        super().__init__(
            name=name,
            value=value,
            items_count=None,
            allowed_item_types=(float, int),
            only_list=False,
            final_type=float,
            allowed_empty=False,
            parent=parent,
        )


class MaxLengthWidget(AbstractFloatListWidget):
    def __init__(self, name, value, parent=None):
        super().__init__(
            name=name,
            value=value,
            items_count=5,
            allowed_item_types=(float, int),
            only_list=False,
            final_type=float,
            allowed_empty=False,
            parent=parent,
        )


# noinspection PyTypeChecker
class TestDialogParameterFloatListWidget:
    """
    Tests the AbstractFloatListWidget.
    """

    key = "test_key"

    @staticmethod
    def form(widget: AbstractFloatListWidget, value: Any) -> Form:
        form = Form(
            {
                "Section": [
                    {
                        "name": TestDialogParameterFloatListWidget.key,
                        "field_type": widget,
                        "value": value,
                    }
                ]
            }
        )
        form.load_fields()
        return form

    @pytest.mark.parametrize(
        "values, value_types, message",
        [
            # valid data
            ([1.0, 2, 3], float, None),
            (3, float, None),
            # value is empty but still valid
            ([], float, None),
            (None, float, None),
            # invalid data
            (False, float, "is not valid"),
            (True, float, "is not valid"),
            ([1.0, "a", 3], float, "must be all valid numbers"),
        ],
    )
    def test_default_widget_attrs(self, qtbot, values, value_types, message):
        """
        Tests the widget with the default class attributes.
        """
        form = self.form(AbstractFloatListWidget, values)
        form_field: FormField = form.find_field(self.key)
        widget: AbstractFloatListWidget = form_field.widget
        warning_message = form_field.message.text()
        if message is None:
            assert warning_message == ""
            if not values:
                assert widget.get_value() is widget.get_default_value()
            else:
                assert widget.get_value() == values
                if isinstance(values, list):
                    assert all([isinstance(v, value_types) for v in widget.get_value()])
                else:
                    assert isinstance(widget.get_value(), value_types)
        else:
            assert message in warning_message
            assert widget.get_value() == widget.get_default_value()

    @pytest.mark.parametrize(
        "values, value_types, message",
        [
            # valid data
            ([1.0, 2, 3], float, None),
            # value is empty but still valid
            ([], float, None),
            (None, float, None),
            # invalid data
            ([1.0, "a", 3], float, "must be all valid numbers"),
            (3, float, "is not valid"),
        ],
    )
    def test_only_list_float_int(self, qtbot, values, value_types, message):
        """
        Tests the widget when only_list is True and allowed_item_types is (float, int).
        """
        form = self.form(OnlyListFloatIntWidget, values)
        form_field: FormField = form.find_field(self.key)
        widget: AbstractFloatListWidget = form_field.widget
        warning_message = form_field.message.text()
        if message is None:
            assert warning_message == ""
            if not values:
                assert widget.get_value() is widget.get_default_value()
            else:
                assert widget.get_value() == values
                assert all([isinstance(v, value_types) for v in widget.get_value()])
        else:
            assert message in warning_message
            assert widget.get_value() == widget.get_default_value()

    @pytest.mark.parametrize(
        "values, value_types, message",
        [
            # valid data
            ([1, 2, 3], int, None),
            # invalid data
            ([1.0, 3.1, 4.5], int, "must be all valid numbers"),
            (3, int, "is not valid"),
        ],
    )
    def test_only_list_int(self, qtbot, values, value_types, message):
        """
        Tests the widget when only_list is True and allowed_item_types is int.
        """
        form = self.form(OnlyListIntWidget, values)
        form_field: FormField = form.find_field(self.key)
        widget: AbstractFloatListWidget = form_field.widget
        warning_message = form_field.message.text()
        if message is None:
            assert warning_message == ""
            if not values:
                assert widget.get_value() is widget.get_default_value()
            else:
                assert widget.get_value() == values
                assert all([isinstance(v, value_types) for v in widget.get_value()])
        else:
            assert message in warning_message
            assert widget.get_value() == widget.get_default_value()

    @pytest.mark.parametrize(
        "values, message",
        [
            # valid data
            ([1, 2, 3], None),
            # valid data - list is always return even without commas
            ([1], None),
            (None, None),
            # invalid data
            ([], "The number of values"),
        ],
    )
    def test_only_list_not_empty(self, qtbot, values, message):
        """
        Tests the widget when only_list is True and allowed_empty is False.
        """
        form = self.form(OnlyListNotEmptyWidget, values)
        form_field: FormField = form.find_field(self.key)
        widget: AbstractFloatListWidget = form_field.widget
        warning_message = form_field.message.text()

        if message is None:
            assert warning_message == ""
            if not values:
                assert widget.get_value() is widget.get_default_value()
            else:
                assert widget.get_value() == values
        else:
            assert message in warning_message
            assert widget.get_value() == widget.get_default_value()

    @pytest.mark.parametrize(
        "values, message",
        [
            # valid data
            ([1, 2, 3, 4, 5], None),
            (None, None),
            # invalid data
            ([], "The number of values"),
            ([1, 2, 3], "The number of values"),
        ],
    )
    def test_max_length(self, qtbot, values, message):
        """
        Tests the widget when only_list is True and allowed_empty is False.
        """
        form = self.form(MaxLengthWidget, values)
        form_field: FormField = form.find_field(self.key)
        widget: AbstractFloatListWidget = form_field.widget
        warning_message = form_field.message.text()

        if message is None:
            assert warning_message == ""
            if not values:
                assert widget.get_value() is widget.get_default_value()
            else:
                assert widget.get_value() == values
        else:
            assert message in warning_message
            assert widget.get_value() == widget.get_default_value()

    @pytest.mark.parametrize(
        "widget, init_values, new_values, message",
        [
            # 1. successful validation
            (AbstractFloatListWidget, 3.0, "5", None),
            (AbstractFloatListWidget, 3.0, "5, 9.8, 2", None),
            # empty field allowed
            (AbstractFloatListWidget, 3.0, "", None),
            # correct length
            (MaxLengthWidget, [1, 2, 3, 4, 5], "6, 7, 8, 9, 10", None),
            # 2. failed validation
            # invalid type
            (AbstractFloatListWidget, 3.0, "wrong", "must be a valid number"),
            # invalid types
            (
                AbstractFloatListWidget,
                3.0,
                "wrong, 2",
                "must contain valid numbers",
            ),
            (
                AbstractFloatListWidget,
                3.0,
                ",,,,,,,,,,,",
                "must contain valid numbers",
            ),
            # wrong length
            (
                MaxLengthWidget,
                [1, 2, 3, 4, 5],
                "6, 9, 10",
                "must contains 5 values",
            ),
            # empty field, but list is required
            (
                OnlyListNotEmptyWidget,
                [1.0, 2.0],
                "",
                "You must provide a value",
            ),
            # value is required
            (
                NotEmptyWidget,
                [1.0, 2.0],
                "",
                "You must provide a value",
            ),
        ],
    )
    def test_validation(self, qtbot, widget, init_values, new_values, message):
        """
        Tests the widget validation.
        """
        form = self.form(widget, init_values)
        form_field: FormField = form.find_field(self.key)
        widget: AbstractFloatListWidget = form_field.widget
        widget.line_edit.setText(new_values)

        # close warning message if validation fails
        output = widget.validate("", "", "")
        if message is not None:
            assert output.validation is False
            assert message in output.error_message
        else:
            assert output.validation is True
