from pywr_editor.form import AbstractFloatListWidget, FormField


class RbfDayOfYearWidget(AbstractFloatListWidget):
    def __init__(
        self,
        name: str,
        value: str | list[str] | None,
        parent: FormField,
    ):
        """
        Initialises the widget to handle the "day_of_year" field for a Rbf profile
        parameter.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        super().__init__(
            name=name,
            value=value,
            # only list of ints is allowed
            only_list=True,
            allowed_item_types=int,
            final_type=int,
            allowed_empty=False,
            log_name=self.__class__.__name__,
            parent=parent,
        )
