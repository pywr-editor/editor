from dataclasses import dataclass
from datetime import datetime

from pywr_editor.utils import Logging


@dataclass
class Change:
    timestamp: float
    """ The message timestamp """
    message: str
    """ The message to store """


class ChangesTracker:
    def __init__(self):
        """
        Initialises the ChangesTracker class.
        """
        self.changed = False
        self.change_log = []
        self.logger = Logging().logger(self.__class__.__name__)

    def add(self, message: str) -> None:
        """
        Adds a new change to the log. This is ignored if the message contains one of
        the pattern to ignore.
        :param message: The message describing the change.
        :return: None
        """
        self.change_log.append(
            Change(timestamp=datetime.now().timestamp(), message=message)
        )
        self.logger.debug(message)
        self.changed = True

    def reset_change_flag(self) -> None:
        """
        Resets the change flag.
        :return: None
        """
        self.changed = False
