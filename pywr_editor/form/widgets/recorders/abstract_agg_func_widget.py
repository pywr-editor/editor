from PySide6.QtCore import Slot

from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to handle the aggregation function for the "agg_func" and
 "temporal_agg_func" keys for a recorder. This widget also interacts with the
 FormFields to change the aggregation configuration when the aggregation
 function is "percentile" or "percentileofscore".

 The "agg_func" key is used by the aggregated_value pywr method of a recorder
 during an optimisation. There are no other components calling the
 method in pywr.

 The "temporal_agg_func" key is instead used by numpy array recorders to
 aggregate values temporally or along an axis (for example percentile for a
 flow duration curve).
"""


class AbstractAggFuncWidget(AbstractStringComboBoxWidget):
    def __init__(
        self,
        name: str,
        value: str | dict | None,
        parent: FormField,
        agg_func_percentile_list: str,
        agg_func_percentile_method: str,
        agg_func_percentileofscore_kind: str,
        agg_func_percentileofscore_score: str,
        log_name: str,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected value.
        :param parent: The parent widget.
        :param agg_func_percentile_list: The FormField name to change the list
        when the aggregation function is "percentile".
        :param agg_func_percentile_method: The FormField name to change the method
        when the aggregation function is "percentile".
        :param agg_func_percentileofscore_kind: The FormField name to change the
        kind when the aggregation function is "percentileofscore".
        :param agg_func_percentileofscore_score: The FormField name to change the
        score when the aggregation function is "percentileofscore".
        :param log_name: The log name.
        """
        self.agg_func_percentile_list = agg_func_percentile_list
        self.agg_func_percentile_method = agg_func_percentile_method
        self.agg_func_percentileofscore_kind = agg_func_percentileofscore_kind
        self.agg_func_percentileofscore_score = agg_func_percentileofscore_score

        labels_map = {
            # from AggFuncs enum in recorder.pyx
            "sum": "Sum",
            "min": "Minimum",
            "max": "Maximum",
            "mean": "Mean",
            "median": "Median",
            "product": "Product",
            "percentile": "Percentile",
            "percentileofscore": "Percentile of score",
            "count_nonzero": "Count non-zero values",
        }

        # convert dictionary to string. The function can be provided as string or
        # as dictionary for some numpy/scipy functions such as
        # {"func": "percentile", "args": [95],"kwargs": {}}
        _value = None
        if isinstance(value, str):
            _value = value
        elif isinstance(value, dict) and "func" in value:
            _value = value["func"]

        super().__init__(
            name=name,
            value=_value,
            parent=parent,
            log_name=log_name,
            labels_map=labels_map,
            default_value=self.get_default_value(),
        )
        self.init = True

        # change field visibility on value change
        # noinspection PyUnresolvedReferences
        self.combo_box.currentIndexChanged.connect(self.toggle_field_visibility)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        super().register_actions()

        # hide/show the fields
        self.toggle_field_visibility()
        self.init = False

    @Slot()
    def toggle_field_visibility(self) -> None:
        """
        SHows or hides specific fields depending on the selected function in the
        ComboBox.
        :return: None
        """
        for field_name in [
            self.agg_func_percentile_method,
            self.agg_func_percentile_list,
        ]:
            self.form.change_field_visibility(
                name=field_name,
                show=self.get_value() == "percentile",
                clear_message=self.init is False,
            )
            # reset field if method changes
            if self.get_value() != "percentile":
                self.form.find_field(field_name).widget.reset()

        for field_name in [
            self.agg_func_percentileofscore_score,
            self.agg_func_percentileofscore_kind,
        ]:
            self.form.change_field_visibility(
                name=field_name,
                show=self.get_value() == "percentileofscore",
                clear_message=self.init is False,
            )
            # reset field if method changes
            if self.get_value() != "percentileofscore":
                self.form.find_field(field_name).widget.reset()

    def get_default_value(self) -> str:
        """
        Returns the default value.
        :return: The default method.
        """
        return "mean"

    def merge_form_dict_fields(self, form_data: dict) -> None:
        """
        Helper function to Group the optimisation fields for the "agg_func"
        and "temporal_agg_func" fields.
        :param form_data: The form dictionary,
        :return: None. The function updates the dictionary given by reference.
        """
        # the FormField name ("agg_func" or "temporal_agg_func")
        field_name = self.field.name

        # return string or dictionary for agg_func depending on the selected method
        # By default a string is returned
        if field_name in form_data:
            # return dictionary, options for agg_func are mandatory and handled
            # by the respective widgets
            if form_data[field_name] == "percentile":
                self.logger.debug("Filtering 'percentile'")
                form_data[field_name] = {
                    "func": form_data[field_name],
                    # mandatory field
                    "args": form_data.pop(self.agg_func_percentile_list),
                }
                method = form_data.pop(self.agg_func_percentile_method, None)
                if method is not None:
                    form_data[field_name]["kwargs"] = {"method": method}
            elif form_data[field_name] == "percentileofscore":
                self.logger.debug("Filtering 'percentileofscore'")
                form_data[field_name] = {
                    "func": form_data[field_name],
                    "kwargs": {
                        # mandatory field
                        "score": form_data.pop(self.agg_func_percentileofscore_score),
                    },
                }
                # do not add None
                kind = form_data.pop(self.agg_func_percentileofscore_kind, None)
                if kind is not None:
                    form_data[field_name]["kwargs"]["kind"] = kind
