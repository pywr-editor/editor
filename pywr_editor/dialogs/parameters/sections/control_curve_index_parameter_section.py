from pywr_editor.form import (
    ControlCurvesWidget,
    FieldConfig,
    FormSection,
    StoragePickerWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class ControlCurveIndexParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
    ):
        """
        Initialises the form section for ControlCurveIndexParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="storage_node",
                        field_type=StoragePickerWidget,
                        value=form.field_value("storage_node"),
                        help_text="Use the storage from the node specified above to "
                        "return a zero-based index",
                    ),
                    # this is always mandatory
                    FieldConfig(
                        # widget always returns a list of parameters
                        name="control_curves",
                        field_type=ControlCurvesWidget,
                        value={
                            # parameter only supports "control_curves" key
                            "control_curve": None,
                            "control_curves": form.field_value("control_curves"),
                        },
                        help_text="Sort the control curves by the highest to the "
                        "lowest. The parameter returns the zero-based index "
                        "corresponding to the first control curve that is above the "
                        "node storage. For example, if only one control curve is "
                        "provided, the index is either 0 (above) or 1 (below). For two "
                        "curves, the index is either 0 (above both), 1 (in between), or"
                        " 2 (below both) depending on the node storage",
                    ),
                ],
                "Miscellaneous": [form.comment],
            }
        )
