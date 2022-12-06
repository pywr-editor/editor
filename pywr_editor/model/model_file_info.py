import os
from datetime import datetime


class ModelFileInfo:
    def __init__(self, config_file: str | None):
        """
        Initialises the class.
        :param config_file: The path to the model JSON file.
        """
        self.file_name: str | None = None
        self.file_path: str | None = None
        self.size = "0 KiB"
        self.created_on = "N/A"
        self.last_modified_on = "N/A"

        if config_file is not None and os.path.exists(config_file):
            self.file_name = os.path.basename(config_file)
            self.file_path = os.path.abspath(os.path.dirname(config_file))
            self.size = f"{round(os.path.getsize(config_file) / 1024, 2)} KiB"
            self.created_on = datetime.fromtimestamp(
                os.path.getctime(config_file)
            ).strftime("%d-%m-%Y %H:%M")
            self.last_modified_on = datetime.fromtimestamp(
                os.path.getmtime(config_file)
            ).strftime("%d-%m-%Y %H:%M")
