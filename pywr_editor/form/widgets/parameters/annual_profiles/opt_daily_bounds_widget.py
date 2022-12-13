from pywr_editor.form import FormField, AbstractFloatListWidget


class OptDailyBoundsWidget(AbstractFloatListWidget):
    def __init__(
        self,
        name: str,
        value: str | list[str] | None,
        parent: FormField,
    ):
        """
        Initialises the widget to handle the lower and upper bounds of an optimisation
        problem for a daily profile.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        super().__init__(
            name=name,
            value=value,
            log_name=self.__class__.__name__,
            items_count=366,
            parent=parent,
        )
