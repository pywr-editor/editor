from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Union

from PySide6.QtGui import QAction, QIcon, QKeySequence

if TYPE_CHECKING:
    from pywr_editor import MainWindow


@dataclass
class Action:
    key: str
    name: str
    icon: str
    tooltip: str
    show_icon: bool = True
    connection: Union[Callable, None] = None
    is_disabled: bool = False
    is_checked: bool | None = None
    shortcut: QKeySequence | None = None
    button_dropdown: bool = False
    button_separator: bool = False


class Actions:
    def __init__(self, window: "MainWindow"):
        self.window = window
        self.registry: dict[str, QAction] = {}

    def add(self, action: Action) -> None:
        """
        Register a new action in the main window.
        :param action: The Action object.
        :return: None.
        """
        action_obj = QAction(QIcon(action.icon), action.name, self.window)
        # noinspection PyUnresolvedReferences
        action_obj.triggered.connect(action.connection)
        action_obj.setIconVisibleInMenu(action.show_icon)
        action_obj.setDisabled(action.is_disabled)

        # if action.data is not None:
        #     action_obj.setData(action.data)
        if action.shortcut is not None:
            action_obj.setShortcut(action.shortcut)

        shortcut_text = action_obj.shortcut().toString(QKeySequence.NativeText)
        if shortcut_text:
            action_obj.setToolTip(
                f"{action.tooltip} ["
                + f"{action_obj.shortcut().toString(QKeySequence.NativeText)}]"
            )
        else:
            action_obj.setToolTip(action.tooltip)

        if action.is_checked is not None:
            action_obj.setCheckable(True)
            action_obj.setChecked(action.is_checked)

        # add button options
        data = {}
        if action.button_separator is True:
            data["separator"] = True
        if action.button_dropdown is not None:
            data["dropdown"] = action.button_dropdown
        action_obj.setData(data)

        self.window.addAction(action_obj)
        self.registry[action.key] = action_obj

    def get(self, key: str) -> QAction:
        """
        Returns the action from its key.
        :param key: The action key.
        :return: The QAction instance.
        """
        if key not in self.registry:
            raise KeyError(f'Invalid action with key "{key}"')

        return self.registry[key]
