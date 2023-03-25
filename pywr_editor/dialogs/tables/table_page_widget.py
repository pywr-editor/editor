from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QMessageBox, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import JsonUtils, ModelConfig
from pywr_editor.utils import Logging, get_columns, maybe_delete_component
from pywr_editor.widgets import PushButton

from .table_form_widget import TableFormWidget
from .table_url_widget import TableUrlWidget
from .tables_list_model import TablesListModel

if TYPE_CHECKING:
    from .table_pages_widget import TablePagesWidget


class TablePageWidget(QWidget):
    def __init__(
        self, name: str, model_config: ModelConfig, parent: "TablePagesWidget"
    ):
        """
        Initialises the widget with the form to edit a table.
        :param name: The table name.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        super().__init__(parent)
        self.name = name
        self.pages = parent
        self.model_config = model_config
        self.table_dict = model_config.tables.get_table_config_from_name(name)
        self.logger.debug(f"Initialising page for table named '{name}'")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # buttons
        close_button = PushButton("Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(parent.dialog.reject)

        # noinspection PyTypeChecker
        self.save_button = PushButton("Save")
        self.save_button.setObjectName("save_button")
        # noinspection PyUnresolvedReferences
        self.save_button.clicked.connect(self.on_save)

        add_button = PushButton("Add new")
        add_button.setObjectName("add_button")
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(parent.on_add_new_table)

        delete_button = PushButton("Delete")
        delete_button.setObjectName("delete_button")
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.on_delete_table)

        button_box = QHBoxLayout()
        button_box.addWidget(add_button)
        button_box.addStretch()
        button_box.addWidget(self.save_button)
        button_box.addWidget(delete_button)
        button_box.addWidget(close_button)

        # form
        self.form = TableFormWidget(
            name=name,
            model_config=model_config,
            table_dict=self.table_dict,
            save_button=self.save_button,
            parent=self,
        )

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

    def set_page_title(self, table_name: str) -> None:
        """
        Sets the page title.
        :param table_name: The table name.
        :return: None
        """
        self.title.setText(f"Table: {table_name}")

    def maybe_new_index(self) -> bool:
        """
        Asks user if they want to change the table index.
        :return: True whether to continue, False otherwise.
        """
        dict_utils = JsonUtils(self.model_config.json)
        output = dict_utils.find_str(self.name, match_key="table")

        if output.occurrences == 0:
            return True

        comp_list = [f"   - {p.replace('/table', '')}" for p in output.paths]
        # truncate list if it's too long
        if len(comp_list) > 10:
            comp_list = comp_list[0:10] + [
                f"\n and {len(comp_list) - 10} more components"
            ]

        answer = QMessageBox.warning(
            self,
            "Warning",
            "You are going to change the index names of the table. This may break the "
            + "configuration of the following model components, if they rely on the "
            + "table index to fetch their values: \n\n"
            + "\n".join(comp_list)
            + "\n\n"
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            return True
        # on discard or No
        return False

    @Slot()
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Update" button. Only visible fields are
         exported.
        :return: None
        """
        form_data = self.form.validate()
        if form_data is False:
            return

        # delete empty fields (None or empty list - for example parse_dates is
        # optional)
        keys_to_delete = []
        [
            keys_to_delete.append(key)
            for key, value in form_data.items()
            if not value
        ]
        [form_data.pop(key, None) for key in keys_to_delete]

        # check changes to index
        prev_index = self.form.get_table_dict_value("index_col")
        new_index = (
            form_data["index_col"] if "index_col" in form_data.keys() else None
        )
        url_widget: TableUrlWidget = self.form.find_field_by_name("url").widget
        if (
            prev_index
            and new_index
            and url_widget.table is not None
            and url_widget.file_ext != ".h5"
        ):
            # if index was numeric, check that it has not changed when converted to str
            if isinstance(prev_index[0], int):
                # noinspection PyBroadException
                try:
                    column_names = get_columns(
                        url_widget.table, include_index=True
                    )
                    prev_index = [column_names[idx] for idx in prev_index]
                except Exception:
                    pass
            # convert to same type
            if isinstance(prev_index, list) and len(prev_index) == 1:
                prev_index = prev_index[0]
            if isinstance(new_index, list) and len(new_index) == 1:
                new_index = new_index[0]

            # abort if the user select No
            if new_index != prev_index:
                if self.maybe_new_index() is False:
                    self.save_button.setEnabled(True)
                    return

        # check if table name has changed
        new_name = form_data["name"]
        if form_data["name"] != self.name:
            # update the model configuration
            self.model_config.tables.rename(self.name, new_name)

            # update the page name in the list
            # noinspection PyUnresolvedReferences
            self.pages.rename_page(self.name, new_name)

            # update the page title
            self.set_page_title(new_name)

            # update the table list
            # noinspection PyUnresolvedReferences
            table_model: TablesListModel = (
                self.pages.dialog.table_list_widget.model
            )
            idx = table_model.table_names.index(self.name)
            # noinspection PyUnresolvedReferences
            table_model.layoutAboutToBeChanged.emit()
            table_model.table_names[idx] = new_name
            # noinspection PyUnresolvedReferences
            table_model.layoutChanged.emit()

            self.name = new_name

        # update the model with the new dictionary
        del form_data["name"]
        self.model_config.tables.update(self.name, form_data)

        # update tree and status bar
        app = self.pages.dialog.app
        if app is not None:
            if hasattr(app, "components_tree"):
                app.components_tree.reload()
            if hasattr(app, "statusBar"):
                app.statusBar().showMessage(f'Table "{self.name}" updated')

    @Slot()
    def on_delete_table(self) -> None:
        """
        Deletes the selected table.
        :return: None
        """
        dialog = self.pages.dialog
        list_widget = dialog.table_list_widget.list
        list_model = list_widget.model
        # check if table is being used and warn before deleting
        total_components = self.model_config.tables.is_used(self.name)

        # ask before deleting
        if maybe_delete_component(self.name, total_components, self):
            # remove the table from the table model
            # noinspection PyUnresolvedReferences
            list_model.layoutAboutToBeChanged.emit()
            list_model.table_names.remove(self.name)
            # noinspection PyUnresolvedReferences
            list_model.layoutChanged.emit()
            list_widget.clear_selection()

            # remove the page widget
            page_widget = self.pages.pages[self.name]
            page_widget.deleteLater()
            del self.pages.pages[self.name]

            # delete the table from the model configuration
            self.model_config.tables.delete(self.name)

            # set default page
            self.pages.set_empty_page()

            # update tree and status bar
            if dialog.app is not None:
                if hasattr(dialog.app, "components_tree"):
                    dialog.app.components_tree.reload()
                if hasattr(dialog.app, "statusBar"):
                    dialog.app.statusBar().showMessage(
                        f'Deleted table "{self.name}"'
                    )

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        """
        Loads the form only when the page is requested.
        :param event: The event being triggered.
        :return: None
        """
        if self.form.loaded is False:
            self.logger.debug(f"Loading fields for table named '{self.name}'")
            self.form.load_fields()

        super().showEvent(event)
