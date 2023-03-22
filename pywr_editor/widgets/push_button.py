from PySide6.QtWidgets import QPushButton, QWidget


class PushButton(QPushButton):
    def __init__(
        self, label: str = "", small: bool = False, parent: QWidget = None
    ):
        """
        Initialises the button widget.
        :param label: The button label. Default to empty.
        :param small: Whether to reduce the x-padding size. Default to False.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(label, parent)

        if small:
            self.setStyleSheet("padding: 4px 6px")
