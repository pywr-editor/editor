from pywr_editor.form import FloatWidget, FormSection
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm


class AbstractNodeSection(FormSection):
    def __init__(
        self,
        form: NodeDialogForm,
        section_data: dict,
        add_conversion_factor: bool = True,
        additional_fields: list[dict] = None,
    ):
        """
        Initialises a general form section for a node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param add_conversion_factor: Whether to add the conversion factor field.
        Some nodes (like the BreakLink) do not make use of the parameter). Default
        to True.
        :param additional_fields: Additional fields to add to the section. Default to
        None.
        """
        super().__init__(form, section_data)
        self.form = form
        self.logger = Logging().logger(self.__class__.__name__)
        self.add_conversion_factor = add_conversion_factor
        if additional_fields:
            self.additional_fields = additional_fields
        else:
            self.additional_fields = []

        # add conversion factor field before any additional fields
        if add_conversion_factor:
            self.additional_fields.append(
                {
                    "name": "conversion_factor",
                    "field_type": FloatWidget,
                    "default_value": 1,
                    "value": self.form.get_node_dict_value("conversion_factor"),
                    "help_text": "The conversion between inflow and outflow for the "
                    + "node",
                },
            )

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": [
                self.form.min_flow_field,
                self.form.max_flow_field,
                self.form.cost_field("flow"),
            ]
            + self.additional_fields
            + [
                self.form.comment,
            ],
        }

        return data_dict
