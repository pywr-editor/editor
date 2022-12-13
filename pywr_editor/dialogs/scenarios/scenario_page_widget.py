import PySide6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QDialogButtonBox,
    QPushButton,
)
from typing import TYPE_CHECKING
from .scenario_form_widget import ScenarioFormWidget
from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from .scenario_pages_widget import ScenarioPagesWidget


class ScenarioPageWidget(QWidget):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        parent: "ScenarioPagesWidget",
    ):
        """
        Initialises the widget with the form to edit a scenario.
        :param name: The scenario name.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.name = name
        self.pages = parent
        self.model_config = model_config
        self.scenario_dict = model_config.scenarios.get_config_from_name(name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save)
        # noinspection PyTypeChecker
        save_button: QPushButton = button_box.findChild(QPushButton)
        save_button.setObjectName("save_button")
        save_button.setText("Update scenario")

        # form
        self.form = ScenarioFormWidget(
            name=name,
            model_config=model_config,
            scenario_dict=self.scenario_dict,
            save_button=save_button,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        button_box.accepted.connect(self.form.on_save)

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addWidget(button_box)

    def set_page_title(self, scenario_name: str) -> None:
        """
        Sets the page title.
        :param scenario_name: The scenario name.
        :return: None
        """
        self.title.setText(f"Scenario: {scenario_name}")

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        """
        Loads the form only when the page is requested.
        :param event: The event being triggered.
        :return: None
        """
        if self.form.loaded is False:
            self.form.load_fields()

        super().showEvent(event)
