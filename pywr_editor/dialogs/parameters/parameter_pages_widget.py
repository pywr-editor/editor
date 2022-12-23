from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStackedWidget

from pywr_editor.model import ModelConfig

from .parameter_empty_page_widget import ParameterEmptyPageWidget
from .parameter_page_widget import ParameterPageWidget

if TYPE_CHECKING:
    from .parameters_dialog import ParametersDialog


class ParameterPagesWidget(QStackedWidget):
    def __init__(self, model_config: ModelConfig, parent: "ParametersDialog"):
        """
        Initialises the widget containing the pages to edit the parameters.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent

        self.empty_page = ParameterEmptyPageWidget()
        self.addWidget(self.empty_page)

        self.pages: dict[str, ParameterPageWidget] = {}
        for name in model_config.parameters.get_all().keys():
            self.add_new_page(name)

        self.set_empty_page()

    def add_new_page(self, parameter_name: str) -> None:
        """
        Adds a new page.
        :param parameter_name: The page or parameter name.
        :return: None
        """
        self.pages[parameter_name] = ParameterPageWidget(
            name=parameter_name, model_config=self.model_config, parent=self
        )
        self.addWidget(self.pages[parameter_name])

    def rename_page(self, parameter_name: str, new_parameter_name: str) -> None:
        """
        Renames a page in the page dictionary.
        :param parameter_name: The parameter name to change.
        :param new_parameter_name: The new parameter name.
        :return: None
        """
        self.pages[new_parameter_name] = self.pages.pop(parameter_name)

    def set_empty_page(self) -> None:
        """
        Sets the empty page as visible.
        :return: None
        """
        self.setCurrentWidget(self.empty_page)

    def set_current_widget_by_name(self, parameter_name: str) -> bool:
        """
        Sets the current widget by providing the parameter name.
        :param parameter_name: The parameter name.
        :return: True if the parameter is found, False otherwise.
        """
        if parameter_name in self.pages.keys():
            self.setCurrentWidget(self.pages[parameter_name])
            return True
        return False
