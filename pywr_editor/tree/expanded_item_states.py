from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem


class ExpandedItemStates:
    expanded_role_value = "store_expanded"

    def __init__(self):
        """
        Initialises the state list.
        """
        self.expanded_items: list[str] = []

    def add(self, item: QTreeWidgetItem, expand: bool = True) -> None:
        """
        Adds a new item to the expanded state list.
        :param item: The item to add.
        :param expand: Expand the item after adding it to the list.
        :return: None
        """
        name = item.text(0)
        if name not in self.expanded_items:
            self.expanded_items.append(name)
            self.store_state(item)
            if expand:
                item.setExpanded(True)

    def remove(self, item: QTreeWidgetItem, collapse: bool = True) -> None:
        """
        Removes a new item to the expanded state list.
        :param item: The item to delete.
        :param collapse: Collapse the item after removing it to the list.
        :return: None
        """
        name = item.text(0)
        if name in self.expanded_items:
            self.expanded_items.remove(name)
            # self.remove_store_state(item)
            if collapse:
                item.setExpanded(False)

    @staticmethod
    def store_state(item: QTreeWidgetItem) -> None:
        """
        Stops storing the expanded state of an item.
        :param item: The item.
        :return: None
        """
        item.setData(0, Qt.UserRole, ExpandedItemStates.expanded_role_value)

    @staticmethod
    def is_state_stored(item: QTreeWidgetItem) -> bool:
        """
        Checks if an item stores the expanded state.
        :param item: The item.
        :return: Whether the item stores its expanded state.
        """
        return item.data(0, Qt.UserRole) == ExpandedItemStates.expanded_role_value

    @staticmethod
    def remove_store_state(item: QTreeWidgetItem) -> None:
        """
        Stores the expanded state of an item.
        :param item: The item.
        :return: None
        """
        item.setData(0, Qt.UserRole, None)

    def get_all(self) -> list[str]:
        """
        Returns the list of expanded items.
        :return: The expanded items.
        """
        return self.expanded_items

    def clear(self) -> None:
        """
        Clears the expanded state list.
        :return: None
        """
        self.expanded_items = []
