from dataclasses import dataclass
from typing import Callable, Union, TYPE_CHECKING
from PySide6.QtGui import QIcon, QKeySequence, QAction

if TYPE_CHECKING:
    from pywr_editor import MainWindow


@dataclass
class Action:
    key: str
    """ The key uniquely identifying the action """
    name: str
    """ The action/button name """
    icon: str
    """ The icon """
    tooltip: str
    """ The tooltip """
    show_icon: bool = True
    """ Whether to show the icon. Default to True """
    connection: Union[Callable, None] = None
    """ A function to call when the action is executed. Optional """
    is_disabled: bool = False
    """ Whether to disable the action. Default to False """
    is_checked: bool | None = None
    """ Whether to make the action checkable and checked. Default to None """
    shortcut: QKeySequence | QKeySequence.StandardKey | None = None
    """ The keyword shortcut to run the action. Default to None """
    button_dropdown: bool = False
    """ Whether the action has a dropdown menu on the button. Default to False """
    button_separator: bool = False
    """ Whether the action has a button separator. Default to False """


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

    def add_undo(self, icon: str) -> None:
        """
        Registers the undo action. The action is created via the QUndoStack.
        :param icon: The icon path to set for the action.
        :return: The QAction instance.
        """
        action_obj = self.window.undo_stack.createUndoAction(
            self.window, "Undo"
        )
        action_obj.setData("UndoStack")
        action_obj.setShortcut(QKeySequence.StandardKey.Undo)
        action_obj.setIcon(QIcon(icon))
        action_obj.setToolTip(
            "Undo the last operation "
            + f"[{action_obj.shortcut().toString(QKeySequence.NativeText)}]"
        )

        self.window.addAction(action_obj)
        self.registry["undo"] = action_obj

    def add_redo(self, icon: str) -> None:
        """
        Registers the redo action. The action is created via the QUndoStack.
        :param icon: The icon path to set for the action.
        :return: The QAction instance.
        """
        action_obj = self.window.undo_stack.createRedoAction(
            self.window, "Redo"
        )
        action_obj.setData("UndoStack")
        action_obj.setShortcut(QKeySequence.StandardKey.Redo)
        action_obj.setIcon(QIcon(icon))
        action_obj.setToolTip(
            "Redo the last operation "
            + f"[{action_obj.shortcut().toString(QKeySequence.NativeText)}]"
        )

        self.window.addAction(action_obj)
        self.registry["redo"] = action_obj

    def get(self, key: str) -> QAction:
        """
        Returns the action from its key.
        :param key: The action key.
        :return: The QAction instance.
        """
        if key not in self.registry:
            raise KeyError(f'Invalid action with key "{key}"')

        return self.registry[key]
