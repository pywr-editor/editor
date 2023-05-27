from pywr_editor.form import FormSection, Validation

from ..node_dialog_form import NodeDialogForm


class AbstractStorageSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises a general form section for a storage (Storage, VirtualStorage,
        etc.).
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)

    def validate(self, form_data: dict) -> Validation:
        """
        Checks the "initial_volume", "initial_volume_pc" and "max_volume" fields.
        The section must have this fields.
        :param form_data: The form data.
        :return: The validation instance.
        """
        # either initial_volume or initial_volume_pc must be provided
        if "initial_volume" not in form_data and "initial_volume_pc" not in form_data:
            return Validation(
                "You must provide the initial absolute or relative "
                + "volume for the storage",
            )
        # both volumes cannot be provided at the same time if max_volume
        # is not a parameter. Pywr will use "initial_volume_pc" first.
        # To avoid unexpected behaviour, raise an error
        elif (
            "initial_volume" in form_data
            and "initial_volume_pc" in form_data
            # max volume is optional or is a constant
            and (
                "max_volume" not in form_data
                or isinstance(form_data["max_volume"], (int, float))
            )
        ):
            return Validation(
                "You can only provide on type of initial volume (absolute or "
                "relative)",
            )
        # both fields are mandatory if max_volume is a parameter
        elif (
            "max_volume" in form_data
            and not isinstance(form_data["max_volume"], (int, float))
            and (
                "initial_volume" not in form_data
                or "initial_volume_pc" not in form_data
            )
        ):
            return Validation(
                "You must provide both the initial absolute and "
                "relative volume when the 'Maximum storage' is a parameter"
            )

        return Validation()
