import logging
import os
from datetime import datetime
from logging.config import dictConfig


class Logging:
    def __init__(self):
        self.init: bool = False

    def configure(self) -> None:
        """
        Configures the logging facility for the first time.
        """
        if self.init is True:
            return

        config = {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "standard": {
                    "format": "[%(asctime)s] - %(levelname)s - %(name)s - %(message)s"
                },
            },
            "handlers": {
                "console_handler": {
                    # "level": "DEBUG",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "": {  # root logger
                    "level": "DEBUG",
                    "handlers": [
                        "console_handler",
                    ],
                },
            },
        }
        if os.getenv("FILE_LOGGING") == str(1):
            config["handlers"]["file_handler"] = {
                # "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.FileHandler",
                "filename": f"pywr-editor-{datetime.now().strftime('%Y-%m-%d_%H:%M')}"
                + ".log",
                "mode": "a",
            }
            config["loggers"][""]["handlers"].append("file_handler")

        dictConfig(config)
        self.init = True

    def logger(self, name: str) -> logging.Logger:
        """
        Returns the logger.
        :param name: The logger name to use.
        :return: The Logger instance.
        """
        return logging.getLogger(name)

    @staticmethod
    def disable() -> None:
        """
        Disable logging.
        :return: None
        """
        logging.disable(logging.CRITICAL)
