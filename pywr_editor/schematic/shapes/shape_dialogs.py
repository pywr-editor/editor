from typing import TYPE_CHECKING, Any, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
)

from pywr_editor.form import FieldConfig, Form, FormTitle
from pywr_editor.model import BaseShape, ModelConfig
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class ShapeDialog(QDialog):
    def __init__(
        self,
        shape_id: str,
        shape_config: BaseShape,
        form_fields: list[FieldConfig],
        parent: Union[QWindow, "MainWindow"],
        append_form_items: dict[str, Any] | None = None,
    ):
        """
        Initialises the modal dialog.
        :param shape_id: The shape ID.
        :param shape_config: The shape configuration instance.
        :param form_fields: The list of FormFields to use to customise the shape.
        :param parent: The parent widget.
        :param append_form_items: Additional items to appends to the form dictionary
        after the form is submitted. Default to None.
        """
        super().__init__(parent)
        self.app = parent
        self.shape_id = shape_id
        self.shape_config = shape_config
        self.append_form_items = append_form_items
        if self.append_form_items is None:
            self.append_form_items = {}

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title
        self.title = FormTitle("Edit shape")

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close
        )
        # noinspection PyTypeChecker
        self.save_button: QPushButton = button_box.findChild(QPushButton)
        self.save_button.setObjectName("save_button")
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)

        # Form
        self.form = ShapeDialogForm(
            form_fields=form_fields,
            model_config=self.app.model_config,
            save_button=self.save_button,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        self.save_button.clicked.connect(self.form.save)

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle("Edit shape")
        self.setMinimumSize(400, 300)
        self.setWindowModality(Qt.WindowModality.WindowModal)


class ShapeDialogForm(Form):
    def __init__(
        self,
        form_fields: list[FieldConfig],
        model_config: ModelConfig,
        save_button: QPushButton,
        parent: ShapeDialog,
    ):
        """
        Initialises the form.
        :param form_fields: A list of dictionaries of the form fields.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        self.dialog = parent
        self.model_config = model_config

        super().__init__(
            available_fields={"Shape": form_fields},
            save_button=save_button,
            parent=parent,
            direction="vertical",
        )
        self.load_fields()

        # remove the border and padding from the first box
        # noinspection PyTypeChecker
        first_section: QGroupBox = self.findChild(QGroupBox, "Shape")
        first_section.setTitle("")
        first_section.setStyleSheet(
            "QGroupBox{border:0;padding:0;padding-top:15px; margin-top:-15px}"
        )

    def save(self) -> None:
        """
        Validates the form and saves the shape configuration.
        :return: None.
        """
        self.logger.debug("Saving form")

        form_data = self.validate()
        if form_data is False:
            self.logger.debug("Validation failed")
            return

        # add missing required fields
        form_data["id"] = self.dialog.shape_id
        form_data["type"] = self.dialog.shape_config.type
        form_data["x"] = self.dialog.shape_config.x
        form_data["y"] = self.dialog.shape_config.y
        form_data = {**form_data, **self.dialog.append_form_items}

        self.model_config.shapes.update(
            shape_id=self.dialog.shape_id, shape_dict=form_data
        )

        # update the schematic and status bar
        app = self.dialog.app
        app.schematic.reload()
        app.statusBar().showMessage("Updated shape")
