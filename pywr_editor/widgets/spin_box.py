import PySide6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox


class SpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        """
        Initialises the widget. This creates a QSpinBox (for integers) with new limits.
        """
        super().__init__(*args, **kwargs)

        self.setRange(int(-pow(10, 6)), int(pow(10, 6)))
        # prevent mouse wheel from changing value on scroll
        self.setFocusPolicy(Qt.StrongFocus)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

    def wheelEvent(self, e: PySide6.QtGui.QWheelEvent) -> None:
        """
        Prevents user from changing the value on scroll.
        :param e: The event being triggered.
        :return: None
        """
        if self.hasFocus():
            super().wheelEvent(e)
        else:
            e.ignore()
