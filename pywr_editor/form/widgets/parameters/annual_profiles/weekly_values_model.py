from pywr_editor.form import AbstractAnnualValuesModel


class WeeklyValuesModel(AbstractAnnualValuesModel):
    def __init__(
        self,
        values: list[float | int] = None,
    ):
        """
        Initialises the model.
        :param values: The list of values.
        """
        super().__init__(
            label="Week",
            values=values,
        )
