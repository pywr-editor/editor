from typing import Callable, Any, Literal

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QDialogButtonBox,
    QPushButton,
    QWidget,
)
from pywr_editor.form import (
    Form,
    FormField,
    FormCustomWidget,
    FormTitle,
    NodePickerWidget,
    FloatWidget,
)
from pywr_editor.utils import Logging
from pywr_editor.model import ModelConfig

"""
 Defines a dialog widget and form to add a node and its factor
 to the NodesANdFactorTableWidget
"""


class NodesAndFactorsDialog(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        node: str | None,
        factor: float | None,
        mode: Literal["add", "edit"],
        after_form_save: Callable[[str | dict[str, Any], Any], None]
        | None = None,
        additional_data: dict[str, int | list[str]] | None = None,
        parent: QWidget | None = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The model configuration instance.
        :param node: The name of the selected node.
        :param factor: The factor.
        :param mode: The dialog mode ("add" when adding new entry or "edit" when
        editing an existing entry).
        :param after_form_save: A function to execute after the form is saved.
        This receives the form data.
        :param parent: The parent widget. Default to None.
        :param additional_data: A dictionary containing additional data send by the
        parent. This may contain the "model_index" key, whose value is passed back as
        argument to NodesAndFactorsTableWidget when editing an entry and the
        "existing_nodes" key with a list of already added nodes to
        NodesAndFactorsTableWidget.
        """
        super().__init__(parent)
        self.logger = Logging().logger(self.__class__.__name__)
        self.after_form_save = after_form_save
        self.additional_data = additional_data
        self.mode = mode

        # check parent
        if issubclass(parent.__class__, (Form, FormField, FormCustomWidget)):
            raise ValueError(
                "The parent cannot be a form component already instantiated"
            )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title and description
        if mode == "add":
            title = FormTitle("Add a new node")
            description = QLabel("Select a node to add to the list")
        elif mode == "edit":
            title = FormTitle("Edit an existing entry")
            description = QLabel("Change the node or scaling factor")
        else:
            raise ValueError("mode can only be set to 'edit' or 'add'")

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Close
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = button_box.findChild(QPushButton)
        save_button.setObjectName("save_button")
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)

        # Form
        self.form = Form(
            available_fields={
                "Configuration": [
                    {
                        "name": "node",
                        "field_type": NodePickerWidget,
                        "value": node,
                    },
                    {
                        "name": "factor",
                        "field_type": FloatWidget,
                        "default_value": 1,
                        "value": factor,
                    },
                ]
            },
            save_button=save_button,
            direction="vertical",
        )
        self.form.model_config = model_config
        self.form.after_render_actions.append(self.filter_nodes)
        self.form.load_fields()

        # noinspection PyUnresolvedReferences
        button_box.accepted.connect(self.on_save)

        # Layout
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.form)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle(title.text())
        self.setMinimumSize(400, 200)

    def filter_nodes(self) -> None:
        """
        Prevent adding an already existing node to the list. This event
        manipulates the ComboBox in the "node" field.
        :return: None
        """
        if self.mode == "add":
            node_widget = self.form.find_field_by_name("node").widget
            for node_name in self.additional_data["existing_nodes"]:
                index = node_widget.combo_box.findData(node_name)
                if index != -1:
                    node_widget.combo_box.removeItem(index)
                    self.logger.debug(
                        f"Removed '{node_name}' from the node list"
                    )

    @Slot()
    def on_save(self) -> None | bool:
        """
        Slot called when user clicks on the "Save" button.
        The form data are sent to self.after_save().
        :return: None
        """
        self.logger.debug("Saving form")

        form_data = self.form.validate()
        if form_data is False:
            self.logger.debug("Validation failed")
            return False

        # callback function
        self.after_form_save(form_data, self.additional_data)
        # close the window to prevent the user from adding more entries at once
        self.close()
