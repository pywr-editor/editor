from typing import TYPE_CHECKING, Union

from PySide6.QtGui import QWindow

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import SettingsDialog

from .recorder_pages_widget import RecorderPagesWidget
from .recorders_widget import RecordersWidget

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class RecordersDialog(SettingsDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        selected_recorder_name: str = None,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The ModelConfig instance.
        :param selected_recorder_name: The name of the recorder to select.
        Default to None.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent

        # pages - init before list
        self.pages_widget = RecorderPagesWidget(
            model_config=model_config,
            parent=self,
        )

        # recorders list
        self.model_config = model_config
        self.recorders_list_widget = RecordersWidget(
            model_config=model_config,
            parent=self,
        )

        self.setup(self.recorders_list_widget, self.pages_widget)
        self.setWindowTitle("Model recorders")
        self.setMinimumSize(950, 700)
        # self.setMinimumSize(850, 700)

        # select a recorder
        if selected_recorder_name is not None:
            # load the page and the form fields
            found = self.pages_widget.set_current_widget_by_name(
                selected_recorder_name
            )
            # do not load the form is the recorder is not found
            if found is False:
                return
            # noinspection PyUnresolvedReferences
            self.pages_widget.currentWidget().form.load_fields()

            # set the selected item in the list
            recorder_list = self.recorders_list_widget.list
            recorder_list.select_row_by_name(selected_recorder_name)
