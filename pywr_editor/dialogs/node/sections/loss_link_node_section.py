from pywr_editor.form import FieldConfig
from pywr_editor.form.widgets.parameter_line_edit_widget import ParameterLineEditWidget

from ..node_dialog_form import NodeDialogForm
from .abstract_node_section import AbstractNodeSection


class LossLinkSection(AbstractNodeSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for an LossLink node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            add_conversion_factor=False,
            additional_fields=[
                FieldConfig(
                    name="loss_factor",
                    field_type=ParameterLineEditWidget,
                    min_value=0,
                    default_value=0,
                    value=form.field_value("loss_factor"),
                    help_text="The proportion of flow that is lost through this node",
                ),
            ],
        )
