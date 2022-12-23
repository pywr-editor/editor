import traceback
from typing import TYPE_CHECKING

import PySide6
from PySide6.QtAxContainer import QAxObject
from PySide6.QtCore import QCoreApplication, Qt, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QStyledItemDelegate,
    QVBoxLayout,
)

from pywr_editor.form import FormCustomWidget, ProfilePlotDialog
from pywr_editor.utils import Logging, is_windows
from pywr_editor.widgets import DoubleSpinBox, PushIconButton, TableView

if TYPE_CHECKING:
    from pywr_editor.dialogs import ParameterDialogForm
    from pywr_editor.form import AbstractAnnualValuesModel


class AbstractAnnualValuesWidget(FormCustomWidget):
    total_values = None

    def __init__(
        self,
        name: str,
        value: list[int | float] | None,
        model: "AbstractAnnualValuesModel",
        log_name: str,
        parent=None,
    ):
        """
        Initialises the widget for the values for an annual profile. The value can only
        be a list of floats or integers.
        :param name: The field name.
        :param value: The field value.
        :param model: The instance of the QAbstractTableModel to use.
        :param log_name: The name to use in the logger.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with value {value}")
        self.warning_message = None
        self.chart_options = None

        if self.total_values is None:
            raise ValueError(
                "The 'total_value' attribute must be defined as static class attribute"
            )

        super().__init__(name, value, parent)

        self.form: "ParameterDialogForm"
        self.model_config = self.form.model_config

        # Table
        self.value, self.warning_message = self.sanitise_value(value)
        # noinspection PyCallingNonCallable
        self.model = model(values=self.value)
        # noinspection PyUnresolvedReferences
        self.model.dataChanged.connect(self.on_value_change)

        self.table = TableView(self.model)
        self.table.setMaximumHeight(200)
        self.table.setAlternatingRowColors(False)
        # customise the QSpinBox precision
        self.table.setItemDelegate(AnnualProfileSpinBoxDelegate())

        # Buttons
        button_layout = QHBoxLayout()

        self.plot_button = PushIconButton(
            icon=":misc/plot", label="Plot profile", small=True
        )
        self.plot_button.setToolTip("Display a chart with the profile")
        # noinspection PyUnresolvedReferences
        self.plot_button.clicked.connect(self.plot_data)
        button_layout.addWidget(self.plot_button)
        button_layout.addStretch()

        if is_windows():
            self.paste_button = PushIconButton(
                icon=":misc/paste", label="Paste from Excel", small=True
            )
            self.paste_button.setToolTip(
                "Paste data copied from a column from an Excel spreadsheet"
            )
            # noinspection PyUnresolvedReferences
            self.paste_button.clicked.connect(self.paste_from_excel)

            self.export_button = PushIconButton(
                icon=":misc/export", label="Export to Excel", small=True
            )
            self.export_button.setToolTip(
                "Create an Excel spreadsheet containing the data from the table above"
            )
            # noinspection PyUnresolvedReferences
            self.export_button.clicked.connect(self.export_to_excel)

            button_layout.addWidget(self.paste_button)
            button_layout.addWidget(self.export_button)

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.form_field.set_warning_message(self.warning_message)

    @Slot()
    def on_value_change(self) -> None:
        """
        Enables the form button when the widget is updated.
        :return: None
        """
        self.form.save_button.setEnabled(True)

    def sanitise_value(
        self, value: list[int | float] | None
    ) -> [list[float | int], str | None]:
        """
        Sanitises the value.
        :param value: The value to sanitise.
        :return: The list of values and the warning message.
        """
        self.logger.debug(f"Sanitising value '{value}'")

        # check values
        message = None
        # value is None or not a list
        if value is None:
            self.logger.debug("Value is None")
            return self.all_zeros, None
        if isinstance(value, list) is False:
            message = "The values set in the model configuration are not valid"
        # wrong list size
        elif len(value) != self.total_values:
            message = (
                "The number of values set in the model configuration must "
                + f"exactly be {self.total_values}, {len(value)} values were given"
            )
        # wrong item types
        elif all([isinstance(val, (int, float)) for val in value]) is False:
            message = (
                "The values set in the model configuration must be all numbers"
            )

        # return None if the values are incorrect
        if message is not None:
            self.logger.debug(message + ". Returning default value")
            return self.all_zeros, message
        else:
            return value, message

    def get_value(self) -> list[float | int]:
        """
        Returns the values for the profile.
        :return: A list with values for the profile.
        """
        return self.model.values

    @property
    def all_zeros(self) -> list[int]:
        """
        The values with all zeros.
        :return: A list with all zeros.
        """
        return [0] * self.total_values

    def get_default_value(self) -> None:
        """
        The field default value.
        :return: None.
        """
        return None

    def reset(self) -> None:
        """
        Resets the widget. This sets all the values to zero in the table.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.values = self.all_zeros
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def paste_from_excel(self) -> None:
        """
        Populates the model with data from the clipboard.
        :return: None
        """
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text()
        self.logger.debug(f"Pasting data from clipboard {repr(text)}")
        text_to_list = clipboard.text().split("\n")
        message = None

        # remove empty entries and convert to number
        # noinspection PyBroadException
        try:
            text_to_list = [float(t) for t in text_to_list if t]
        except Exception:
            message = f"The profile must contain {self.total_values} numbers"
        # check list size
        if message is None:
            if len(text_to_list) == 0:
                message = (
                    "The clipboard is empty. Please copy the profile from an "
                    + "Excel spreadsheet"
                )
            elif len(text_to_list) != self.total_values:
                message = (
                    f"The profile must contain {self.total_values} values, "
                    + f"{len(text_to_list)} given"
                )

        if message is not None:
            QMessageBox.warning(
                self,
                "Warning",
                message,
                QMessageBox.StandardButton.Ok,
            )
            return

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.values = text_to_list
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        # noinspection PyUnresolvedReferences
        self.model.dataChanged.emit([], [], [])
        self.logger.debug(f"Model updated with {text_to_list}")

    # noinspection PyTypeChecker
    @Slot()
    def export_to_excel(self) -> None:
        """
        Exports the data to an Excel spreadsheet.
        :return: None
        """
        self.logger.debug("Exporting data to Excel")
        # disable button
        self.export_button.setEnabled(False)
        button_text = self.export_button.text()
        self.export_button.setText("Exporting...")
        self.table.setFocus()
        QCoreApplication.processEvents()

        # add the workbook
        # noinspection PyBroadException
        try:
            excel = QAxObject("Excel.Application", self)
            work_books = excel.querySubObject("WorkBooks")
            work_books.dynamicCall("Add")
            work_book = excel.querySubObject("ActiveWorkBook")

            # rename the sheet
            work_sheets = work_book.querySubObject("Sheets")
            first_sheet = work_sheets.querySubObject("Item(int)", 1)

            param_name = self.form.find_field_by_name("name")
            if param_name is not None and param_name != "":
                first_sheet.setProperty("Name", param_name.value())

            # header
            cell = first_sheet.querySubObject("Cells(int, int)", 1, 1)
            cell.setProperty("Value", self.model.label)
            cell = first_sheet.querySubObject("Cells(int, int)", 1, 2)
            cell.setProperty("Value", "Value")

            # values
            for row in range(0, self.model.rowCount()):
                for col in range(0, self.model.columnCount()):
                    index = self.model.index(row, col)
                    cell = first_sheet.querySubObject(
                        "Cells(int, int)", row + 2, col + 1
                    )
                    cell.setProperty(
                        "Value",
                        self.model.data(index, Qt.ItemDataRole.DisplayRole),
                    )

            # show Excel
            excel.dynamicCall("SetVisible(bool)", True)
        except Exception:
            self.logger.debug(
                "An error occurred while exporting data to Excel: "
                + traceback.print_exc()
            )
            QMessageBox.critical(
                self,
                "Error",
                "An error occurred while exporting the data to Excel",
                QMessageBox.StandardButton.Ok,
            )

        self.export_button.setEnabled(True)
        self.export_button.setText(button_text)

    @Slot()
    def plot_data(self) -> None:
        """
        Plots the profile.
        :return: None
        """
        param_name = self.form.find_field_by_name("name")
        if param_name is not None and param_name.value() != "":
            title = f"Parameter: {param_name.value()}"
        else:
            title = "Profile chart"

        dialog = ProfilePlotDialog(
            title=title,
            y=self.model.values,
            chart_options=self.chart_options,
            parent=self,
        )
        dialog.show()


class AnnualProfileSpinBoxDelegate(QStyledItemDelegate):
    def createEditor(
        self,
        parent: PySide6.QtWidgets.QWidget,
        option: PySide6.QtWidgets.QStyleOptionViewItem,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
    ) -> PySide6.QtWidgets.QWidget:
        return DoubleSpinBox(parent=parent)
