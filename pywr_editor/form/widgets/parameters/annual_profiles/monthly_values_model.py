import calendar
from pywr_editor.form import AbstractAnnualValuesModel


class MonthlyValuesModel(AbstractAnnualValuesModel):
    def __init__(
        self,
        values: list[float | int] = None,
    ):
        """
        Initialises the model.
        :param values: The list of values.
        """
        super().__init__(
            label="Month",
            label_values=list(calendar.month_name)[1:],
            values=values,
        )
