import PySide6
from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

from pywr_editor.dialogs.base.component_empty_page import ComponentEmptyPage
from pywr_editor.dialogs.base.component_pages import ComponentPages
from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.widgets import TableView

"""
 The widget listing the available components
"""


class ComponentListView(TableView):
    def __init__(
        self,
        model: QAbstractTableModel,
        proxy_model: QSortFilterProxyModel,
        empty_page: ComponentEmptyPage,
        wrapper: "ComponentList",
    ):
        """
        Initialise the widget showing the list of the model components.
        :param model: The data model.
        :param proxy_model: The model to use as proxy for sorting the data.
        :param empty_page: The pointer to the component empty page.
        :param wrapper: The wrapper parent widget.
        """
        self.empty_page = empty_page
        # noinspection PyTypeChecker
        self.pages: ComponentPages = wrapper.dialog.findChild(ComponentPages)

        super().__init__(model=model, proxy_model=proxy_model, parent=wrapper)

        self.horizontalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(26)
        self.resizeColumnsToContents()

        self.setShowGrid(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # add style
        stylesheet: dict = TableView.stylesheet(as_string=False)
        stylesheet["TableView"]["background"] = "transparent"
        stylesheet["TableView"]["border"] = "0px"
        self.setStyleSheet(stylesheet_dict_to_str(stylesheet))

    def selectionChanged(
        self,
        selected: PySide6.QtCore.QItemSelection,
        deselected: PySide6.QtCore.QItemSelection,
    ) -> None:
        """
        When no parameter is selected, show the empty page.
        :param selected: The selection instance.
        :param deselected: The instance of deselected items.
        :return: None
        """
        if len(selected.indexes()) == 0:
            self.pages.setCurrentWidget(self.empty_page)
        else:
            parameter_name = selected.indexes()[0].data(Qt.ItemDataRole.DisplayRole)
            self.pages.set_page_by_name(parameter_name)
        super().selectionChanged(selected, deselected)


"""
 The widget wrapping the list of available components.
"""


class ComponentList(QWidget):
    def __init__(
        self,
        model: QAbstractTableModel,
        proxy_model: QSortFilterProxyModel,
        empty_page: ComponentEmptyPage,
        dialog: QDialog,
    ):
        """
        Initialise the widget containing the list of components.
        :param model: The model with the component list.
        :param proxy_model: The proxy model with the component list.
        :param empty_page: The widget for the empty page when no component is selected.
        :param dialog: The dialog containing this widget.
        """
        super().__init__()
        self.dialog = dialog

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(290)
        self.setMaximumWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            stylesheet_dict_to_str(
                {
                    "ComponentList": {
                        "background": Color("gray", 100).hex,
                        "border-right": f"1px solid {Color('gray', 400).hex}",
                        "margin-top": "1px",
                    }
                }
            )
        )

        # Add the table
        self.table = ComponentListView(model, proxy_model, empty_page, self)
        # self.table.setModel(proxy_model)
        self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 5, 10)
        layout.addWidget(self.table)
