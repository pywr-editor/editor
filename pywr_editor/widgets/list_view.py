from typing import TypeVar

import PySide6
from PySide6.QtCore import QAbstractTableModel, Qt, Slot
from PySide6.QtWidgets import QListView, QWidget

from pywr_editor.style import Color, stylesheet_dict_to_str

from .push_button import PushButton
from .push_icon_button import PushIconButton

buttons_type = TypeVar(
    "buttons_type",
    bound=PushButton
    | PushIconButton
    | list[PushButton | PushIconButton]
    | None,
)


class ListView(QListView):
    def __init__(
        self,
        model: QAbstractTableModel | None,
        toggle_buttons_on_selection: buttons_type | None = None,
        parent: QWidget = None,
    ):
        """
        Initialises the ListView widget.
        :param model: The model.
        :param toggle_buttons_on_selection: The buttons to enable when at least one
        table item is selected, or to disable when no item is selected. Default to
        None. When available, the button is disabled if no table item is selected.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        # action buttons
        self.toggle_buttons_on_selection = toggle_buttons_on_selection
        if toggle_buttons_on_selection is not None and not isinstance(
            toggle_buttons_on_selection, list
        ):
            self.toggle_buttons_on_selection = [toggle_buttons_on_selection]

        self.parent = parent
        self.model = model
        # disable buttons when there are no items
        if self.toggle_buttons_on_selection is not None:
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.connect(self.on_layout_changed)

        self.setAlternatingRowColors(False)
        self.setStyleSheet(self.stylesheet())
        self.verticalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
        self.setModel(model)

    def selectionChanged(
        self,
        selected: PySide6.QtCore.QItemSelection,
        deselected: PySide6.QtCore.QItemSelection,
    ) -> None:
        """
        Enables/disables the buttons linked to the table when at least one item
        is selected.
        :param selected: The selected items.
        :param deselected: The deselected items.
        :return: None
        """
        self.toggle_buttons_on_selection: buttons_type
        if self.toggle_buttons_on_selection is not None:
            [
                button.setDisabled(selected.size() == 0)
                for button in self.toggle_buttons_on_selection
            ]
        super().selectionChanged(selected, deselected)

    @Slot()
    def on_layout_changed(self) -> None:
        """
        Disables the buttons when there are no items in the model.
        :return: None
        """
        self.toggle_buttons_on_selection: buttons_type
        [
            button.setDisabled(self.model.rowCount() == 0)
            for button in self.toggle_buttons_on_selection
        ]

    def clear_selection(self) -> None:
        """
        Clear the current selection and restore the focus on the widget. This method
        can be called when the current selection changes (for example when an item is
        deleted from the model).
        :return: None
        """
        self.clearSelection()
        self.setFocus()

    @staticmethod
    def stylesheet(as_string: bool = True) -> str | dict:
        """
        Defines the widget stylesheet.
        :param as_string: Returns the stylesheet as string if True, as dictionary
        otherwise.
        :return: The stylesheet as string.
        """
        style = {
            "ListView": {
                "background": "#FFF",
                "border": f"1px solid {Color('neutral', 300).hex}",
                "border-radius": "6px",
                "outline": 0,
                "color": Color("neutral", 700).hex,
                "::item": {
                    "border": "1px solid transparent",
                    "border-radius": "5px",
                    "color": Color("neutral", 700).hex,
                    "::selected": {
                        "background-color": Color("blue", 300).hex,
                        "color": Color("neutral", 900).hex,
                    },
                    "::hover": {
                        "background-color": Color("neutral", 300).hex,
                    },
                    "::selected::hover": {
                        "background-color": Color("blue", 300).hex,
                    },
                },
            },
        }

        if as_string:
            return stylesheet_dict_to_str(style)
        return style
