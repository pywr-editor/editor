from pywr_editor.form import AbstractFloatListWidget, FormField


class RbfOptBoundWidget(AbstractFloatListWidget):
    def __init__(
        self,
        name: str,
        value: str | list[str] | None,
        parent: FormField,
    ):
        """
        Initialises the widget to handle the "lower_bounds" and "upper_bounds fields
        for a Rbf profile parameter.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        super().__init__(
            name=name,
            value=value,
            log_name=self.__class__.__name__,
            parent=parent,
        )
