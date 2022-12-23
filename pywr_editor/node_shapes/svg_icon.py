import PySide6
from PySide6.QtCore import QByteArray, QFile, QRectF, Qt, QTextStream
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QGraphicsItem

from pywr_editor.style import Color

from .base_node import BaseNode


class IconProps:
    def __init__(
        self,
        name: str,
        fill: Color,
        outline: Color,
        padding: float = 4.5,
        rect: QRectF = None,
    ):
        """
        Initialises the class
        :param name: The icon name in the resource file.
        :param fill: The Color instance to use to fill the icon.
        :param outline: The Color instance for the icon outline.
        :param padding: The icon padding around the node.
        :param rect: A custom QRectF to use for the bounding rectangle. Optional.
        """
        self.name = name
        self.fill = fill
        self.outline = outline
        self.padding = padding
        if rect and not isinstance(rect, QRectF):
            raise TypeError("rect must be of type QRectF")
        self.rect = rect


class SvgIcon(QGraphicsItem):
    def __init__(self, parent: BaseNode, icon: IconProps | None = None):
        """
        Initialises the class for an icon.
        :param parent: The parent circle.
        :param icon: The icon properties.
        :return None
        """
        super().__init__(parent)

        self.parent = parent
        self.icon_name = icon.name
        self.fill = icon.fill
        self.outline = icon.outline
        self.padding = icon.padding
        self.custom_rect = icon.rect

        self.setZValue(2)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setAcceptedMouseButtons(Qt.NoButton)

    def renderer(self) -> PySide6.QtSvg.QSvgRenderer:
        """
        Defines the renderer. it loads the icon and colours it based on the
        parent's colours.
        :return: The SVG renderer instance.
        """
        f = QFile(self.icon_name)
        f.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(f)
        svg_data = stream.readAll()
        f.close()

        # svg_data = svg_data.replace('currentFill', self.fill.hex)
        # svg_data = svg_data.replace('currentStroke', self.outline.hex)
        svg_data = svg_data.replace("currentColor", self.fill.hex)
        # noinspection PyTypeChecker
        return QSvgRenderer(QByteArray(svg_data))

    def boundingRect(self) -> PySide6.QtCore.QRectF:
        """
        Defines the boundary box. The box and therefore the icon's size are scaled
        based on the circle's size and icon's padding. The larger the padding, the
        smaller the icon.
        :return: The rectangle
        """
        if self.custom_rect:
            return self.custom_rect

        size = self.parent.size
        return QRectF(
            -size[0] / 2 + self.padding,
            -size[1] / 2 + self.padding,
            size[0] - self.padding * 2,
            size[1] - self.padding * 2,
        )

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the icon.
        :param painter: The painter instance.
        :param option: The option.
        :param widget: The widget.
        :return: None
        """
        self.renderer().render(painter, self.boundingRect())
