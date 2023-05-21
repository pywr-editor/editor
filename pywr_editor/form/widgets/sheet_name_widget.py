import traceback
from typing import TYPE_CHECKING

from pandas import ExcelFile
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField, FormValidation, UrlWidget
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import ComboBox

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm


class SheetNameWidget(FormCustomWidget):
    def __init__(self, name: str, value: str, parent: FormField):
        """
        Initialises the widget to list the available sheet names in the Excel file.
        This field is only available when the table file is of type Excel (i.e.
        extension is either .xlx, .xlsx or .xlsm).
        :param name: The field name.
        :param value: The current set sheet.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)
        self.form: "ModelComponentForm"
        self.model_config = self.form.model_config
        self.excel_sheets = []
        self.is_valid_sheet = False
        self.value = self.sanitise_value(value)

        # combo box
        self.combo_box = ComboBox()
        self.combo_box.setObjectName(f"{name}_combo_box")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

        # populate field for the first time
        self.logger.debug("Populating widget")
        self.on_populate_field()

        # connect Slots after widget render
        self.logger.debug("Connecting currentTextChanged Slot")
        # 1. update the internal value when the selected sheet name changes
        # noinspection PyUnresolvedReferences
        self.combo_box.currentTextChanged.connect(self.on_update_value)

        # 2. Slot used by UrlWidget. When sheet name changes, this automatically
        # reloads the table
        self.logger.debug("Registering field_value_changed")
        # noinspection PyUnresolvedReferences
        self.field_value_changed = self.combo_box.currentTextChanged

    @Slot()
    def on_update_field(self) -> None:
        """
        Slots triggered to update the field. This is registered by another widget.
        :return: None
        """
        self.logger.debug(
            "Running on_update_field Slot because file changed from "
            + get_signal_sender(self)
        )
        self.on_populate_field()
        self.logger.debug("Completed on_update_field Slot")

    @Slot()
    def on_populate_field(self) -> None:
        """
        Populates the ComoBox with the sheet names.
        :return: None
        """
        self.logger.debug(
            f"Running on_populate_field Slot from {get_signal_sender(self)}"
        )
        self.logger.debug("Resetting widget")

        # prevent setItems, clear and setCurrentText methods of ComboBox from
        # triggering SLot
        self.combo_box.blockSignals(True)

        # on_update_value is called whilst the field is still empty
        self.setEnabled(False)
        self.combo_box.clear()
        self.form_field.clear_message(message_type="warning")

        # Load sheets
        self.load_excel_sheets()
        self.value = self.sanitise_value(self.value)

        # the file does not exist. Field is emtpy and disabled. Error already
        # shown in URL widget
        if self.excel_sheets is None:
            self.logger.debug("The Excel file does not exist")
        # the file does not contain sheets
        elif self.has_excel_sheet is False:
            self.logger.debug("The Excel file does not contain any sheet")
            self.form_field.set_warning_message(
                "The Excel file does not contain any sheet"
            )
        else:
            self.setEnabled(True)
            self.combo_box.addItems(self.excel_sheets)
            self.logger.debug(f"Added items to widget: {', '.join(self.excel_sheets)}")

            if self.value is False or self.is_valid_sheet is False:
                self.logger.debug(
                    f"{self.value} is not a valid sheet name (using first sheet). "
                    + "Setting warning message"
                )
                self.form_field.set_warning_message(
                    "The sheet name, currently set in the model config file, does not "
                    + "exist in the Excel file. The first available sheet was "
                    + "selected, otherwise select another name"
                )
            else:
                self.combo_box.setCurrentText(self.value)
                self.logger.debug(f"Selected value is {self.value}")

        self.combo_box.blockSignals(False)
        self.logger.debug("Completed on_populate_field Slot")

    @Slot(str)
    def on_update_value(self, selected_sheet: str) -> None:
        """
        Stores the last selected value when the field changes.
        :param selected_sheet: The selected item in the QComboBox.
        :return: None
        """
        self.logger.debug(
            f"Running on_update_value Slot with value {selected_sheet} from "
            + get_signal_sender(self)
        )
        self.form_field.clear_message(message_type="warning")
        self.value = self.sanitise_value(selected_sheet)
        self.logger.debug(f"Updated field value to {self.value}")
        self.logger.debug("Completed on_update_value Slot")

    def load_excel_sheets(self) -> None:
        """
        Loads the sheet names if the file is of type Excel. This updated
        self.excel_sheets
        :return: None
        """
        # noinspection PyTypeChecker
        url_form_field: UrlWidget = self.form.fields["url"].widget
        file = url_form_field.full_file
        self.logger.debug(f"Loading sheets from {file}")
        prev_sheets = self.excel_sheets
        self.excel_sheets = []

        if file is None:  # the file does not exist
            self.excel_sheets = None
            self.logger.debug("Skipped, the file does not exist")
        elif url_form_field.file_ext in [".xls", ".xlsx", ".xlsm"]:
            # noinspection PyBroadException
            try:
                xl = ExcelFile(url_form_field.full_file)
                self.excel_sheets = xl.sheet_names
                xl.close()
                self.logger.debug(f"Found {', '.join(self.excel_sheets)}")
            except Exception:
                self.logger.debug(f"Exception thrown: {traceback.print_exc()}")
                pass
        else:
            self.logger.debug("Skipped, not an Excel file")

        if (
            self.excel_sheets is not None
            and len(self.excel_sheets) > 0
            and prev_sheets is not None
            and len(prev_sheets) > 0
            and prev_sheets != self.excel_sheets
        ):
            self.logger.debug(
                f"New sheets ({', '.join(self.excel_sheets)}) are different than "
                + f"previous ones ({', '.join(prev_sheets)})"
            )
            self.value = self.excel_sheets[0]
            self.logger.debug(
                f"Set selected sheet to first available value ({self.value})"
            )

    def get_default_value(self) -> int:
        """
        Returns the default value. This is the first sheet in the Excel file.
        :return: The default sheet.
        """
        return 0

    def get_value(self) -> str | int | bool:
        """
        Returns the form field value.
        :return: The selected sheet name.
        """
        return self.value

    def sanitise_value(self, value: str | int) -> str | bool:
        """
        Sanitises the value. If the Excel sheets are available and the value is a
        column number, this will convert the value to an Excel sheet name for
        consistency.
        :param value: The value to sanitise.
        :return: The selected sheet name or False if the sheet name or number is
        invalid.
        """
        self.logger.debug(f"Sanitising value {value}")
        # When False, Pandas loads the first available sheet
        selected_sheet_name = False
        self.is_valid_sheet = True

        # sheets are not available
        if self.has_excel_sheet is False:
            self.logger.debug("Sheet names are not available. Value not changed")
            selected_sheet_name = value
        # handle different value types for the selected sheet (as string or int)
        elif value is None:
            # if value is not set, it is None. With None, Pandas will load all sheets
            # and dataframes in a dictionary. To prevent this, use the first (default)
            # sheet.
            selected_sheet_name = self.excel_sheets[0]
            self.logger.debug(f"Setting default value to {selected_sheet_name}")
        elif isinstance(value, int) or isinstance(value, str):
            if isinstance(value, str):
                # check that the provided name exists, otherwise select the first sheet.
                if value not in self.excel_sheets:
                    selected_sheet_name = self.excel_sheets[0]
                    self.is_valid_sheet = False
                    self.logger.debug(
                        "Sheet name is not valid. The first sheet ("
                        + f"{selected_sheet_name}) is selected"
                    )
                else:
                    selected_sheet_name = value
                    self.logger.debug(
                        f"Preserving passed value of {selected_sheet_name}"
                    )
            else:
                # if sheet index is provided, convert to string
                try:
                    selected_sheet_name = self.excel_sheets[value]
                    self.logger.debug(
                        f"Converted value to string to {selected_sheet_name}"
                    )
                except IndexError:
                    # index is wrong. Passed value will be False, which will cause
                    # Pandas to load the first available sheet
                    selected_sheet_name = self.excel_sheets[0]
                    self.is_valid_sheet = False
                    self.logger.debug(
                        "Sheet index is not valid. The first sheet ("
                        + f"{selected_sheet_name}) is selected"
                    )
                    pass
        else:
            self.logger.debug(f"{value} is not a valid sheet name")
            self.is_valid_sheet = False

        return selected_sheet_name

    @property
    def has_excel_sheet(self) -> bool:
        """
        Returns whether the file has Excel sheets.
        :return: True if the file has Excel sheets, False otherwise.
        """
        return self.excel_sheets is not None and len(self.excel_sheets) > 0

    def validate(
        self,
        name: str,
        label: str,
        value: str | None,
    ) -> FormValidation:
        """
        Checks that the set Excel sheet is valid. Validation fails if there are no
        sheets (file does not exist or is not valid) or the value is of the wrong type.
        When the key does not exist, the first key is always selected.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value from self.get_value().
        :return: The FormValidation instance.
        """
        self.logger.debug("Validating field")
        if self.has_excel_sheet is False or self.value is False:
            self.logger.debug("Validation failed")
            return FormValidation(
                validation=False,
                error_message="You must select a valid sheet from the list",
            )

        self.logger.debug("Validation passed")
        return FormValidation(validation=True)
