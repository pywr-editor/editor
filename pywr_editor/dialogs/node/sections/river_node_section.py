from pywr_editor.form import FormSection
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm


class RiverSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises a form section for a River node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form = form
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.logger.debug("Registering form")

        # river node is a Link. Even though min_flow and cost
        # can be set, pywr manual suggests to set the max_flow
        # only
        data_dict = {
            "Configuration": [
                self.form.max_flow_field,
                self.form.comment,
            ],
        }

        return data_dict
