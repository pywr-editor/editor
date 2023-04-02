import logging
import sys
import traceback
from datetime import datetime

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from .helpers import get_app_path


class ExceptionHandler(QObject):
    exception_signal = Signal(str, str)

    def __init__(self, *args, **kwargs):
        """
        Initialises the exception handler.
        """
        super().__init__(*args, **kwargs)

        # register the hook
        sys.excepthook = self.exception_hook
        # noinspection PyUnresolvedReferences
        self.exception_signal.connect(self.on_exception)

    def exception_hook(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Handles exception.
        :param exc_type: The exception type.
        :param exc_value: The exception value.
        :param exc_traceback: The traceback.
        :return: None
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            log_msg = "\n".join(
                [
                    "".join(traceback.format_tb(exc_traceback)),
                    f"{exc_type.__name__}: {exc_value}",
                ]
            )
            log = logging.getLogger(__name__)
            log_file = (
                get_app_path()
                / f"error_{datetime.now().strftime('%Y%m%d')}.log"
            )
            log.addHandler(logging.FileHandler(log_file))
            # force logs to be on in case the app is started without logging
            logging.disable(logging.INFO)

            log.critical(
                f"Uncaught exception:\n {log_msg}",
                exc_info=(exc_type, exc_value, exc_traceback),
            )
            self.exception_signal.emit(log_msg, str(log_file))

    @staticmethod
    def on_exception(log_msg: str, log_file: str) -> None:
        """
        Shows a message box with the exception and log it.
        :param log_msg: The log message.
        :param log_file: The path to the log file.
        :return: None
        """
        app = QApplication.instance()
        if app is not None:
            QMessageBox().critical(
                app.findChild(QMainWindow),
                "Error",
                f"An unexpected error occurred: \n{log_msg}\n\n"
                + "This error message has been saved in the following log file: "
                + log_file,
            )
            app.exit()
