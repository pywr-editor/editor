from typing import Any

from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    IntegerWidget,
    KeatingStreamsWidget,
    TableValuesWidget,
    Validation,
)

from ..node_dialog_form import NodeDialogForm


class KeatingAquiferSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for an Input node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="stream_flows",
                        field_type=KeatingStreamsWidget,
                        label="Streams",
                        value={
                            "stream_flow_levels": form.field_value(
                                "stream_flow_levels"
                            ),
                            "transmissivity": form.field_value("transmissivity"),
                        },
                        help_text="Add and configure the aquifer streams. For each "
                        "stream you need to provide a list of levels and transmissivity"
                        " coefficients for each aquifer level",
                    ),
                    FieldConfig(
                        name="coefficient",
                        label="Calibration coefficient",
                        field_type=FloatWidget,
                        allow_empty=False,
                        value=form.field_value("coefficient"),
                        help_text="The calibration coefficient. In Keating (1982) this "
                        "is the ratio between the aquifer width and length",
                    ),
                    FieldConfig(
                        name="num_additional_inputs",
                        label="Number of additional outflows",
                        field_type=IntegerWidget,
                        field_args={"min_value": 0},
                        default_value=0,
                        value=form.field_value("num_additional_inputs"),
                        help_text="Number of additional outflows (for example for "
                        "direct abstraction or discharge from the aquifer)",
                    ),
                ],
                "Volume-level relationship": [
                    FieldConfig(
                        name="levels",
                        field_type=TableValuesWidget,
                        field_args={"min_total_values": 1},
                        value={"values": form.field_value("levels")},
                        help_text="A list of levels for the level-volume relationship",
                    ),
                    FieldConfig(
                        name="volumes",
                        field_type=TableValuesWidget,
                        validate_fun=self.check_volumes,
                        value={"values": form.field_value("volumes")},
                        help_text="A list of volumes for each level. This is "
                        "optional and the volume can be also calculated by providing "
                        "the aquifer area and storativity parameters below",
                    ),
                    FieldConfig(
                        name="area",
                        field_type=FloatWidget,
                        field_args={"min_value": 0, "suffix": "m<sup>2</sup>"},
                        value=form.field_value("area"),
                        help_text="The area of the aquifer",
                    ),
                    FieldConfig(
                        name="storativity",
                        label="Storativity factors",
                        field_type=TableValuesWidget,
                        validate_fun=self.check_storativity,
                        value={"values": form.field_value("storativity")},
                        help_text="A list of factors whose length should be one "
                        "less than the levels. This is optional if the volumes "
                        "are provided above otherwise the factors are used along "
                        "with the area to calculated the volumes",
                    ),
                ],
            }
        )

    def check_volumes(
        self, name: str, label: str, value: dict[str, list[float]]
    ) -> Validation:
        """
        Checks that the size of volumes matches the number of levels.
        :param name: The field name.
        :param label: The field label.
        :param value: The dictionary with the list of volumes.
        :return: The form validation instance.
        """
        levels = self.form.find_field("levels").value()["values"]
        volumes = value["values"]
        if levels and volumes and len(levels) != len(volumes):
            return Validation(
                f"The number of volumes ({len(volumes)}) must match "
                f"the number of levels ({len(levels)})",
            )
        return Validation()

    def check_storativity(
        self, name: str, label: str, value: dict[str, list[float]]
    ) -> Validation:
        """
        Checks that the size of storativity matches the number of levels minus one.
        :param name: The field name.
        :param label: The field label.
        :param value: The dictionary with the list of factors.
        :return: The form validation instance.
        """
        levels = self.form.find_field("levels").value()["values"]
        factors = value["values"]
        if levels and factors and len(levels) - 1 != len(factors):
            return Validation(
                f"The number of factors ({len(factors)}) must match "
                f"the number of levels ({len(levels)}) minus one",
            )
        return Validation()

    def filter(self, form_data: dict[str, Any]) -> None:
        """
        Unpacks the values for the level-volume relationship.
        :param form_data: The form data.
        :return: None
        """
        for key in ["volumes", "levels", "storativity"]:
            if key in form_data:
                values = form_data[key]["values"]
                if values:
                    form_data[key] = values
                else:
                    del form_data[key]

    def validate(self, form_data: dict[str, Any]) -> Validation:
        """
        Checks that the volumes or the storativity factors and area are provided.
        :param form_data: The form data.
        :return: The validation instance.
        """
        volumes = form_data["volumes"]["values"]
        storativity = form_data["storativity"]["values"]

        # volumes or storativity not provided
        if not volumes and not storativity:
            return Validation(
                "You must provide either the volumes or the storativity factors",
            )
        # only volumes or storativity is needed
        elif volumes and storativity:
            return Validation(
                "You must provide the volumes or the storativity, "
                "but not both values at the same time",
            )
        # area is mandatory with storativity
        elif storativity and "area" not in form_data:
            return Validation(
                "When you provide the storativity factors, the "
                "aquifer area is mandatory",
            )

        return Validation()
