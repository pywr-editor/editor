import ast
from typing import TYPE_CHECKING, Literal, Union

from pywr_editor.form import FieldConfig, FormSection, Validation
from pywr_editor.utils import Logging

from .widgets.custom_component_external_data_toggle import ComponentExternalDataToggle
from .widgets.dictionary.dictionary_widget import DictionaryWidget

if TYPE_CHECKING:
    from pywr_editor.dialogs import ParameterDialogForm, RecorderDialogForm

"""
 This section allows setting up a custom component dictionary
 by providing key/value pairs with support to external files
 (to configure url, table, index_col, etc. fields)
"""


class AbstractCustomComponentSection(FormSection):
    def __init__(
        self,
        form: Union["ParameterDialogForm", "RecorderDialogForm"],
        section_data: dict,
        component_type: Literal["parameter", "recorder"],
        additional_sections: dict[str, list[str, dict]] | None = None,
    ):
        """
        Initialises the form section for a custom component (recorder or parameter).
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param component_type: The type of model component (parameter or recorder).
        :param additional_sections: Additional sections to add to this section.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)
        self.component_type = component_type
        if additional_sections is None:
            self.additional_sections = {}
        else:
            self.additional_sections = additional_sections

        if component_type == "parameter":
            form_dict = form.parameter_dict
        elif component_type == "recorder":
            form_dict = form.recorder_dict
        else:
            raise ValueError(
                "The component_type parameter can only be 'parameter' or 'recorder'"
            )

        # check if the component was imported using the "include" JSON key
        self.imported = False
        if "imported" in section_data and section_data["imported"]:
            self.imported = True

        # show or hide "custom type" field
        self.form.register_after_render_action(self.toggle_type_field_visibility)

        # Make table fields optional
        optional_col_field = form.column_field
        optional_col_field["field_args"] = {"optional": True}

        optional_index_field = form.index_field
        optional_index_field["field_args"] = {"optional": True}

        # remove type for DictionaryWidget, the type is handle with the dedicated field
        # below
        comp_type = form_dict.pop("type", None)
        self.add_fields(
            {
                "Single key/value pairs": [
                    FieldConfig(
                        name="custom_type",
                        label=f"{self.component_type.title()} type",
                        value=comp_type,
                        allow_empty=False,
                        validate_fun=self._check_python_class,
                        help_text="The name of the Python class with or without the"
                        f"'{self.component_type.title()}' suffix. For example if the "
                        f"class is called 'Custom{self.component_type.title()}', you "
                        f"can use 'Custom{self.component_type.title()}' or 'Custom' as "
                        "type. The type is case-insensitive",
                    ),
                    FieldConfig(
                        name="component_dict",
                        label="Dictionary",
                        field_type=DictionaryWidget,
                        value=form_dict,
                        help_text=f"Configure the {self.component_type} by providing "
                        "its dictionary keys and values",
                    ),
                    FieldConfig(
                        name="external_data",
                        label="Add external data",
                        value=form_dict,
                        field_type=ComponentExternalDataToggle,
                        help_text="Sets the 'url' or 'table' key and any additional "
                        "fields to fetch external data using Pandas and Pywr built-in "
                        "methods (for ex. load_parameter)",
                    ),
                ],
                "External data": [
                    form.source_field_wo_value,
                    # table
                    form.table_field,
                    # anonymous table
                    form.url_field,
                ]
                + form.csv_parse_fields
                + form.excel_parse_fields
                + form.h5_parse_fields,
                form.table_config_group_name: [
                    form.index_col_field,
                    form.parse_dates_field,
                    optional_index_field,
                    optional_col_field,
                ],
                "Miscellaneous": [form.comment],
                **self.additional_sections,
            }
        )

    def toggle_type_field_visibility(self) -> None:
        """
        Shows or hides the type field. The field is hidden when the custom component
        is imported in the "includes" JSON key and its type cannot be changed.
        :return: None
        """
        self.form.change_field_visibility(name="custom_type", show=not self.imported)
        # warn if the custom component is not imported
        if not self.imported:
            self.form.find_field("custom_type").set_warning(
                f"You can autoload an unknown custom {self.component_type} in Pywr "
                "by clicking on the 'Imports' toolbar button and adding the Python "
                "file containing the class"
            )

    def filter(self, form_data: dict) -> None:
        """
        Sets the component type and unpacks the dictionary items.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # if the field is not imported, the type is set in the "custom_type" key,
        # which always store the correct type
        if "custom_type" in form_data:
            self.logger.debug(f"Setting type to {form_data['custom_type']}")
            form_data["type"] = form_data["custom_type"]
            del form_data["custom_type"]

        # unpack the dictionary items
        for key, value in form_data["component_dict"].items():
            form_data[key] = value
        del form_data["component_dict"]

    @staticmethod
    def _check_python_class(name: str, label: str, value: str) -> Validation:
        """
        Checks the component type is a valid Python class name.
        :param name: The field name.
        :param label: The field label.
        :param value: THe field value.
        :return: The validation instance.
        """
        class_definition = f"class {value}: pass"
        # noinspection PyBroadException
        try:
            ast.parse(class_definition)
            return Validation()
        except Exception:
            return Validation("The type must be a valid Python class")
