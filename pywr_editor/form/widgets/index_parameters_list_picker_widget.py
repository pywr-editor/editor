from typing import TYPE_CHECKING, Union

from pywr_editor.form import AbstractParametersListPickerWidget, FormField

if TYPE_CHECKING:
    from pywr_editor.dialogs import ParameterDialogForm, RecorderDialogForm


"""
 Widgets that provides a list of index parameters.
"""


class IndexParametersListPickerWidget(AbstractParametersListPickerWidget):
    def __init__(
        self,
        name: str,
        value: list[int | float | str | dict] | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The list of parameters or numbers.
        :param parent: The parent widget.
        """
        # noinspection PyTypeChecker
        form: Union["ParameterDialogForm", "RecorderDialogForm"] = parent.form

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            # only include parameters derived from IndexParameter
            include_param_key=form.model_config.pywr_parameter_data.get_keys_with_parent_class(  # noqa: E501
                "IndexParameter"
            )
            + form.model_config.includes.get_keys_with_subclass(
                "IndexParameter", "parameter"
            ),
        )
