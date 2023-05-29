from typing import TYPE_CHECKING, Union

from PySide6.QtCore import QSortFilterProxyModel, Qt, QUuid, Slot
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QDialog, QHBoxLayout

from pywr_editor.model import ModelConfig

from ..base.component_dialog_splitter import ComponentDialogSplitter
from ..base.component_list import ComponentList
from ..base.component_pages import ComponentPages
from .recorder_empty_page import RecorderEmptyPage
from .recorder_page import RecorderPage
from .recorders_list_model import RecordersListModel

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class RecordersDialog(QDialog):
    def __init__(
        self,
        model: ModelConfig,
        selected_name: str = None,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialise the modal dialog.
        :param model: The ModelConfig instance.
        :param selected_name: The name of the recorder to select. Default to None.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent
        self.model = model

        if model.load_error:
            raise ValueError(
                f"The model '{model.json_file}' cannot be loaded "
                f"because: {model.load_error}"
            )
        # Right widget
        self.pages = ComponentPages(self)

        # add pages
        empty_page = RecorderEmptyPage(self.pages)
        self.pages.add_page("empty_page", empty_page, True)
        for name in model.recorders.names:
            self.pages.add_page(name, RecorderPage(name, model, self.pages))

        # Left widget
        # models
        self.list_model = RecordersListModel(
            recorder_names=list(model.recorders.names),
            model_config=model,
        )
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.list_model)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # widget
        self.list = ComponentList(self.list_model, self.proxy_model, empty_page, self)
        self.list.setMaximumWidth(290)

        # setup dialog
        self.setWindowTitle("Model recorders")
        self.setMinimumSize(1000, 750)

        splitter = ComponentDialogSplitter(self.list, self.pages, self.app)

        modal_layout = QHBoxLayout(self)
        modal_layout.setContentsMargins(0, 0, 5, 0)
        modal_layout.addWidget(splitter)

        # select a recorder
        if selected_name is not None:
            found = self.pages.set_page_by_name(selected_name)
            if found is False:
                return

            # noinspection PyTypeChecker
            page: RecorderPage = self.pages.currentWidget()
            page.form.load_fields()
            # set the selected item in the list
            self.list.table.select_row_by_name(selected_name)

    @Slot()
    def add_recorder(self, configuration: dict | None = None) -> None:
        """
        Add a new recorder. This creates a new scenario in the model and adds, and
        selects the form page.
        :param configuration: The configuration to use when the parameter is added. When
        omitted a constant parameter with 0 as value is used.
        :return: None
        """
        # generate unique name
        recorder_name = f"Recorder {QUuid().createUuid().toString()[1:7]}"

        if not configuration:
            status_label = f'Added new recorder "{recorder_name}"'
            # add the dictionary to the model. Default to NodeRecorder
            # NOTE: the node is not specified and the recorder is not valid
            self.model.recorders.update(recorder_name, {"type": "node"})
        else:
            status_label = f'Cloned recorder as "{recorder_name}"'
            self.model.recorders.update(recorder_name, configuration)

        # add the page
        new_page = RecorderPage(recorder_name, self.model, self.pages)
        self.pages.add_page(recorder_name, new_page)
        new_page.show()

        # add it to the list model
        self.list_model.layoutAboutToBeChanged.emit()
        self.list_model.recorder_names.append(recorder_name)
        self.list_model.layoutChanged.emit()

        # select the item
        table = self.list.table
        new_index = self.proxy_model.mapFromSource(
            table.find_index_by_name(recorder_name)
        )
        table.setCurrentIndex(new_index)

        # update tree and status bar
        if self.app is not None:
            if hasattr(self.app, "components_tree"):
                self.app.components_tree.reload()
            if hasattr(self.app, "statusBar"):
                self.app.statusBar().showMessage(status_label)
