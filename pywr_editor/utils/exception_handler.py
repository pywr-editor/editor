import sys
import traceback
import logging
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QMessageBox, QMainWindow


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
            exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = "\n".join(
                [
                    "".join(traceback.format_tb(exc_traceback)),
                    f"{exc_type.__name__}: {exc_value}",
                ]
            )
            log = logging.getLogger(__name__)
            log_file = (
                Path(__file__).parent
                / f"error_{datetime.now().strftime('%Y%m%d_%H%M')}.log"
            )
            handler = logging.FileHandler(log_file)
            log.addHandler(handler)
            log.critical(f"Uncaught exception:\n {0}", exc_info=exc_info)

            # noinspection PyUnresolvedReferences
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
