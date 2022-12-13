import json
import PySide6
from PySide6.QtCore import QRect, Slot
from PySide6.QtGui import QFont, QPainter, Qt
from PySide6.QtWidgets import QPlainTextEdit
from .json_highlighter import JsonHighlighter
from .line_number_area import LineNumberArea
from pywr_editor.style import Color


class JsonEditor(QPlainTextEdit):
    def __init__(
        self,
        file_content: str | dict,
        document_title: str = "JSON viewer",
    ):
        """
        Initialises the JSOn code reader.
        :param file_content: The JSON document.
        :param document_title: The document title. Optional
        """
        super().__init__()

        if isinstance(file_content, dict):
            file_content = json.dumps(file_content, indent=2)

        JsonHighlighter(self.document())

        # font
        font = QFont()
        font.setStyleHint(QFont.Monospace, QFont.PreferAntialias)
        self.setFont(font)

        # init the document
        self.setPlainText(file_content)
        self.setReadOnly(True)
        self.setDocumentTitle(document_title)

        # style
        self.setMinimumSize(700, 700)
        self.line_number_area = LineNumberArea(self)

        # noinspection PyUnresolvedReferences
        self.blockCountChanged.connect(self.set_line_number_area_width)
        # noinspection PyUnresolvedReferences
        self.updateRequest.connect(self.updated_line_number_area)
        self.set_line_number_area_width()

    @Slot()
    def line_number_area_width(self) -> int:
        """
        Calculates the width of the line number area.
        :return: The width.
        """
        digits = 1
        max_block = max(1, self.blockCount())
        while max_block >= 10:
            max_block /= 10
            digits += 1

        return 4 + self.fontMetrics().horizontalAdvance("9") * digits

    @Slot()
    def set_line_number_area_width(self) -> None:
        """
        Updates the width of the line number area.
        :return: None
        """
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    @Slot()
    def updated_line_number_area(self, rect: QRect, dy: int) -> None:
        """
        Updates the line number area.
        :param rect: The rectangle for the area.
        :param dy: The vertical scroll.
        :return: None
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.set_line_number_area_width()

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        """
        Handles the editor resize window event. This updates the geometry of the line
        number area.
        :param event: The event being triggered.
        :return: None
        """
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(
                cr.left(), cr.top(), self.line_number_area_width(), cr.height()
            )
        )

    def line_number_area_paint_event(
        self, event: PySide6.QtGui.QPaintEvent
    ) -> None:
        """
        Paints the line number area.
        :param event: The event being triggered.
        :return: None
        """
        painter = QPainter(self.line_number_area)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Color("gray", 200).qcolor)
        painter.drawRoundedRect(event.rect(), 4, 4)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = block_number + 1
                painter.setPen(Color("gray", 600).qcolor)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 2,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(number),
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
