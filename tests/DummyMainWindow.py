from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QMainWindow
from pywr_editor import Action, Actions, Settings, Schematic
from model import ModelConfig


class MainWindow(QMainWindow):
    warning_info_message = Signal(str, str, str)
    error_message = Signal(str, bool)

    def __init__(self, model_file: str | None = None):
        """
        Draws a schematic on a test window.
        :param model_file: The JSON model file.
        """
        super().__init__()
        self.model_file = model_file
        self.actions = Actions(window=self)
        self.model_config = ModelConfig(model_file)

        # noinspection PyUnresolvedReferences
        self.warning_info_message.connect(self.empty_slot)
        # noinspection PyUnresolvedReferences
        self.error_message.connect(self.empty_slot)

        self.schematic = Schematic(model_config=self.model_config, app=self)
        dummy_actions = ["minimise", "decrease-width", "decrease-height"]
        for action_key in dummy_actions:
            self.actions.add(
                Action(
                    key=action_key,
                    name=action_key,
                    icon="",
                    tooltip="",
                )
            )
        self.schematic.draw()

    @Slot(str, str, str)
    def empty_slot(self, *args) -> None:
        """
        Creates an empty slot.
        :return: None
        """
        pass

    @property
    def editor_settings(self) -> Settings:
        """
        Returns the editor settings.
        :return: The Settings instance.
        """
        return Settings(self.model_file)
