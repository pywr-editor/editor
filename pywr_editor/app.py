import logging
import sys
from argparse import ArgumentParser, BooleanOptionalAction

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QApplication

from pywr_editor.dialogs import StartScreen
from pywr_editor.utils import ExceptionHandler, Logging, browse_files

from .main_window import MainWindow


# noinspection PyTypeChecker
def app() -> None:
    """
    Runs the application. This accepts the following arguments:
     * file: the path to the JSON file to open.
     * --create_new: force the editor to open an empty model.
     * --browse: open the editor with the file browser.
     * --log: enable logging.
     * --log_to_file: when supplied with --log, the editor activity is logged to a file
    :return: None
    """
    argument_parser = ArgumentParser(
        description="Open a new pywr model in the pywr editor"
    )

    argument_parser.add_argument("file", type=str, nargs="?")
    argument_parser.add_argument("--create_new", action=BooleanOptionalAction)
    argument_parser.add_argument("--browse", action=BooleanOptionalAction)
    argument_parser.add_argument("--log", action=BooleanOptionalAction)

    # register taskbar icon for Windows
    try:
        # noinspection PyUnresolvedReferences
        from ctypes import windll

        windll.shell32.SetCurrentProcessExplicitAppUserModelID("pywr-editor")
    except ImportError:
        pass

    # create the application
    options = argument_parser.parse_args()
    ExceptionHandler()
    editor = QApplication(sys.argv)
    editor.setWindowIcon(QIcon(":logos/small"))

    # handle the logger
    Logging().configure(file_logging=options.log)
    if not options.log:
        Logging.disable()

    logger = logging.getLogger("main")
    logger.debug(f"Starting application with {sys.argv}")

    # show the welcome screen or the main window
    file = options.file if options.file else None
    create_new = options.create_new if options.create_new else None
    browse = options.browse if options.browse else None

    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # create new model command
    if create_new is not None:
        logger.debug("Opening main window with empty model")
        MainWindow()
    # browse command
    elif browse is not None:
        logger.debug("Browsing for file")
        file = browse_files()
        if file:
            MainWindow(file)
    # file not provided, open the welcome screen
    elif file is None:
        logger.debug("Opening welcome screen")
        dialog = StartScreen()
        dialog.show()
    else:
        logger.debug(f"Opening main window with model file {file}")
        MainWindow(file)

    sys.exit(editor.exec())
