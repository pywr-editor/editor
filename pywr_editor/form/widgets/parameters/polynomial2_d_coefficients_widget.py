from pywr_editor.form import FormField, TableValuesWidget

"""
 Defines a widget to handle the coefficients for
 a 2D polynomial. The coefficients are given as
 list of nested lists.
"""


class Polynomial2DCoefficientsWidget(TableValuesWidget):
    var_names: list[str] = ["Value 1", "Value 2"]

    def __init__(
        self,
        name: str,
        value: list[list[float | int]] | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The polynomial coefficients.
        :param parent: The parent widget.
        """
        # parent widget wants a dictionary of variables, but the parameter
        # uses nested lists
        table_dict = {self.var_names[0]: [], self.var_names[1]: []}
        if isinstance(value, list):
            # coefficients must contain only 2 list
            for vi in range(2):
                try:
                    table_dict[self.var_names[vi]] = value[vi]
                except (IndexError, ValueError):
                    table_dict[self.var_names[vi]] = []

        super().__init__(
            name=name,
            value=table_dict,
            parent=parent,
            show_row_numbers=True,
            row_number_from_zero=True,
            row_number_label="Degree",
            min_total_values=1,
            scientific_notation=True,
            lower_bound=-pow(10, 30),
            upper_bound=pow(10, 30),
            precision=9,
        )
