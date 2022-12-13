from ..parameter_dialog_form import ParameterDialogForm
from .abstract_interpolation_section import AbstractInterpolationSection
from pywr_editor.form import StoragePickerWidget, ValuesAndExternalDataWidget
from pywr_editor.utils import Logging


class InterpolatedVolumeParameterSection(AbstractInterpolationSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a InterpolatedVolumeParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": [
                {
                    "name": "node",
                    "label": "Storage node",
                    "field_type": StoragePickerWidget,
                    "value": self.form.get_param_dict_value("node"),
                    "help_text": "This parameter returns an interpolated value using "
                    + "the volume from the storage node provided above",
                },
                {
                    "name": "volumes",
                    "label": "Known volumes",
                    "field_type": ValuesAndExternalDataWidget,
                    "field_args": {"min_total_values": 2},
                    "value": self.form.get_param_dict_value("volumes"),
                    "help_text": "Provide the volumes or x coordinates of the data "
                    + "points to use for the interpolation",
                },
                {
                    "name": "values",
                    "label": "Known values",
                    "field_type": ValuesAndExternalDataWidget,
                    "field_args": {"min_total_values": 2},
                    "value": self.form.get_param_dict_value("values"),
                    "help_text": "Provide the values or y coordinates of the data "
                    + "points to use for the interpolation",
                },
            ],
            "Interpolation settings": self.interp_settings,
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        return data_dict
