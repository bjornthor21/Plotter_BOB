import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout


class GCodeViewer(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.plot = pg.PlotWidget()
        self.plot.setAspectLocked(True)
        self.plot.showGrid(x=True, y=True)

        layout.addWidget(self.plot)