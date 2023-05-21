from typing import TYPE_CHECKING, Union

from pywr_editor.form import AbstractModelNodePickerWidget, FormField

if TYPE_CHECKING:
    from pywr_editor.dialogs import ParameterDialogForm, RecorderDialogForm

"""
 This widgets displays a list of available model storage
 nodes and allows the user to pick one.
"""


class StoragePickerWidget(AbstractModelNodePickerWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
        is_mandatory: bool = True,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected node name.
        :param parent: The parent widget.
        :param is_mandatory: Whether at least one parameter should be provided or the
        field can be left empty. Default to True.
        """
        # noinspection PyTypeChecker
        form: Union["ParameterDialogForm", "RecorderDialogForm"] = parent.form
        model_config = form.model_config
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            # filter node types
            include_node_types=model_config.pywr_node_data.get_keys_with_parent_class(
                "AbstractStorage", False  # exclude abstract class
            )
            + model_config.includes.get_keys_with_subclass("AbstractStorage", "node"),
            is_mandatory=is_mandatory,
        )
