from pywr_editor.form import AbstractColumnsSelectorWidget, FormField


class IndexColWidget(AbstractColumnsSelectorWidget):
    def __init__(self, name: str, value: str | int | list, parent: FormField):
        """
        Initialises the widget.
        :param name: The widget name.
        :param value: The widget value.
        :param parent: The widget parent.
        """
        super().__init__(
            name,
            value,
            parent,
            is_index_selector=True,
            log_name=self.__class__.__name__,
        )
