from PySide6.QtCore import Slot, QUuid
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
)
from typing import TYPE_CHECKING
from .parameter_pages_widget import ParameterPagesWidget
from .parameters_list_widget import ParametersListWidget
from .parameters_list_model import ParametersListModel
from pywr_editor.widgets import PushIconButton

from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from .parameters_dialog import ParametersDialog


class ParametersWidget(QWidget):
    def __init__(self, model_config: ModelConfig, parent: "ParametersDialog"):
        """
        Initialises the widget showing the list of available parameters.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent
        self.app = self.dialog.app

        # Model
        self.model = ParametersListModel(
            parameter_names=list(self.model_config.parameters.names),
            model_config=model_config,
        )
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add", parent=self
        )
        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", parent=self
        )

        # Parameters list
        self.list = ParametersListWidget(
            model=self.model, delete_button=self.delete_button, parent=self
        )

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addItem(
            QSpacerItem(10, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_parameter)
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_parameter)

        # Global layout
        layout = QVBoxLayout()
        layout.addWidget(self.list)
        layout.addLayout(button_layout)

        # Style
        self.setLayout(layout)
        self.setMaximumWidth(260)

    @Slot()
    def on_delete_parameter(self) -> None:
        """
        Deletes the selected parameter.
        :return: None
        """
        # check if parameter is being used and warn before deleting
        indexes = self.list.selectedIndexes()
        if len(indexes) == 0:
            return
        parameter_name = self.model.parameter_names[indexes[0].row()]
        total_components = self.model_config.parameters.is_used(parameter_name)

        # ask before deleting
        if self.maybe_delete(parameter_name, total_components, self):
            # remove the parameter from the model
            # noinspection PyUnresolvedReferences
            self.model.layoutAboutToBeChanged.emit()
            self.model.parameter_names.remove(parameter_name)
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.emit()
            self.list.clear_selection()

            # remove the page widget
            page_widget = self.dialog.pages_widget.pages[parameter_name]
            page_widget.deleteLater()
            del self.dialog.pages_widget.pages[parameter_name]

            # delete the parameter from the model configuration
            self.model_config.parameters.delete(parameter_name)

            # update tree and status bar
            if self.app is not None:
                if hasattr(self.app, "components_tree"):
                    self.app.components_tree.reload()
                if hasattr(self.app, "statusBar"):
                    self.app.statusBar().showMessage(
                        f'Deleted parameter "{parameter_name}"'
                    )

    @Slot()
    def on_add_new_parameter(self) -> None:
        """
        Adds a new parameter. This creates a new scenario in the model and adds, and
        selects the form page.
        :return: None
        """
        # generate unique name
        parameter_name = f"Parameter {QUuid().createUuid().toString()[1:7]}"

        # add the dictionary to the model. Default to ConstantParameter
        self.model_config.parameters.update(
            parameter_name, {"type": "constant", "value": 0}
        )

        # add the page
        pages_widget: ParameterPagesWidget = self.dialog.pages_widget
        pages_widget.add_new_page(parameter_name)
        pages_widget.set_current_widget_by_name(parameter_name)

        # add it to the list model
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.parameter_names.append(parameter_name)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        # select the item (this is always added as last)
        self.list.setCurrentIndex(
            self.model.index(self.model.rowCount() - 1, 0)
        )

        # update tree and status bar
        if self.app is not None:
            if hasattr(self.app, "components_tree"):
                self.app.components_tree.reload()
            if hasattr(self.app, "statusBar"):
                self.app.statusBar().showMessage(
                    f'Added new parameter "{parameter_name}"'
                )

    @staticmethod
    def maybe_delete(
        parameter_name: str, total_times: int, parent: QWidget
    ) -> bool:
        """
        Asks user if they want to delete a parameter that's being used by a model
        component.
        :param parameter_name: The parameter name to delete.
        :param total_times: The number of times the parameter is used by the model
        components.
        :param parent: The parent widget.
        :return: True whether to delete the parameter, False otherwise.
        """
        message = f"Do you want to delete {parameter_name}?"
        if total_times > 0:
            times = "time"
            if total_times > 1:
                times = f"{times}s"
            message = (
                f"The parameter '{parameter_name}' you would like to delete is "
                + f"used {total_times} {times} by the model components. If you "
                + "delete it, the model will not be able to run anymore.\n\n"
                + "Do you want to continue?"
            )

        answer = QMessageBox.warning(
            parent,
            "Warning",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            return True
        elif answer == QMessageBox.StandardButton.No:
            return False
        # on discard
        return False
