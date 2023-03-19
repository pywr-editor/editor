from typing import TYPE_CHECKING, Any, TypeVar, Union

from PySide6.QtCore import QSize, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from pywr_editor.form import (
    FormCustomWidget,
    FormField,
    FormValidation,
    NodesAndFactorsDialog,
    NodesAndFactorsModel,
)
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import PushIconButton, TableView

if TYPE_CHECKING:
    from pywr_editor.dialogs.node.node_dialog_form import NodeDialogForm

"""
 This widget provides a list of nodes and factors. This is
 used by the AnnualTotalFlowRecorderSection.
"""

value_type = TypeVar("value_type", bound=dict[str, list | None])


class NodesAndFactorsTableWidget(FormCustomWidget):
    def __init__(self, name: str, value: value_type, parent: FormField):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: A dictionary containing the list of nodes and factors with the
        "nodes" and "factors" keys.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)
        self.form: "NodeDialogForm"
        self.model_config = self.form.model_config
        self.value, self.warning_message = self.sanitise_value(value)

        # # noinspection PyCallingNonCallable
        self.model = NodesAndFactorsModel(values=self.value)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.connect(self.form.on_field_changed)

        # Action buttons
        buttons_layout = QHBoxLayout()
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add", small=True
        )
        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_row)
        self.add_button.setToolTip("Add a new node")

        self.edit_button = PushIconButton(
            icon=":misc/edit",
            label="Edit",
            small=True,
            icon_size=QSize(10, 10),
        )
        self.edit_button.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.edit_button.clicked.connect(self.on_edit_row)
        self.edit_button.setToolTip(
            "Edit the node and factor of the selected row"
        )

        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", small=True
        )
        self.delete_button.setDisabled(True)
        self.delete_button.setToolTip("Delete the selected row")
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_row)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)

        # Table
        self.table = TableView(
            model=self.model,
            toggle_buttons_on_selection=[self.delete_button, self.edit_button],
        )
        self.table.setColumnWidth(0, 450)
        self.table.setMaximumHeight(400)

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addLayout(buttons_layout)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")

        if self.warning_message:
            self.logger.debug(self.warning_message)
        self.form_field.set_warning_message(self.warning_message)

    @Slot()
    def on_delete_row(self) -> None:
        """
        Deletes the selected rows.
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_row Slot from {get_signal_sender(self)}"
        )
        indexes = self.table.selectedIndexes()
        row_indexes = [index.row() for index in indexes]

        # Preserve only the row values that are not selected
        new_node_values = []
        new_factor_values = []
        for index, sub_values in enumerate(self.model.nodes):
            if index not in row_indexes:
                new_node_values.append(sub_values)
                new_factor_values.append(self.model.factors[index])
            else:
                self.logger.debug(
                    f"Deleted index {index} with values {sub_values}"
                )

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.nodes = new_node_values
        self.model.factors = new_factor_values
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        self.table.clear_selection()

    @Slot()
    def on_edit_row(self) -> None:
        """
        Opens the dialog to edit an existing row.
        :return: None
        """
        current_index = (
            self.table.selectionModel().selection().indexes()[0].row()
        )
        dialog = NodesAndFactorsDialog(
            model_config=self.model_config,
            node=self.model.nodes[current_index],
            factor=self.model.factors[current_index],
            mode="edit",
            additional_data={"model_index": current_index},
            after_form_save=self.on_form_save,
            parent=self.form.parent,
        )
        dialog.open()

    @Slot()
    def on_add_row(self) -> None:
        """
        Opens the dialog to add a new row.
        :return: None
        """
        dialog = NodesAndFactorsDialog(
            model_config=self.model_config,
            node=None,
            factor=None,
            mode="add",
            additional_data={"existing_nodes": self.model.nodes},
            after_form_save=self.on_form_save,
            parent=self.form.parent,
        )
        dialog.open()

    def on_form_save(
        self,
        form_data: dict[str, Any],
        additional_data: dict[str, int | list[str]] | None,
    ) -> None:
        """
        Updates the values for the node and factor.
        :param form_data: The form data from NodesAndFactorsDialog.
        :param additional_data: This is the dictionary containing the
        model index of the row to update.
        :return: None
        """
        self.logger.debug(
            f"Running post-saving action on_form_save with value {form_data}"
        )

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()

        # update an existing row
        factor = (
            form_data["factor"]
            if "factor" in form_data
            else self.get_default_factor
        )
        if additional_data is not None and "model_index" in additional_data:
            index = additional_data["model_index"]
            self.model.nodes[index] = form_data["node"]
            self.model.factors[index] = factor
        # new row
        else:
            self.model.nodes.append(form_data["node"])
            self.model.factors.append(factor)

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    def sanitise_value(self, value: value_type) -> [value_type, str | None]:
        """
        Sanitises the field values.
        :param value: The values to sanitise.
        :return: The values and the warning message.
        """
        self.logger.debug(f"Sanitising value {value}")
        message = None
        _value = self.get_default_value()

        # check if nodes are provided
        if value["nodes"] is None:
            self.logger.debug("The nodes are not provided. Using default")
        # nodes and factors (if provided) must be lists
        elif not isinstance(value["nodes"], list) or (
            value["factors"] and not isinstance(value["factors"], list)
        ):
            message = (
                "The nodes and factors provided in the model configuration "
            )
            message += "must be valid lists"
        # both list must have the same size when factors are provided
        elif value["factors"] and len(value["nodes"]) != len(value["factors"]):
            message = "The number of nodes must match the number of factors"
        # the list of nodes must contain strings
        elif any([not isinstance(el, str) for el in value["nodes"]]) is True:
            message = (
                "The list of nodes provided in the model configuration must "
            )
            message += "contain only strings"
        # the list of nodes must contain existing nodes
        elif (
            any(
                [
                    self.model_config.nodes.find_node_index_by_name(el) is None
                    for el in value["nodes"]
                ]
            )
            is True
        ):
            message = (
                "One or more nodes provided in the model configuration do "
                + "not exist"
            )
        # the list of factors can contain only number when provided
        elif value["factors"] and (
            any([not isinstance(el, (int, float)) for el in value["factors"]])
            is True
        ):
            message = (
                "The list of factors provided in the model configuration must "
            )
            message += "contain only number"
        # assign final values
        else:
            if value["nodes"] is None:
                _value["nodes"] = []
            else:
                _value["nodes"] = value["nodes"]
                # do not assign factors if nodes are not valid
                # if empty, use and show default value
                if not value["factors"]:
                    _value["factors"] = [self.get_default_factor] * len(
                        _value["nodes"]
                    )
                else:
                    _value["factors"] = value["factors"]

        return _value, message

    def get_default_value(self) -> value_type:
        """
        The field default value.
        :return: A dictionary with an empty list of nodes and factors.
        """
        return {"nodes": [], "factors": []}

    @property
    def get_default_factor(self) -> int:
        """
        The factor default value.
        :return: Returns 1.
        """
        return 1

    def get_value(self) -> Union[value_type, None]:
        """
        Returns the widget value.
        :return: A list containing the lists of nodes and factors.
        """
        # factor always defaults to 1. Return None if it contains all ones
        factors = self.model.factors
        if all([f == self.get_default_factor for f in factors]):
            factors = []
        return {"nodes": self.model.nodes, "factors": factors}

    def reset(self) -> None:
        """
        Resets the widget. This sets an empty list on the model.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.nodes = self.get_default_value()["nodes"]
        self.model.factors = self.get_default_value()["factors"]
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        self.table.clear_selection()

    def validate(
        self, name: str, label: str, value: value_type
    ) -> FormValidation:
        """
        Checks that the widget is not empty.
        :param name: The field name.
        :param label: The field label.
        :param value: The widget value.
        :return: The validation instance.
        """
        # nodes are mandatory, factors are not
        if not value["nodes"]:
            return FormValidation(
                validation=False,
                error_message="You must provide one or more nodes to calculate the "
                + "annual total flow",
            )

        return FormValidation(validation=True)

    def after_validate(
        self, form_dict: dict[str, Any], form_field_name: str
    ) -> None:
        """
        Unpacks the widget value.
        :param form_dict: The dictionary containing the data of the form
        the widget is child of.
        :param form_field_name: The name of the parent FormField.
        :return: None
        """
        for key, value in form_dict["nodes_and_factors"].items():
            if value:
                form_dict[key] = value
        del form_dict["nodes_and_factors"]
