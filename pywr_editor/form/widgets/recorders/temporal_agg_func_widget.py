from pywr_editor.form import AbstractAggFuncWidget, FormField

"""
 Defines a widget to handle the function used in the "temporal_agg_func" key.
"""


class TemporalAggFuncWidget(AbstractAggFuncWidget):
    agg_func_percentile_list = "agg_func_percentile_list"
    agg_func_percentile_method = "agg_func_percentile_method"
    agg_func_percentileofscore_kind = "agg_func_percentileofscore_kind"
    agg_func_percentileofscore_score = "agg_func_percentileofscore_score"

    def __init__(self, name: str, value: str | None, parent: FormField):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected value.
        :param parent: The parent widget.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            agg_func_percentile_list=self.agg_func_percentile_list,
            agg_func_percentile_method=self.agg_func_percentile_method,
            agg_func_percentileofscore_kind=self.agg_func_percentileofscore_kind,
            agg_func_percentileofscore_score=self.agg_func_percentileofscore_score,
            log_name=self.__class__.__name__,
        )
