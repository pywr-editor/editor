from typing import TYPE_CHECKING, Union

from PySide6.QtCore import QSortFilterProxyModel, Qt, QUuid
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QDialog, QHBoxLayout

from pywr_editor.model import ModelConfig

from ..base.component_list import ComponentList
from ..base.component_pages import ComponentPages
from .parameter_empty_page import ParameterEmptyPage
from .parameter_page import ParameterPage
from .parameters_list_model import ParametersListModel

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class ParametersDialog(QDialog):
    def __init__(
        self,
        model: ModelConfig,
        selected_parameter_name: str = None,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialise the modal dialog.
        :param model: The ModelConfig instance.
        :param selected_parameter_name: The name of the parameter to select.
        Default to None.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent
        self.model = model

        if model.load_error:
            raise ValueError(
                f"The model '{model.json_file}' cannot be loaded "
                + f"because: {model.load_error}"
            )

        # Right widget
        self.pages = ComponentPages(self)

        # add pages
        empty_page = ParameterEmptyPage(self.pages)
        self.pages.add_page("empty_page", empty_page, True)
        for name in model.parameters.names:
            self.pages.add_page(name, ParameterPage(name, model, self.pages))

        # Left widget
        # models
        self.list_model = ParametersListModel(
            parameter_names=model.parameters.names,
            model_config=model,
        )
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.list_model)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # widget
        self.list = ComponentList(self.list_model, self.proxy_model, empty_page, self)
        self.list.setMaximumWidth(290)

        # setup dialog
        self.setWindowTitle("Model parameters")
        self.setMinimumSize(1000, 750)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        modal_layout = QHBoxLayout()
        modal_layout.setContentsMargins(0, 0, 5, 0)
        modal_layout.addWidget(self.list)
        modal_layout.addWidget(self.pages)
        self.setLayout(modal_layout)

        # select a parameter
        if selected_parameter_name is not None:
            found = self.pages.set_page_by_name(selected_parameter_name)
            if found is False:
                return

            # noinspection PyTypeChecker
            page: ParameterPage = self.pages.currentWidget()
            page.form.load_fields()
            # set the selected item in the list
            self.list.table.select_row_by_name(selected_parameter_name)

    def add_parameter(self, configuration: dict | None = None) -> None:
        """
        Adds a new parameter. This creates a new scenario in the model and adds, and
        selects the form page.
        :param configuration: The configuration to use when the parameter is added. When
        omitted a constant parameter with 0 as value is used.
        :return: None
        """
        # generate unique name
        parameter_name = f"Parameter {QUuid().createUuid().toString()[1:7]}"

        if not configuration:
            status_label = f'Added new parameter "{parameter_name}"'
            self.model.parameters.update(
                parameter_name, {"type": "constant", "value": 0}
            )
        else:
            status_label = f'Cloned parameter as "{parameter_name}"'
            self.model.parameters.update(parameter_name, configuration)

        # add the page
        new_page = ParameterPage(parameter_name, self.model, self.pages)
        self.pages.add_page(parameter_name, new_page)
        new_page.show()

        # add it to the list model
        self.list_model.layoutAboutToBeChanged.emit()
        self.list_model.parameter_names.append(parameter_name)
        self.list_model.layoutChanged.emit()

        # select the item
        table = self.list.table
        new_index = self.proxy_model.mapFromSource(
            table.find_index_by_name(parameter_name)
        )
        table.setCurrentIndex(new_index)

        # update tree and status bar
        if self.app is not None:
            if hasattr(self.app, "components_tree"):
                self.app.components_tree.reload()
            if hasattr(self.app, "statusBar"):
                self.app.statusBar().showMessage(status_label)
