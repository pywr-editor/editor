from PySide6.QtWidgets import QDialog, QStackedWidget, QWidget


class ComponentPages(QStackedWidget):
    def __init__(self, dialog: QDialog):
        super().__init__(dialog)
        self.dialog = dialog

    def add_page(
        self, component_name: str, page: QWidget, active: bool = False
    ) -> None:
        """
        Add a new page to the stack.
        :param :component_name The component name.
        :param :page The pointer to the page widget to add.
        :param :enable Whether to make the new page active. Default to False.
        :return: None
        """
        page.setObjectName(component_name)
        self.addWidget(page)
        if active:
            self.setCurrentWidget(page)

    def set_page_by_name(self, component_name: str) -> bool:
        """
        Set the current widget by providing the component name.
        :param component_name The component name.
        :return: Whether the page with the given name is found.
        """
        # noinspection PyTypeChecker
        page: QWidget = self.findChild(QWidget, component_name)
        if page is not None:
            self.setCurrentWidget(page)
            return True
        return False

    def rename_page(self, component_name: str, new_name: str) -> None:
        """
        Rename a page in the stack.
        :param component_name The component name to change.
        :param new_name: The new name.
        :return: None
        """
        if (page := self.findChild(QWidget, component_name)) is not None:
            # noinspection PyUnresolvedReferences
            page.setObjectName(new_name)
