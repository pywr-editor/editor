from PySide6.QtCore import Slot

from pywr_editor.form import AbstractStringComboBoxWidget, FormField
from pywr_editor.utils import Logging, get_signal_sender

"""
 Change the visibility of the fields to provide
 the control curve values. The values can be provided
 as list of numbers or as parameters.
"""


class ControlCurvesValuesSourceWidget(AbstractStringComboBoxWidget):
    def __init__(self, name: str, value: dict[str, bool], parent: FormField):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: A dictionary containing "values" and "parameters" as keys and a
        boolean as value indicating which key is present in the control curve parameter
        dictionary.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        self.init: bool = True
        new_value = None
        if value["values"] is True:
            self.logger.debug("'values' key is set")
            new_value = "values"
        elif value["parameters"] is True:
            self.logger.debug("'parameters' key is set")
            new_value = "parameters"

        super().__init__(
            name=name,
            value=new_value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map={
                "values": "Use constant values",
                "parameters": "Use values from parameters",
            },
            keep_default=True,
            default_value="values",
        )

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        super().register_actions()
        # init field visibility
        self.toggle_visibility()

        # noinspection PyUnresolvedReferences
        self.combo_box.currentIndexChanged.connect(self.toggle_visibility)
        self.init = False

    @Slot()
    def toggle_visibility(self) -> None:
        """
        Shows/hides the values and parameters fields and resets the widgets.
        :return: None
        """
        self.logger.debug(f"Running on_populate_field Slot - {get_signal_sender(self)}")
        for field_name in self.labels_map.keys():
            self.form.change_field_visibility(
                name=field_name, show=self.get_value() == field_name
            )
            widget = self.form.find_field_by_name(field_name).widget
            # reset only after init
            if self.init is False:
                widget.reset()
