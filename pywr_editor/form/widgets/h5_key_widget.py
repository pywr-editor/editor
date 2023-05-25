import traceback
from typing import TYPE_CHECKING

from pandas import HDFStore
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormField, FormWidget, UrlWidget, Validation
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import ComboBox

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm


class H5KeyWidget(FormWidget):
    def __init__(
        self,
        name: str,
        value: str,
        parent: FormField,
    ):
        """
        Initialises the widget to list the available keys in the HDF file. This field
        is only available when the table file is of type HDF (i.e. extension is .h5).
        :param name: The field name.
        :param value: The current set sheet.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)
        self.form: "ModelComponentForm"
        self.model_config = self.form.model_config
        self.keys: list[str] = []
        self.is_key_valid = False
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
        self.field_value_changed: Signal = self.combo_box.currentTextChanged

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
        Populates the ComoBox with the key names.
        :return: None
        """
        self.logger.debug(
            f"Running on_populate_field Slot from {get_signal_sender(self)}"
        )
        self.logger.debug("Resetting widget")

        # prevent setItems, clear and setCurrentText methods of ComboBox from
        # triggering Slot
        self.combo_box.blockSignals(True)

        # on_update_value is called whilst the field is still empty
        self.setEnabled(False)
        self.combo_box.clear()
        self.field.clear_message(message_type="warning")

        # Load sheets
        self.load_key_names()
        self.value = self.sanitise_value(self.value)

        # the file does not exist. Field is emtpy and disabled. Error already shown in
        # URL widget
        if self.keys is None:
            self.logger.debug("The H5 file does not exist")
        # the file does not contain keys
        elif self.has_keys is False:
            self.field.set_warning("The H5 file does not contain any key")
        else:
            self.setEnabled(True)
            self.combo_box.addItems(self.keys)
            self.logger.debug(f"Added items to widget: {', '.join(self.keys)}")

            if self.value is False or self.is_key_valid is False:
                self.logger.debug(
                    f"{self.value} is not a valid key (using first sheet). "
                    + "Setting warning message"
                )
                self.field.set_warning(
                    "The key, currently set in the model config file, does not exist "
                    + "in the H5 file. The first available key was selected, otherwise "
                    + "select another name"
                )
            else:
                self.combo_box.setCurrentText(self.value)
                self.logger.debug(f"Selected value is {self.value}")

        self.combo_box.blockSignals(False)
        self.logger.debug("Completed on_populate_field Slot")

    @Slot(str)
    def on_update_value(self, selected_key: str) -> None:
        """
        Stores the last selected value when the field changes.
        :param selected_key: The selected item in the QComboBox.
        :return: None
        """
        self.logger.debug(
            f"Running on_update_value Slot with value {selected_key} from "
            + get_signal_sender(self)
        )
        self.field.clear_message(message_type="warning")
        self.value = self.sanitise_value(selected_key)
        self.logger.debug(f"Updated field value to {self.value}")
        self.logger.debug("Completed on_update_value Slot")

    def load_key_names(self) -> None:
        """
        Loads the key names if the file is of type HDF. This updated self.keys
        :return: None
        """
        # noinspection PyTypeChecker
        url_form_field: UrlWidget = self.form.fields["url"].widget
        file = url_form_field.full_file
        self.logger.debug(f"Loading keys from {file}")
        prev_keys = self.keys
        self.keys = []

        if file is None:  # the file does not exist
            self.keys = None
            self.logger.debug("Skipped, the file does not exist")
        elif url_form_field.file_ext == ".h5":
            # noinspection PyBroadException
            try:
                store = HDFStore(url_form_field.full_file)
                self.keys = store.keys()
                store.close()
                self.logger.debug(f"Found {', '.join(self.keys)}")
            except Exception:
                self.logger.debug(f"Exception thrown: {traceback.print_exc()}")
                pass
        else:
            self.logger.debug("Skipped, not a H5 file")

        if (
            self.keys is not None
            and len(self.keys) > 0
            and prev_keys is not None
            and len(prev_keys) > 0
            and prev_keys != self.keys
        ):
            self.logger.debug(
                f"New sheets ({', '.join(self.keys)}) are different than "
                + f"previous ones ({', '.join(prev_keys)})"
            )
            self.value = self.keys[0]
            self.logger.debug(
                f"Set selected key to first available value ({self.value})"
            )

    def get_default_value(self) -> str | None:
        """
        Returns the default value. This is the first key in the file, if the keys
        are available.
        :return: The default key or None if the keys are not valid.
        """
        return None

    def get_value(self) -> str | bool:
        """
        Returns the form field value.
        :return: The selected key.
        """
        return self.value

    def sanitise_value(self, value: str) -> str | bool:
        """
        Sanitises the value.
        :param value: The value to sanitise.
        :return: The selected key or False if the key is invalid.
        """
        self.logger.debug(f"Sanitising value {value}")
        selected_key = False
        self.is_key_valid = True

        # sheets are not available
        if self.has_keys is False:
            self.logger.debug("Key names are not available. Value not changed")
            selected_key = value
        elif value is None:
            # if value is not set (None), use the first key. The key is always
            # mandatory.
            selected_key = self.keys[0]
            self.logger.debug(f"Setting default value to {selected_key}")
        elif isinstance(value, str):
            # check that the provided name exists, otherwise select the first key.
            if value not in self.keys:
                selected_key = self.keys[0]
                self.is_key_valid = False
                self.logger.debug(
                    f"Key is not valid. The first key ({selected_key}) is selected"
                )
            else:
                selected_key = value
                self.logger.debug(f"Preserving passed value of {selected_key}")
        else:
            self.logger.debug(f"{value} is not a valid key name")
            self.is_key_valid = False

        return selected_key

    @property
    def has_keys(self) -> bool:
        """
        Returns whether the file has keys.
        :return: True if the file has keys, False otherwise.
        """
        return self.keys is not None and len(self.keys) > 0

    def validate(
        self,
        name: str,
        label: str,
        value: str | None,
    ) -> Validation:
        """
        Checks that the set H5 key is valid. Validation fails if there are no keys
        (file does not exist or is not valid) or the value is of the wrong type.
        When the key does not exist, the first key is always selected.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value from self.get_value().
        :return: The Validation instance.
        """
        self.logger.debug("Validating field")
        if self.has_keys is False or self.value is False:
            self.logger.debug("Validation failed")
            return Validation("You must select a valid key from the list")

        self.logger.debug("Validation passed")
        return Validation()
