from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGroupBox, QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import ComboBox

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm


"""
 This widgets handles the visibility of the form widgets depending
 on the selected source. For example, if the parameter is defined
 from a model table, the "value", "url", "index_col" and "parse_dates"
 fields are hidden. The source can be:
    - table: the parameter is defined using data from a model table
    - url: the parameter is defined directly using an external file
    - value: the parameter is defined by specifying its value(s)

 The widget skips non-existing form fields. For example ConstantParameter
 uses "value" as field name, but all other profiles (such as
 MonthlyProfileParameter) use "values". ConstantParameter also
 makes use of the "index" field to define its value, but all other
 parameters do not.
"""


class SourceSelectorWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: dict,
        parent: FormField,
        enable_value_source: bool = True,
        log_name: str = None,
    ):
        """
        Initialises the widget to select the parameter source (from a table, url or
        provide a value).
        :param name: The field name.
        :param value: The parameter dictionary.
        :param parent: The parent widget.
        :param enable_value_source: Whether the widget should handle the "value" and
        "values" fields for the parameter. Default to True. Some parameters like the
        DataFrameParameter supports only the "url" and "table" fields.
        :param log_name: The name to use in the logger.
        """
        if log_name is None:
            log_name = self.__class__.__name__

        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with value {value}")
        super().__init__(name, value, parent)

        self.labels = {
            "table": "An existing model table",
            "anonymous_table": "A table from an external file",
            "value": "Provide value",
        }
        if enable_value_source is False:
            del self.labels["value"]

        self.combo_box = ComboBox()
        self.combo_box.addItems(list(self.labels.values()))
        self.enable_value_field = enable_value_source
        self.init = True

        # the parameter configuration depends on which fields are provided in the
        # configuration
        if self.enable_value_field:
            if "table" in value:
                self.combo_box.setCurrentText(self.labels["table"])
                self.logger.debug("Source is table")
            elif "url" in value:
                self.combo_box.setCurrentText(self.labels["anonymous_table"])
                self.logger.debug("Source is anonymous table")
            # default
            else:
                self.combo_box.setCurrentText(self.labels["value"])
                self.logger.debug("Source is value")
        else:
            self.logger.debug("Value(s) field will not be handled")
            if "url" in value:
                self.combo_box.setCurrentText(self.labels["anonymous_table"])
                self.logger.debug("Source is anonymous table")
            # default to table
            else:
                self.combo_box.setCurrentText(self.labels["table"])
                self.logger.debug("Source is table")

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

        # run action after all fields are available
        self.form.register_after_render_action(self.after_field_render)

    def after_field_render(self) -> None:
        """
        Action called after the entire section has been rendered. This shows and hides
        the form fields based on the selected source.
        :return: None
        """
        # init form
        self.on_type_change(self.get_value())

        # noinspection PyUnresolvedReferences
        self.combo_box.currentTextChanged.connect(self.on_type_change)

        self.init = False

    @Slot(str)
    def on_type_change(self, field_value: str) -> None:
        """
        Slots called at init or when the field changes its value.
        :param field_value: The field value or index.
        :return: None
        """
        self.logger.debug(
            f"Running on_type_change Slot with value '{field_value}' from "
            + get_signal_sender(self)
        )

        # Trigger field reset and Slots after field is initialised
        if self.init is False:
            for name in ["url", "table", "value", "values"]:
                self.logger.debug(f"Resetting FormField '{name}'")
                form_field = self.form.find_field_by_name(name)
                # ignore non-existing fields
                if form_field is not None:
                    # noinspection PyUnresolvedReferences
                    form_field.widget.reset()

        # Toggle component visibility
        # 1. The "index" and "column" fields are both used by UrlWidget and
        #    TableSelectorWidget
        # 2. "index_col" and "parse_dates" fields (these apply to anonymous tables
        #    only) are handled by this widget and UrlWidget depending on the file type
        # 3. When source is value the "Table configuration" section is hidden
        hide_table_group_box = False
        if field_value == self.labels["table"]:
            hide = [
                "value",
                "values",
                "url",
                "index_col",
                "parse_dates",
            ]
            show = ["table", "index", "column"]
        elif field_value == self.labels["anonymous_table"]:
            hide = ["value", "values", "table"]
            show = ["url", "index", "column", "index_col", "parse_dates"]
        elif field_value == self.labels["value"]:
            hide = [
                "index",
                "column",
                "table",
                "url",
                "index_col",
                "parse_dates",
            ]
            show = ["value", "values"]
            hide_table_group_box = True
        else:
            raise ValueError("Wrong source type provided")

        # show (and enable) or hide (and disable) the correct fields
        # ignore non-existing fields
        self.logger.debug(f"Hiding fields: {', '.join(hide)}")
        [
            self.form.change_field_visibility(
                name,
                show=False,
                clear_message=True,
                disable_on_hide=True,
                throw_if_missing=False,
            )
            for name in hide
        ]
        self.logger.debug(f"Showing fields: {', '.join(show)}")
        [
            self.form.change_field_visibility(
                name,
                show=True,
                clear_message=True,
                disable_on_hide=True,
                throw_if_missing=False,
            )
            for name in show
        ]

        # Hide section
        self.form: "ModelComponentForm"
        group_name = self.form.table_config_group_name
        # noinspection PyTypeChecker
        group_box: QGroupBox = self.form.findChild(QGroupBox, group_name)
        if group_box is not None:
            if self.enable_value_field:
                if hide_table_group_box:
                    self.logger.debug(f"Hiding '{group_name}' QGroupBox")
                    group_box.setVisible(False)
                else:
                    self.logger.debug(f"Showing '{group_name}' QGroupBox")
                    group_box.setVisible(True)

    def get_value(self) -> str:
        """
        Returns the form field value.
        :return: The form field value.
        """
        return self.combo_box.currentText()
