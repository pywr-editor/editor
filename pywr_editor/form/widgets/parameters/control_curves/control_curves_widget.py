from pywr_editor.form import AbstractParametersListPickerWidget, FormField
from pywr_editor.utils import Logging

"""
 This widgets inherits from AbstractParametersListPickerWidget.
 Control curves can be specified using the following
 keys:
  - control_curve: for a number, a parameter
    dictionary or model parameter
  - control_curves: for a list of numbers, parameter
    dictionaries or model parameters

 The widget converts the value to a list of parameters
 to be compatible with the parent widget.
"""


class ControlCurvesWidget(AbstractParametersListPickerWidget):
    def __init__(
        self,
        name: str,
        value: dict[
            str,
            str | dict | float | int | list[str | dict | float | int] | None,
        ],
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: A dictionary with the "control_curve" and "control_curves" keys.
        The dictionary values are a parameter or list of parameters defining the
        control curves. A parameter can be defined as a number, dictionary or string
        for model parameters.
        :param parent: The parent widget.
        """
        # check which key is provided
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        new_value = None
        if value["control_curve"] is not None:
            self.logger.debug("'control_curve' key is set")
            new_value = value["control_curve"]
        elif value["control_curves"] is not None:
            self.logger.debug("'control_curves' key is set")
            new_value = value["control_curves"]

        # force value to list if not
        if new_value and not isinstance(new_value, list):
            self.logger.debug("Converting value to list")
            new_value = [new_value]

        super().__init__(
            name=name,
            value=new_value,
            parent=parent,
            show_row_numbers=True,
            row_number_label="Curve",
            log_name=self.__class__.__name__,
        )
        self.list.resizeColumnsToContents()
