from PySide6.QtGui import Qt
from PySide6.QtWidgets import QTreeWidgetItem

from pywr_editor.model import ModelConfig
from pywr_editor.style import Color


class TreeWidgetTable(QTreeWidgetItem):
    def __init__(
        self,
        table_name: str,
        table_dict: dict,
        model_config: ModelConfig,
        parent=None,
    ):
        """
        Initialises the item containing the table name and its attributes.
        :param table_name: The name of the table.
        :param table_dict: The table properties.
        :param model_config: The ModelConfig instance.
        :param: parent: The parent item, if available.
        """
        super().__init__(parent)
        self.name = table_name
        self.table_dict = table_dict
        self.model_config = model_config
        self.addChildren(self.children)

    @property
    def children(self) -> list[QTreeWidgetItem]:
        """
        Collects the table's attributes.
        :return: A list of items.
        """
        items = []
        for attribute_name, attribute_value in self.table_dict.items():
            item = QTreeWidgetItem(self)
            item.setText(0, self.rename_attribute(attribute_name))

            value = str(attribute_value)
            item.setText(1, value)
            item.setToolTip(1, value)

            if (
                attribute_name == "url"
                and self.model_config.does_file_exist(attribute_value) is False
            ):
                item.setBackground(1, Color("red", 100).qcolor)
                item.setData(
                    1, Qt.ItemDataRole.BackgroundRole, Color("red", 100).qcolor
                )
                item.setToolTip(1, f'The file "{value}" cannot be found')

            items.append(item)

        return items

    @staticmethod
    def rename_attribute(attribute: str) -> str:
        """
        Renames an attribute. For example index_col is converted to "Index colum".
        :param attribute: The attribute to convert.
        :return: The converted attribute.
        """
        if attribute == "index_col":
            return "Index colum"

        prop_list = attribute.split("_")
        prop_list[0] = prop_list[0].title()
        return " ".join(prop_list)
