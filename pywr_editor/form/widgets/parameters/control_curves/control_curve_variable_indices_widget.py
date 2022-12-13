from pywr_editor.form import AbstractFloatListWidget, FormField


class ControlCurveVariableIndicesWidget(AbstractFloatListWidget):
    def __init__(
        self,
        name: str,
        value: list[int] | None,
        parent: FormField,
    ):
        """
        Initialises the widget to handle the variable_indices field of an optimisation
        problem for a control curve parameter.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        super().__init__(
            name=name,
            value=value,
            log_name=self.__class__.__name__,
            only_list=True,
            allowed_item_types=int,
            final_type=int,
            parent=parent,
        )
