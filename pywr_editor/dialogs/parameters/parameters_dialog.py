from typing import TYPE_CHECKING, Union

from PySide6.QtGui import QWindow

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import SettingsDialog

from .parameter_pages_widget import ParameterPagesWidget
from .parameters_widget import ParametersWidget

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class ParametersDialog(SettingsDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        selected_parameter_name: str = None,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The ModelConfig instance.
        :param selected_parameter_name: The name of the parameter to select.
        Default to None.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent

        # pages - init before list
        self.pages_widget = ParameterPagesWidget(
            model_config=model_config,
            parent=self,
        )

        # parameters list
        self.model_config = model_config
        self.parameters_list_widget = ParametersWidget(
            model_config=model_config,
            parent=self,
        )

        self.setup(self.parameters_list_widget, self.pages_widget)
        self.setWindowTitle("Model parameters")
        self.setMinimumSize(930, 700)
        # self.setMinimumSize(850, 700)

        # select a parameter
        if selected_parameter_name is not None:
            # load the page and the form fields
            found = self.pages_widget.set_current_widget_by_name(
                selected_parameter_name
            )
            # do not load the form is the parameter is not found
            if found is False:
                return
            # noinspection PyUnresolvedReferences
            self.pages_widget.currentWidget().form.load_fields()

            # set the selected item in the list
            param_list = self.parameters_list_widget.list
            param_list.select_row_by_name(selected_parameter_name)
