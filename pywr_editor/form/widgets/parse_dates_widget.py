from pywr_editor.form import AbstractColumnsSelectorWidget, FormField


class ParseDatesWidget(AbstractColumnsSelectorWidget):
    def __init__(self, name: str, value: dict, parent: FormField):
        """
        Initialises the widget.
        :param name: The widget name.
        :param value: The widget value. This is a dictionary containing the value of
        the "parse_dates" and "index_col" keys.
        :param parent: The widget parent.
        """
        if not isinstance(value, dict):
            raise TypeError("The value must be a dictionary")

        if "parse_dates" not in value.keys():
            raise KeyError("The value dictionary must contain the 'parse_dates' key")

        if "index_col" not in value.keys():
            raise KeyError("The value dictionary must contain the 'index_col' key")

        # when parse_dates is True, Pandas will parse dates the index
        if value["parse_dates"] is True:
            new_value = value["index_col"]
        else:
            new_value = value["parse_dates"]

        super().__init__(
            name,
            new_value,
            parent,
            is_index_selector=False,
            log_name=self.__class__.__name__,
        )
