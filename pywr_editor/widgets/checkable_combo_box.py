import PySide6
from typing import Any, Sequence
from PySide6.QtCore import QEvent, Qt, QModelIndex
from PySide6.QtGui import QFontMetrics, QStandardItem
from PySide6.QtWidgets import QStyledItemDelegate
from pywr_editor import ComboBox


class Delegate(QStyledItemDelegate):
    def sizeHint(
        self,
        option: PySide6.QtWidgets.QStyleOptionViewItem,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
    ) -> PySide6.QtCore.QSize:
        """
        Increases the item size.
        :param option: The option.
        :param index: The index.
        :return: The QSize instance.
        """
        size = super().sizeHint(option, index)
        size.setHeight(20)
        return size


class CheckableComboBox(ComboBox):
    def __init__(self, *args, **kwargs):
        """
        Initialises the widget. This creates a ComboBox with multi selection.
        """
        super().__init__(*args, **kwargs)

        # make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setObjectName("combo_box_line_edit")

        # custom delegate to resize the items
        self.setItemDelegate(Delegate())

        # update the text when an item is toggled
        # noinspection PyUnresolvedReferences
        self.model().dataChanged.connect(self.update_text)

        # hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.close_on_line_edit_click = False

        # prevent popup from closing when clicking on an item and other events
        self.view().viewport().installEventFilter(self)
        self.installEventFilter(self)

    def clear(self) -> None:
        """
        Clears the ComboBox and its model.
        :return: None
        """
        self.model().clear()
        super().clear()

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        """
        Recomputes the elided text.
        :param event: The vent being triggered.
        :return: None
        """
        # Recompute text to elide as needed
        self.update_text()
        super().resizeEvent(event)

    def wheelEvent(self, e: PySide6.QtGui.QWheelEvent):
        """
        Prevents user from changing the ComboBox value regardless of the widget focus
        status.
        :param e: The event being triggered.
        :return: None
        """
        e.ignore()

    def eventFilter(
        self, watched: PySide6.QtCore.QObject, event: PySide6.QtCore.QEvent
    ) -> bool:
        """
        Handles the popup and checkbox state
        :param watched: The object being clicked.
        :param event: The event being triggered
        :return: True to stop the event, False otherwise.
        """
        if watched == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.close_on_line_edit_click:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True

            return False

        # prevent keyboard interaction. Up and Down arrows change the line edit text
        # but not the checkboxes
        if watched == self and event.type() == QEvent.KeyPress:
            return True

        if watched == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                # noinspection PyUnresolvedReferences
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self) -> None:
        """
        Displays the ComboBox popup.
        :return: None
        """
        super().showPopup()
        # When the popup is displayed, a click on the line edit should close it
        self.close_on_line_edit_click = True

    def hidePopup(self) -> None:
        """
        Hides the ComboBox popup.
        :return: None
        """
        super().hidePopup()
        # prevent the popup from reopening after clicking on lineEdit
        self.startTimer(200)
        # refresh the display text when closing
        self.update_text()

    def timerEvent(self, event: PySide6.QtCore.QTimerEvent) -> None:
        """
        Handles the timer.
        :param event: The timer event
        :return: None
        """
        self.killTimer(event.timerId())
        self.close_on_line_edit_click = False

    def update_text(self) -> None:
        """
        Updates the text in the lineEdit widget.
        :return: None
        """
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())

        # block currentTextChanged Signal
        self.lineEdit().blockSignals(True)

        if len(texts) == 0:
            self.lineEdit().setText("None")
            return

        text = ", ".join(texts)

        # Compute elided text (with "...")
        width = self.lineEdit().width()
        if width < 300:
            width = 300
        metrics = QFontMetrics(self.lineEdit().font())
        elided_text = metrics.elidedText(text, Qt.ElideRight, width)

        self.lineEdit().setText(elided_text)

        self.lineEdit().blockSignals(False)

    # noinspection PyPep8Naming,PyMethodOverriding
    def addItem(
        self,
        text: str,
        userData: Any = None,
    ) -> None:
        """
        Adds an item
        :param text: The checkbox text.
        :param userData: The user data linked to the model. Default to None
        :return: None
        """
        # block currentTextChanged Signal
        self.lineEdit().blockSignals(True)

        item = QStandardItem()
        item.setText(text)
        # this triggers dataChanged and the text update in the line edit field
        if userData is None:
            item.setData(text)
        else:
            item.setData(userData, Qt.UserRole)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

        self.lineEdit().blockSignals(False)

    def addItems(
        self,
        texts: Sequence[str],
        datalist: Any = None,
        emit_signal: bool = False,
    ) -> None:
        """
        Adds more items to the model. This calls self.addItem method to add the
        checkbox to each item. If emit_signal is
        True, the Signal is emitted only once.
        :param texts: The text items.
        :param datalist: The data list.
        :param emit_signal: Whether to emit the dataChanged signal. Default to False.
        :return: None
        """
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

        # emit signal only once using dummy data
        if emit_signal:
            # noinspection PyUnresolvedReferences
            self.model().dataChanged.emit(QModelIndex(), QModelIndex(), [])
        else:
            # change text manually because signal is not emitted
            self.update_text()

    def checked_items(self, use_data: bool = False) -> list[str]:
        """
        Returns a list of checked items.
        :param use_data: Collect the data stored in the combobox items
        UserRole instead of their texts.
        :return: The checked items.
        """
        checked_items = []
        for index in range(self.model().rowCount()):
            item = self.model().item(index)
            if item.checkState() == Qt.Checked:
                checked_items.append(
                    item.text() if not use_data else item.data(Qt.UserRole)
                )
        return checked_items

    def check_items(
        self, indexes: list[int] | int, emit_signal: bool = True
    ) -> None:
        """
        Checks the items in the ComboBox based on their index.
        :param indexes: The index or a list of indexes to check.
        :param emit_signal: Emit the dataChanged Signal to notify the model changes.
        Default to True
        :return: None
        """
        if isinstance(indexes, int):
            indexes = [indexes]

        # block signals and emit it only once. Otherwise, setCheckState calls
        # dataChanged at every loop iteration
        self.model().blockSignals(True)
        for col_index in indexes:
            self.model().item(col_index).setCheckState(Qt.Checked)
        self.model().blockSignals(False)

        # emit signal only once using dummy data
        if emit_signal:
            # noinspection PyUnresolvedReferences
            self.model().dataChanged.emit(QModelIndex(), QModelIndex(), [])
        else:
            # change text manually because signal is not emitted
            self.update_text()

    def uncheck_all(self) -> None:
        """
        Unchecks all the checkboxes.
        :return: None
        """
        # block signals and emit it only once. Otherwise, setCheckState calls
        # dataChanged at every loop iteration
        self.model().blockSignals(True)
        for col_name in self.all_items:
            col_index = self.all_items.index(col_name)
            self.model().item(col_index).setCheckState(Qt.Unchecked)
        self.model().blockSignals(False)

        # emit signal only once using dummy data
        # noinspection PyUnresolvedReferences
        self.model().dataChanged.emit(QModelIndex(), QModelIndex(), [])

    def currentData(self, role: int = ...) -> list[str]:
        """
        Returns the current data set on the selected item of the model.
        :param role: The data role.
        :return The data as list.
        """
        data = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                data.append(self.model().item(i).data())
        return data
