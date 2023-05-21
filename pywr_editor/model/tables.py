from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pywr_editor.model import ComponentsDict, JsonUtils

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig


class Tables(ComponentsDict):
    model: "ModelConfig"
    """ The ModelConfig instance """

    def __init__(self, model: "ModelConfig"):
        """
        Initialise the class.
        :param model: The ModelConfig instance.
        """
        super().__init__(model=model, key="tables")

    def is_used(self, table_name: str) -> int:
        """
        Check if the given table name is being used in the model.
        :param table_name: The name of the table.
        :return: The number of model components using the table. If the table does
        not exist, this returns 0.
        """
        if self.exists(table_name) is False:
            return 0

        dict_utils = JsonUtils(self.model.json).find_str(table_name, "table")
        return dict_utils.occurrences

    def config(self, table_name: str, deep_copy: bool = False) -> dict[str, Any] | None:
        """
        Get the table configuration dictionary.
        :param table_name: The table name to look for.
        :param deep_copy: Returns a copy of the dictionary.
        :return: The table configuration if found, None otherwise.
        """
        if self.exists(table_name) is False:
            return None

        table_dict = self.get_all()[table_name]
        if deep_copy:
            return deepcopy(table_dict)
        return table_dict

    def get_table_extension(self, table_name: str) -> str | None:
        """
        Get the file extension from the table name.
        :param table_name: The table name to look for.
        :return: The file extension or None if the table has no file.
        """
        table_dict = self.config(table_name=table_name)
        # noinspection PyBroadException
        try:
            return Path(table_dict["url"]).suffix
        except Exception:
            return

    def rename(self, table_name: str, new_name: str) -> None:
        """
        Renames a table. This changes the name in the "tables" dictionary and in each
        model component, where the table is referred using the "table": table_name
        syntax.
        :param table_name: The table to rename.
        :param new_name: The new table name.
        :return: None
        """
        if self.exists(table_name) is False:
            return None

        # rename key in "tables"
        self.model.json["tables"][new_name] = self.model.json["tables"].pop(table_name)

        # rename references in model components and in "tables" key
        self.model.json = JsonUtils(self.model.json).replace_str(
            old=table_name, new=new_name, match_key="table"
        )
        self.model.has_changed()
