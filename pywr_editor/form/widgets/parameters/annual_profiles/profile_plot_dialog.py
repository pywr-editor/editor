from typing import Any

import pyqtgraph as pg
from pyqtgraph import mkBrush, mkPen
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget

from pywr_editor.style import Color


class ChartOptions:
    def __init__(
        self,
        y_label: str = "Value",
        x_major_ticks: list[[int, str]] | None = None,
        x_minor_ticks: list[[int, str]] | None = None,
        x_tick_spacing: list[int, int] | None = None,
        show_points: bool = False,
        step_mode: bool = False,
        background: str | Color = Color("gray", 50).qcolor,
        foreground: str | Color = "k",
        line_color: str | Color = Color("teal", 600).qcolor,
        line_width: int = 3,
    ):
        """
        Defines the chart options.
        :param y_label: The label on the y-axis. Default to "Value"
        :param x_major_ticks: The major ticks on the x-axis. Optional to place the
        ticks automatically.
        :param x_minor_ticks: The minor ticks on the x-axis.
        :param x_tick_spacing: Explicitly set the spacing of major ticks on the x-axis.
        :param show_points: Show the points.
        :param step_mode: Whether to plot the data as a step-wise function.
        :param background: The chart background colour.
        :param foreground: The chart foreground colour.
        :param line_color: The line colour.
        :param line_width: The line width.
        """
        self.x_major_ticks = x_major_ticks
        if self.x_major_ticks is None:
            self.x_major_ticks = []

        self.x_minor_ticks = x_minor_ticks
        if self.x_minor_ticks is None:
            self.x_minor_ticks = []

        self.y_label = y_label
        self.x_major_ticks = x_major_ticks
        self.x_tick_spacing = x_tick_spacing
        self.show_points = show_points
        self.step_mode = step_mode
        self.background = background
        self.foreground = foreground
        self.line_color = line_color
        self.line_width = line_width


class ProfilePlotDialog(QDialog):
    def __init__(
        self,
        title: str,
        y: list[float],
        x: list[int | float] = None,
        chart_options: ChartOptions = None,
        parent: QWidget = None,
    ):
        """
        Initialises the profile plot dialog.
        :param title: The dialog and chart self.title.
        :param y: The y-coordinate.
        :param x: The x-coordinates. Optional to show the point number.
        :param y: A list of the data to plot.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.x = x
        self.chart_options = chart_options
        self.title = f"Parameter: {title}"

        if self.chart_options is None:
            self.chart_options = ChartOptions()
        if self.x is None:
            if self.chart_options.step_mode:
                self.x = list(range(0, len(y) + 1))
            else:
                self.x = list(range(0, len(y)))

        pg.setConfigOption("background", self.chart_options.background)
        pg.setConfigOption("foreground", self.chart_options.foreground)
        pg.setConfigOptions(antialias=True)

        # Chart widget
        self.widget = pg.PlotWidget(name=self.title, enableMenu=False)
        # disable drag and drop
        self.widget.setMouseEnabled(x=False, y=False)

        # Line
        pen = mkPen(
            color=self.chart_options.line_color,
            width=self.chart_options.line_width,
        )
        self.line = pg.PlotCurveItem(
            x=self.x,
            y=y,
            pen=pen,
            stepMode=self.chart_options.step_mode,
        )
        self.widget.addItem(self.line)

        # Points
        if self.chart_options.show_points:
            brush = mkBrush(color=self.chart_options.line_color)
            self.points = pg.ScatterPlotItem(
                x=self.x[0:-1] if self.chart_options.step_mode else self.x,
                y=y,
                pen=pen,
                brush=brush,
                hoverable=True,
                size=7,
                hoverSize=11,
                tip=self.show_tooltip,
            )
            self.points.setSymbol("o")
            self.widget.addItem(self.points)

        # Axis style
        self.widget.showGrid(x=True, y=True, alpha=0.3)
        self.widget.setLabel(
            "bottom", self.chart_options.y_label, **{"font-weight": "bold"}
        )
        self.widget.setLabel("left", "Value", **{"font-weight": "bold"})

        # Set x-ticks and labels
        ay = self.widget.getAxis("bottom")
        if chart_options.x_tick_spacing:
            ay.setTickSpacing(
                major=chart_options.x_tick_spacing[0],
                minor=chart_options.x_tick_spacing[1],
            )
        elif (
            self.chart_options.x_major_ticks or self.chart_options.x_minor_ticks
        ):
            ay.setTicks(
                [
                    self.chart_options.x_major_ticks,
                    self.chart_options.x_minor_ticks,
                ]
            )

        # Change style of other components
        plot_item = self.widget.getPlotItem()
        # make self.title bold
        plot_item.setTitle(self.title)
        bold = QFont()
        bold.setBold(True)
        plot_item.titleLabel.item.setFont(bold)

        # Show the other axis for boxed plot
        for axis_name in ["top", "right"]:
            plot_item.showAxis(axis_name)
            self.widget.getAxis(axis_name).setTicks([])

        # Dialog
        self.setWindowTitle(self.title)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)

    def show_tooltip(self, x: float, y: float, data: Any) -> str:
        """
        Shows the tooltip for the point.
        :param x: The x position.
        :param y: The y position.
        :param data: The data.
        :return: The tooltip text.
        """
        if self.chart_options.x_major_ticks:
            label = [
                x_tick_data[1]
                for x_tick_data in self.chart_options.x_major_ticks
                if x_tick_data[0] == x
            ]
            if label and label[0] != "":
                return f"{label[0]}: {y}"

        return f"{x}: {y}"
