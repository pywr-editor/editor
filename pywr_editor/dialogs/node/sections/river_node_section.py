from pywr_editor.form import FormSection

from ..node_dialog_form import NodeDialogForm


class RiverSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises a form section for a River node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)

        # river node is a Link. Even though min_flow and cost
        # can be set, pywr manual suggests to set the max_flow
        # only
        self.add_fields(
            {
                "Configuration": [
                    form.max_flow_field,
                    form.comment,
                ],
            }
        )
