from typing import TYPE_CHECKING

from pywr_editor.form import (
    FieldConfig,
    FormSection,
    IntegerWidget,
    ParametersListPickerWidget,
    Validation,
)

if TYPE_CHECKING:
    from ..node_dialog_form import NodeDialogForm


class AbstractPiecewiseLinkNodeSection(FormSection):
    def __init__(
        self,
        form: "NodeDialogForm",
        section_data: dict,
        additional_fields: list[dict] | None = None,
    ):
        """
        Initialises a general form section for a PiecewiseLink node or nodes inheriting
        from it.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param additional_fields: Additional fields to add to the abstract section.
        """
        super().__init__(form, section_data)
        if not additional_fields:
            additional_fields = []

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="nsteps",
                        label="Number of sub links",
                        field_type=IntegerWidget,
                        field_args={"min_value": 1},
                        value=form.field_value("nsteps"),
                        help_text="The number of sub-links to create within the node. "
                        + "A cost and a maximum flow can be set on each link",
                    ),
                    # cost and max flow values can be set to null in the list. This is
                    # not supported by the widget, but the user can set the cost and
                    # max_flow default values of the Node component
                    FieldConfig(
                        name="max_flows",
                        label="Maximum flows",
                        field_type=ParametersListPickerWidget,
                        field_args={"is_mandatory": False},
                        validate_fun=self.check_size,
                        value=form.field_value("max_flows"),
                        help_text="A monotonic increasing list of maximum flows",
                    ),
                    FieldConfig(
                        name="costs",
                        field_type=ParametersListPickerWidget,
                        field_args={"is_mandatory": False},
                        validate_fun=self.check_size,
                        value=form.field_value("costs"),
                        help_text="A list of costs corresponding to the 'Maximum "
                        "flows'",
                    ),
                ]
                + additional_fields,
                "Miscellaneous": [
                    form.comment,
                ],
            }
        )

    def check_size(
        self, name: str, label: str, value: list[str, dict, int, float]
    ) -> Validation:
        """
        Checks that the number of values in "max_flow" and "cost" matches "nsteps".
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The form validation instance.
        """
        nsteps = self.form.find_field("nsteps").value()
        if value and len(value) != nsteps:
            return Validation(
                f"The number of values ({len(value)}) must "
                + f"match the number of sub-links ({nsteps})",
            )
        return Validation()
