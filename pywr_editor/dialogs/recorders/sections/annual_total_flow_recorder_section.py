from pywr_editor.form import NodesAndFactorsTableWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class AnnualTotalFlowRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a AnnualTotalFlowRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "nodes_and_factors",
                "field_type": NodesAndFactorsTableWidget,
                "value": {
                    "nodes": form.get_recorder_dict_value("nodes"),
                    "factors": form.get_recorder_dict_value("factors"),
                },
                "help_text": "Store the total flow through the nodes provided "
                + "above for each simulated year. The flow of each node may also "
                + "be scaled, for example, to calculate operational costs",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            agg_func_field_labels=TemporalWidgetField(
                label="Annual aggregation function",
                help_text="Aggregate the total annual volumes for each scenario "
                + "using the provided function",
            ),
            show_ignore_nan_field=True,
            log_name=self.__class__.__name__,
        )

    def filter(self, form_data: dict) -> None:
        """
        Move the dictionary items in "nodes_and_factors" to the form data dictionary.
        :param form_data: The form data.
        :return: None
        """
        for key, value in form_data["nodes_and_factors"].items():
            if value:
                form_data[key] = value
        del form_data["nodes_and_factors"]
