from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from pywr_editor.model import JsonUtils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig


@dataclass
class Tables:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def get_all(self) -> dict[str, dict] | None:
        """
        Returns the list of tables.
        :return: The table dictionary with the table name as key and its properties
        as value.
        """
        return self.model.json["tables"]

    @property
    def count(self) -> int:
        """
        Returns the total number of tables.
        :return: The edges count.
        """
        return len(self.get_all())

    @property
    def names(self) -> list[str]:
        """
        Returns the table names.
        :return: The tables names.
        """
        tables = self.get_all()
        if tables is None:
            return list()
        return list(self.get_all().keys())

    def does_table_exist(self, table_name: str) -> bool:
        """
        Checks if a table name exists.
        :param table_name: The table name to check.
        :return: True if the table exists, False otherwise.
        """
        if self.get_all() is None or table_name not in self.get_all().keys():
            return False
        return True

    def is_used(self, table_name: str) -> int:
        """
        Checks if the given table name is being used in the model.
        :param table_name: The name of the table.
        :return: The number of model components using the table. If the table does
        not exist, this returns 0.
        """
        if self.does_table_exist(table_name) is False:
            return 0

        dict_utils = JsonUtils(self.model.json).find_str(table_name, "table")
        return dict_utils.occurrences

    def delete(self, table_name: str) -> None:
        """
        Deletes a table from the model.
        :param table_name: The table name to delete.
        :return: None
        """
        if self.does_table_exist(table_name) is False:
            return None

        try:
            del self.model.json["tables"][table_name]
            self.model.changes_tracker.add(f"Deleted table {table_name}")
        except KeyError:
            pass

    def get_table_config_from_name(
        self, table_name: str, deep_copy: bool = False
    ) -> dict[str, Any] | None:
        """
        Gets the table configuration dictionary.
        :param table_name: The table name to look for.
        :param deep_copy: Returns a copy of the dictionary.
        :return: The table configuration if found, None otherwise.
        """
        if self.does_table_exist(table_name) is False:
            return None

        table_dict = self.get_all()[table_name]
        if deep_copy:
            return deepcopy(table_dict)
        return table_dict

    def update(self, table_name: str, table_dict: dict) -> None:
        """
        Replaces the table dictionary for an existing table or create a new one if it
        does not exist.
        :param table_name: The table name to add or update.
        :param table_dict: The table dictionary with the fields to add or update.
        :return: None
        """
        self.model.json["tables"][table_name] = table_dict
        self.model.changes_tracker.add(
            f"Updated table {table_name} with the following values: {table_dict}"
        )

    def rename(self, table_name: str, new_name: str) -> None:
        """
        Renames a table. This changes the name in the "tables" dictionary and in each
        model component, where the table is referred using the "table": table_name
        syntax.
        :param table_name: The table to rename.
        :param new_name: The new table name.
        :return: None
        """
        if self.does_table_exist(table_name) is False:
            return None

        # rename key in "tables"
        self.model.json["tables"][new_name] = self.model.json["tables"].pop(
            table_name
        )

        # rename references in model components and in "tables" key
        self.model.json = JsonUtils(self.model.json).replace_str(
            old=table_name, new=new_name, match_key="table"
        )
        self.model.changes_tracker.add(
            f"Change table name from {table_name} to {new_name}"
        )
