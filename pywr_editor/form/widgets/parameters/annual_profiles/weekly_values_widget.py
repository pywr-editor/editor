from pywr_editor.form import (
    AbstractAnnualValuesWidget,
    ChartOptions,
    FormField,
    WeeklyValuesModel,
)


class WeeklyValuesWidget(AbstractAnnualValuesWidget):
    total_values: int = 52

    def __init__(
        self,
        name: str,
        value: list[int | float] | None,
        parent: FormField,
    ):
        """
        Initialises the widget for a weekly profile parameter. The value can only
        be a list of floats or integers.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        # noinspection PyTypeChecker
        super().__init__(
            name=name,
            value=value,
            model=WeeklyValuesModel,
            log_name=self.__class__.__name__,
            parent=parent,
        )

        self.chart_options = ChartOptions(
            y_label=self.model.label,
            step_mode=True,
            x_tick_spacing=[4, 2],
        )
