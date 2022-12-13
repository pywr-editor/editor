from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QLabel,
    QVBoxLayout,
    QSpacerItem,
    QHBoxLayout,
)
from typing import TYPE_CHECKING, Union
from pywr_editor.style import Color
from pywr_editor.form import FormTitle

if TYPE_CHECKING:
    from .parameter_pages_widget import ParameterPagesWidget


class ParameterEmptyPageWidget(QWidget):
    def __init__(self, parent: Union["ParameterPagesWidget", None] = None):
        """
        Initialises the empty page widget.
        :param parent: The parent widget.
        """
        super().__init__(parent)

        layout = QVBoxLayout(self)

        title = FormTitle("Parameters")
        label = QLabel()
        label.setText(
            "Select the model parameter you would like to edit on the list on the "
            + "left-hand side. Otherwise click the 'Add' button to add a new "
            + "parameter to the model configuration."
        )
        label.setStyleSheet(f"color: {Color('gray', 500).hex}")
        label.setWordWrap(True)

        icon_layout = QHBoxLayout()
        icon_layout.addItem(
            QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        icon = QSvgWidget(":toolbar/edit-parameters")
        icon.setFixedSize(200, 200)
        icon_layout.addWidget(icon)

        layout.addWidget(title)
        layout.addLayout(icon_layout)
        layout.addWidget(label)
        layout.addItem(
            QSpacerItem(10, 30, QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
