import traceback
from dataclasses import dataclass
from typing import Any

from pandas import DataFrame
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel, QVBoxLayout

from pywr_editor.form import (
    FormCustomWidget,
    FormField,
    FormValidation,
    IndexColWidget,
    SourceSelectorWidget,
    TableSelectorWidget,
    UrlWidget,
)
from pywr_editor.utils import (
    Logging,
    clear_layout,
    default_index_name,
    get_columns,
    get_index_names,
    get_index_values,
    get_signal_sender,
    is_table_not_empty,
)
from pywr_editor.widgets import ComboBox


@dataclass
class StoredIndexDict:
    index_values: list[str | float | int | None | bool] = None
    index_names: list[str] = None
    index_types: list[type | None] = None

    def __post_init__(self):
        self.index_values = []
        self.index_names = []
        self.index_types = []


class IndexWidget(FormCustomWidget):
    default_index_name = "Anonymous index"

    def __init__(
        self,
        name: str,
        value: dict,
        parent: FormField,
        optional: bool = False,
    ):
        """
        Initialises the widget to provide the list of the values stored in the table
        indexes. The field gets the DataFrame from the TableSelectorWidget or UrlWidget.
        NOTE: this applies to CSV and Excel files only as H5 files are not supported by
        ConstantParameter (i.e. read_hdf, used by the parameter, does not support
        "index_col" to set the data frame index).
        :param name: The field name.
        :param value: The value set for the index. This is a dictionary with "index"
        and "indexes" as key. Pywr look for both key in the dictionary.
        :param parent: The parent widget.
        :param optional: Whether the field is optional. Default to False.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)
        self.init = True
        self.optional = optional
        self._value = value
        self.value = StoredIndexDict()

        # layout is populated afterwards based on the number of indexes set
        # on the DataFrame
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # populate fields
        self.form.register_after_render_action(self.after_form_render)

    def init_index_values(
        self,
        index_names: str | int | list[str] | list[int] | None,
        index_values: Any | list[Any] | None,
    ) -> dict[str, Any | None]:
        """
        Initialises the initial index values.
        :param index_names: The name of the initial indexes.
        :param index_values: The value of the indexes.
        :return: A dictionary with the index name as key as its value as dictionary
        value. If the index names are not provided, the dictionary is empty. If at
        least one index value is not provided, all the values are set to None.
        """
        value_source_field = self.form.find_field_by_name("source")
        selected_source = value_source_field.value()
        # noinspection PyTypeChecker
        value_source_widget: SourceSelectorWidget = value_source_field.widget

        # dataframe from the table set in the table field
        if selected_source == value_source_widget.labels["table"]:
            # noinspection PyTypeChecker
            table_selector_widget: TableSelectorWidget = (
                self.form.find_field_by_name("table").widget
            )
            # if table is not available or invalid, preserve index names from
            # table selector
            if (
                table_selector_widget.table is None
                or table_selector_widget.table.empty
            ):
                index_names = table_selector_widget.index_names
            else:
                index_names = get_index_names(table_selector_widget.table)
            self.logger.debug(
                f"Fetched index names from TableSelectorWidget: {index_names}"
            )
        # use values in "index_col" key. This ensures sorting between index names
        # and values
        elif selected_source == value_source_widget.labels["anonymous_table"]:
            # "index_col" key not provided
            if not index_names or index_names == "":
                self.logger.debug(
                    "Index names not provided ('index_col' key is None). "
                    + f"Using '{default_index_name}'"
                )
                index_names = [default_index_name]
            # cast to list
            elif not isinstance(index_names, list):
                self.logger.debug("Converted index name to list")
                index_names = [index_names]

            # index_col is provided with numerical column indexes - check column
            # and convert to string
            if isinstance(index_names[0], int):
                # noinspection PyTypeChecker
                url_widget: UrlWidget = self.form.find_field_by_name(
                    "url"
                ).widget
                columns = get_columns(url_widget.table, True)
                new_index_names = []
                for index in index_names:
                    # noinspection PyBroadException
                    try:
                        new_index_names.append(columns[index])
                    except Exception:
                        # preserve wrong column
                        self.logger.debug(
                            f"Column index {index} not found: {traceback.print_exc()}"
                        )
                        new_index_names.append(str(index))
                        pass
                self.logger.debug(
                    f"Converted numerical column indexes '{index_names}' "
                    + "to column names"
                )
                index_names = new_index_names

            self.logger.debug(
                f"Fetched index names from index_col: {', '.join(index_names)}"
            )
        else:
            index_names = [None]
            self.logger.debug("Index names not available")

        # index names are not provided
        if index_names is None:
            self.logger.debug("Index names not found. Set empty dictionary")
            return {}

        # "index" key not provided
        if index_values is None:
            self.logger.debug("Index values not provided. Set empty values")
            return {index_name: None for index_name in index_names}

        # cast to list in case of string or integer
        if not isinstance(index_values, list):
            self.logger.debug("Converted index value to list")
            index_values = [index_values]
        # length of values != length of names (i.e. not possible to map values to names)
        if len(index_names) != len(index_values):
            self.logger.debug(
                f"The length of the index names ({len(index_names)}) differs from the "
                + f"length of the index values ({len(index_values)}). Set "
                + "invalid values"
            )
            return {index_name: False for index_name in index_names}

        self.logger.debug(
            f"Using index names: {index_names} / index_values: {index_values}"
        )
        return {
            index_name: index_values[ii]
            for ii, index_name in enumerate(index_names)
        }

    def after_form_render(self) -> None:
        """
        Renders the widgets after the entire form is rendered. This also re-renders
        the fields when the table is updated
        :return: None
        """
        self.logger.debug("Registering post-render section actions")

        # Pywr parses both the "index" and "indexes" key. Check which one is set.
        # Although both keys can be provided, this applies only to parameters
        # supporting multi-indexes.
        # See https://github.com/pywr/pywr/blob/c19070a774edcdb765124170c3b3de6cfc6234e7/pywr/dataframe_tools.py#L159) # noqa: E501
        indexes = None
        if self._value["index"] is not None:
            indexes = self._value["index"]
        elif "indexes" in self._value:
            indexes = self._value["indexes"]
        init_value = self.init_index_values(self._value["index_col"], indexes)

        # populate field for the first time
        self.value = self.sanitise_value(init_value)
        self.on_populate_field()
        self.init = False

    @property
    def table(self) -> [DataFrame | None, str | None]:
        """
        Returns the table used for the parameter. The table is loaded from the
        TableSelectorWidget or UrlWidget depending on the selected source.
        :return: A tuple containing the table, if the table is available (None when
        it is not) and the file extension.
        """
        self.logger.debug("Fetching table")
        # noinspection PyTypeChecker
        value_source_field = self.form.find_field_by_name("source")
        selected_source = value_source_field.value()
        # noinspection PyTypeChecker
        value_source_widget: SourceSelectorWidget = value_source_field.widget

        # dataframe from the table set in the table field
        if selected_source == value_source_widget.labels["table"]:
            # noinspection PyTypeChecker
            table_field: TableSelectorWidget = self.form.find_field_by_name(
                "table"
            ).widget
            self.logger.debug("Table loaded from TableSelectorWidget")
        # dataframe from the table set in the url field
        elif selected_source == value_source_widget.labels["anonymous_table"]:
            # noinspection PyTypeChecker
            table_field: UrlWidget = self.form.find_field_by_name("url").widget
            self.logger.debug("Table loaded from UrlWidget")
        else:
            self.logger.debug("The table cannot be fetched")
            return None, None

        return table_field.table, table_field.file_ext

    def sanitise_value(self, value: dict[str, Any]) -> StoredIndexDict:
        """
        Sanitises the value.
        :param value: The value to sanitise as a dictionary of index name as key as
        index value as dictionary value.
        :return: A instance of StoredIndexDict containing the name, values and types
        of all the table indexes.
        """
        self.logger.debug(f"Sanitising value {value}")
        selected_index_dict = StoredIndexDict()
        table, file_ext = self.table

        if is_table_not_empty(table) is False:
            self.logger.debug(
                "The table is not available or is empty. Value not changed"
            )
            selected_index_dict.index_names = list(value.keys())
            selected_index_dict.index_values = list(value.values())
        else:
            index_names = get_index_names(table)
            for index_id, name in enumerate(index_names):
                all_index_values = get_index_values(table, name)[0]
                first_value = all_index_values[0]

                self.logger.debug(
                    f"Sanitising index #{index_id} ({name}) - data type is "
                    + f"{type(first_value).__name__}"
                )
                # add index name and type
                selected_index_dict.index_names.append(name)
                data_type_fun = type(first_value)
                selected_index_dict.index_types.append(data_type_fun)

                # get value
                # for H5 files the index is not passed by the index_col key, it is
                # already sorted in list check that index map is provided
                if file_ext == ".h5" and value:
                    values_list = list(value.values())
                    self.logger.debug(
                        "Index name from H5 file. Mapping index name to value using "
                        + f"{values_list}"
                    )
                    index_value = values_list[index_id]
                elif name in value.keys():
                    self.logger.debug("Index name found in passed values")
                    index_value = value[name]
                else:
                    self.logger.debug(
                        "Value not available. Setting empty value"
                    )
                    index_value = None

                if index_value in ["", "None"] or index_value is None:
                    self.logger.debug(f"Value not set ({index_value})")
                    selected_index_dict.index_values.append(None)
                elif index_value is False:
                    self.logger.debug(f"Value is invalid ({index_value})")
                    selected_index_dict.index_values.append(index_value)
                else:
                    index_value_correct_type = data_type_fun(index_value)

                    self.logger.debug(
                        f"Updating index value with {index_value} "
                        + f"({index_value_correct_type}) - "
                        + f"data type is {type(first_value).__name__}"
                    )
                    # always the correct type - self.value may store a string as number
                    if index_value_correct_type not in all_index_values:
                        self.logger.debug(
                            f"The value '{index_value_correct_type}' does not exist "
                            + "in the index column"
                        )
                        selected_index_dict.index_values.append(False)
                    else:
                        self.logger.debug(f"Using final value: '{index_value}'")
                        selected_index_dict.index_values.append(index_value)

            # supplied index names that are not valid table indexes
            removed_indexes = list(set(value.keys()) - set(index_names))
            if removed_indexes:
                # column names may be numeric
                removed_indexes = list(map(str, removed_indexes))
                self.logger.debug(
                    "The following supplied index names are not valid table indexes: "
                    + ", ".join(removed_indexes)
                )

        return selected_index_dict

    @Slot()
    def on_populate_field(self) -> None:
        """
        Populates the widget with the ComboBox for each index.
        :return: None
        """
        self.logger.debug(
            f"Running on_populate_field Slot - {get_signal_sender(self)}"
        )

        # empty the layout
        self.logger.debug("Resetting widget")
        clear_layout(self.layout)
        self.form_field.clear_message(message_type="warning")

        table, _ = self.table
        columns = get_columns(table)

        # show dummy field when the table is not valid or set
        if is_table_not_empty(table) is False:
            if table is None:
                self.logger.debug(
                    "The table is not available and data cannot be fetched"
                )
            # no columns
            elif len(columns) == 0:
                self.logger.debug(
                    "The table does not contain any column. Keeping field disabled "
                    + "with warning"
                )
                self.form_field.set_warning_message(
                    "The table does not contain any column"
                )
            # no rows - although columns are available and index names may be set,
            # just show dummy field
            elif len(table) == 0:
                self.logger.debug(
                    "The table does not contain any rows. Keeping field disabled "
                    + "with warning"
                )
                self.form_field.set_warning_message(
                    "The table does not contain any row"
                )
            # show dummy field
            layout, _ = self.render_field_layout(default_index_name, 0)
            self.layout.addLayout(layout)
        else:
            wrong_index_values = []
            index_names = get_index_names(table)

            self.logger.debug(
                f"Found the following indexes: {', '.join(index_names)}"
            )

            # Add ComboBox and populate it
            for index_id, name in enumerate(index_names):
                self.logger.debug(
                    f"Rendering field #{index_id+1} for index '{name}'"
                )
                index_field_layout, combo_box = self.render_field_layout(
                    index_name=name,
                    index_number=index_id,
                )
                # add the ComboBox
                self.layout.addLayout(index_field_layout)
                combo_box.setEnabled(True)
                self.logger.debug("Fetching index values")

                # populate it
                all_index_values = get_index_values(table, name)[0]
                combo_box.addItems(["None"] + list(map(str, all_index_values)))
                combo_box.setCurrentText("None")

                # set the selected value
                ii = self.value.index_names.index(name)
                current_value = self.value.index_values[ii]
                if current_value is False:
                    wrong_index_values.append(name)
                    self.logger.debug(
                        f"The value of the index {name} does not exist in the table"
                    )
                else:
                    self.logger.debug(f"Setting value '{current_value}'")
                    combo_box.setCurrentText(str(current_value))

                # add Slot to update values when user select another index value
                # noinspection PyUnresolvedReferences
                combo_box.currentTextChanged.connect(self.on_update_value)

            if wrong_index_values:
                self.form_field.set_warning_message(
                    "The value of the following indexes is not valid or does not exist "
                    + "in the table: "
                    + ", ".join(wrong_index_values)
                )

    @Slot(str)
    def on_update_value(self, new_index_value: str) -> None:
        """
        Stores the last selected values of the indexes when one field changes.
        This function updates the values for all indexed, regardless of the changed
        index.
        :param new_index_value: The selected item in the QComboBox. This is not used.
        :return: None
        """
        self.logger.debug(
            f"Running on_update_value Slot - {get_signal_sender(self)} value changed "
            + f"to {new_index_value}"
        )
        self.form_field.clear_message(message_type="warning")

        # Collect all the index values to sanitise
        new_values = {}
        table, _ = self.table
        for index_name in get_index_names(table):
            # noinspection PyTypeChecker
            combo_box: ComboBox = self.findChild(ComboBox, index_name)
            new_values[combo_box.objectName()] = combo_box.currentText()

        self.value = self.sanitise_value(new_values)
        self.logger.debug(f"Updated field value to '{self.value}'")
        self.logger.debug("Completed on_update_value Slot")

    @Slot()
    def update_field(self) -> None:
        """
        Slots triggered to update the field. This is registered by the URL and table
        widgets.
        :return: None
        """
        # when form is initialises, UrlWidget registers index_changed Slots, then
        # IndexColWidget inits and emits index_changed before ColWidget is
        # initialised. Prevent this behaviour (it is wrong) by ignoring the Signal
        # before this widget is initialised.
        if self.init is True:
            self.logger.debug(
                "Skipping update_field Slot when index changed. Widget not "
                + "initialised yet"
            )
            return

        self.logger.debug(
            "Running update_field Slot because index changed - "
            + get_signal_sender(self)
        )
        # reparse the previously stored values. If table was invalid, force update
        # of types
        values = {
            name: self.value.index_values[ii]
            for ii, name in enumerate(self.value.index_names)
        }
        self.value = self.sanitise_value(values)
        self.on_populate_field()
        self.logger.debug("Completed update_field Slot")

    def render_field_layout(
        self, index_name: str, index_number: int
    ) -> [QVBoxLayout, ComboBox]:
        """
        Renders the label and ComboBox to select the index values.
        :param index_name: The name of the index.
        :param index_number: The number of the index being added.
        :return: A tuple with the layout and ComBox instances.
        """
        self.logger.debug("Rendering widget")

        # columns list
        combo_box = ComboBox()
        combo_box.setEnabled(False)
        combo_box.setCurrentText("None")
        combo_box.setObjectName(index_name)
        # reconnect the Slot to enable the save button
        # noinspection PyUnresolvedReferences
        combo_box.activated.connect(self.form.on_field_changed)

        # main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setObjectName(f"{index_name}_layout")
        label = QLabel(f"Index: {index_name}")
        label.setObjectName(f"{index_name}_label")

        # align the first label with FormField label
        if index_number == 0 and self.form.direction == "horizontal":
            label.setStyleSheet("QLabel{ margin-top: 8px }")
        main_layout.addWidget(label)
        main_layout.addWidget(combo_box)

        return main_layout, combo_box

    def validate(
        self,
        name: str,
        label: str,
        value: list[int | float | str] | int | float | str,
    ) -> FormValidation:
        """
        Validates the field. The field fails validation when the value is None, or for
        multi-index, when at least one value is None.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The FormValidation instance.
        """
        self.logger.debug("Validating field")

        if self.optional:
            self.logger.debug("Field is optional. Validation passed")
            return FormValidation(validation=True)

        if value is None or (
            isinstance(value, list)
            # empty list or containing None
            and (not value or any(v is None for v in value) is None)
        ):
            self.logger.debug("Validation failed")
            return FormValidation(
                validation=False,
                error_message="You must provide a value for all the table indexes",
            )

        self.logger.debug("Validation passed")
        return FormValidation(validation=True)

    def get_value_as_dict(self) -> dict[str, int | float | str]:
        """
        Returns the form field value. The value is converted from string to the
        correct type stored in the DataFrame column.
        :return: The form field value. With multi-indexed tables, this is a dictionary
        mapping the index name with its value. The index value may be None if it is not
        set.
        """
        table, _ = self.table
        # if data type is not set or table is not valid, skip this
        if is_table_not_empty(table) is False or not self.value.index_types:
            return {}

        values = {}
        names = self.value.index_names
        supported_types = [float, int, complex]
        for vi, value in enumerate(self.value.index_values):
            # value is not supplied (None) or is invalid (False)
            if value is False or value is None:
                value = None
            else:
                # convert value to the correct data type from str if number
                # noinspection PyTypeChecker
                data_type = self.value.index_types[vi]
                if data_type in supported_types:
                    value = data_type(value)
            values[names[vi]] = value

        return values

    def get_value(
        self,
    ) -> None | list[str] | list[int] | list[float] | int | float | str:
        """
        Returns the form field value. For multi-index tables, this is a list whose
        values are sorted based on the index names in the index_col field. With one
        index, the value is a number or a string.
        :return: The form field value.
        """
        dict_value = self.get_value_as_dict()
        # when dict is empty or all values are not supplied or invalid, return None
        if not dict_value or any(v is None for v in dict_value.values()):
            return None

        names = list(dict_value.keys())
        # single-indexed table
        if len(dict_value) == 1:
            return dict_value[names[0]]

        # multi-indexes table
        value_source_field = self.form.find_field_by_name("source")
        selected_source = value_source_field.value()
        # noinspection PyTypeChecker
        value_source_widget: SourceSelectorWidget = value_source_field.widget

        # With model table, the dictionary is already sorted because index names in
        # index_col cannot be changed
        if selected_source == value_source_widget.labels["table"]:
            return list(dict_value.values())
        # With anonymous tables, convert index dict to list using sorting from index_col
        elif selected_source == value_source_widget.labels["anonymous_table"]:
            # noinspection PyTypeChecker
            index_col_widget: IndexColWidget = self.form.find_field_by_name(
                "index_col"
            ).widget
            index_names = index_col_widget.get_value()
            if index_names:
                return [dict_value[index_name] for index_name in index_names]

        return None
