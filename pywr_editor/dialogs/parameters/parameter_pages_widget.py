from typing import TYPE_CHECKING

from PySide6.QtCore import QUuid, Slot
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

        self.empty_page = ParameterEmptyPageWidget(self)
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

    @Slot()
    def on_add_new_parameter(self) -> None:
        """
        Adds a new parameter. This creates a new scenario in the model and adds, and
        selects the form page.
        :return: None
        """
        list_widget = self.dialog.parameters_list_widget.list
        list_model = self.dialog.parameters_list_widget.model
        proxy_model = self.dialog.parameters_list_widget.proxy_model

        # generate unique name
        parameter_name = f"Parameter {QUuid().createUuid().toString()[1:7]}"

        # add the dictionary to the model. Default to ConstantParameter
        self.model_config.parameters.update(
            parameter_name, {"type": "constant", "value": 0}
        )

        # add the page
        pages_widget: ParameterPagesWidget = self.dialog.pages_widget
        pages_widget.add_new_page(parameter_name)
        pages_widget.set_current_widget_by_name(parameter_name)

        # add it to the list model
        # noinspection PyUnresolvedReferences
        list_model.layoutAboutToBeChanged.emit()
        list_model.parameter_names.append(parameter_name)
        # noinspection PyUnresolvedReferences
        list_model.layoutChanged.emit()
        # select the item
        new_index = proxy_model.mapFromSource(
            list_widget.find_index_by_name(parameter_name)
        )
        list_widget.setCurrentIndex(new_index)

        # update tree and status bar
        if self.dialog.app is not None:
            if hasattr(self.dialog.app, "components_tree"):
                self.dialog.app.components_tree.reload()
            if hasattr(self.dialog.app, "statusBar"):
                self.dialog.app.statusBar().showMessage(
                    f'Added new parameter "{parameter_name}"'
                )
