import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout


class PathViewer(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.plot = pg.PlotWidget()
        self.plot.setAspectLocked(True)
        self.plot.showGrid(x=True, y=True)
        self.plot.setBackground("w")

        layout.addWidget(self.plot)

    def draw_paths(self, paths, show_travel=True):
        self.plot.clear()

        draw_x = []
        draw_y = []
        travel_x = []
        travel_y = []

        last_end = None

        for path in paths:
            if not path.points:
                continue

            if show_travel and last_end is not None:
                travel_x.extend([last_end.x, path.start.x, np.nan])
                travel_y.extend([last_end.y, path.start.y, np.nan])

            for p1, p2 in zip(path.points, path.points[1:]):
                draw_x.extend([p1.x, p2.x, np.nan])
                draw_y.extend([p1.y, p2.y, np.nan])

            last_end = path.end

        if travel_x:
            self.plot.plot(
                np.array(travel_x, dtype=float),
                np.array(travel_y, dtype=float),
                pen=pg.mkPen("r", width=1, style=Qt.PenStyle.DashLine),
            )

        if draw_x:
            self.plot.plot(
                np.array(draw_x, dtype=float),
                np.array(draw_y, dtype=float),
                pen=pg.mkPen("k", width=1),
            )

        self.plot.enableAutoRange()