from typing import TYPE_CHECKING, Union

from PySide6.QtCore import SIGNAL, QModelIndex, Qt, Slot
from PySide6.QtWidgets import (
    QCompleter,
    QDialog,
    QFrame,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from pywr_editor.dialogs import (
    NodeDialog,
    ParametersDialog,
    RecordersDialog,
    TablesDialog,
)
from pywr_editor.model import ModelConfig
from pywr_editor.style import Color, stylesheet_dict_to_str

from .search_model import ItemType, SearchModel

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class SearchDialog(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        parent: Union["MainWindow", None] = None,
    ):
        """
        Opens the search bar.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.app = parent

        # Autocomplete widget
        model = SearchModel(model_config)
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setModel(model)
        # noinspection PyTypeChecker
        completer.connect(
            completer, SIGNAL("activated(QModelIndex)"), self.open_component
        )

        # Search field
        line_edit = QLineEdit()
        line_edit.setObjectName("search_field")
        line_edit.setCompleter(completer)
        line_edit.setMinimumWidth(600)
        line_edit.setMinimumHeight(40)
        line_edit.setStyleSheet("#search_field { font-size: 20px }")

        # Description
        description = QLabel("Start typing to find and open any model components")
        description.setStyleSheet("font-size: 11px; border: 0")

        self.setObjectName("search_dialog")
        # remove the dialog style
        self.setStyleSheet("QDialog#search_dialog { background: none; border: none}")
        self.setModal(True)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Popup
            | Qt.CustomizeWindowHint
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # child layout
        layout = QVBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(description)

        # add container with background
        frame = QFrame()
        frame.setStyleSheet(
            stylesheet_dict_to_str(
                {
                    "QFrame": {
                        "background": Color("gray", 100).hex,
                        "border": f"1px solid {Color('gray', 300).hex}",
                        "border-radius": "5px",
                    }
                }
            )
        )
        frame.setLayout(layout)

        # dialog layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(frame)

        self.setLayout(main_layout)
        line_edit.setFocus()
        self.open()

    @Slot(QModelIndex)
    def open_component(self, index: QModelIndex) -> None:
        """
        Opens the dialog to edit the selected component.
        :param index: The selected model index.
        :return: None
        """
        comp_name = index.data(Qt.ItemDataRole.EditRole)
        comp_type = index.data(Qt.ItemDataRole.UserRole)
        dialog = None

        if comp_type == ItemType.NODE.value:
            dialog = NodeDialog(
                model_config=self.model_config,
                node_name=comp_name,
                parent=self.app,
            )
        elif comp_type == ItemType.RECORDER.value:
            dialog = RecordersDialog(
                model_config=self.model_config,
                selected_recorder_name=comp_name,
                parent=self.app,
            )
        elif comp_type == ItemType.PARAMETER.value:
            dialog = ParametersDialog(
                model=self.model_config,
                selected_parameter_name=comp_name,
                parent=self.app,
            )
        elif comp_type == ItemType.TABLE.value:
            dialog = TablesDialog(
                model_config=self.model_config,
                selected_table_name=comp_name,
                parent=self.app,
            )

        if dialog:
            dialog.show()
            self.close()
