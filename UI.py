from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox,
    QLabel, QTextEdit
)
from settings import Settings
from converter import convert_dxf
from viewer import PathViewer
from pathlib import Path
from PySide6.QtGui import QIcon


class PlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_paths = []

        self.setWindowTitle("Plotter BOB")
        self.setWindowIcon(QIcon("icon.ico"))
        self.resize(500, 600)

        self.selected_file = None

        self.file_label = QLabel("No DXF selected")

        self.optimize_cb = QCheckBox("Optimize Paths")
        self.optimize_cb.setChecked(True)

        self.text_cb = QCheckBox("Text")
        self.text_cb.setChecked(True)

        self.dim_cb = QCheckBox("Dimensions")
        self.dim_cb.setChecked(True)

        self.border_cb = QCheckBox("Border")
        self.border_cb.setChecked(True)

        self.title_cb = QCheckBox("Title block")
        self.title_cb.setChecked(True)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.viewer = PathViewer()

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self.preview_paths)

        open_btn = QPushButton("Open DXF")
        open_btn.clicked.connect(self.open_file)

        gen_btn = QPushButton("Generate G-code")
        gen_btn.clicked.connect(self.generate_gcode)

        save_btn = QPushButton("Save As")
        save_btn.clicked.connect(self.save_as)

        controls = QHBoxLayout()
        controls.addWidget(open_btn)
        controls.addWidget(gen_btn)
        controls.addWidget(save_btn)

        checks = QHBoxLayout()
        checks.addWidget(self.optimize_cb)
        checks.addWidget(self.text_cb)
        checks.addWidget(self.dim_cb)
        checks.addWidget(self.border_cb)
        checks.addWidget(self.title_cb)

        layout = QVBoxLayout()
        layout.addWidget(self.file_label)
        layout.addLayout(controls)
        layout.addLayout(checks)
        layout.addWidget(QLabel("Log"))
        layout.addWidget(self.log)
        layout.addWidget(self.preview_btn)
        layout.addWidget(self.viewer)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open DXF",
            "",
            "DXF Files (*.dxf)"
        )

        if file_path:
            self.selected_file = file_path
            self.file_label.setText(file_path)
            self.log.append(f"Loaded: {file_path}")

    def generate_gcode(self):
        if not self.selected_file:
            self.log.append("No DXF selected.")
            return

        settings = Settings(
            optimize_paths=self.optimize_cb.isChecked(),
            draw_text=self.text_cb.isChecked(),
            draw_mtext=self.text_cb.isChecked(),
            draw_dimensions=self.dim_cb.isChecked(),
            draw_border=self.border_cb.isChecked(),
            draw_title_block=self.title_cb.isChecked()
        )

        input_path = Path(self.selected_file)

        try:
            gcode, paths = convert_dxf(str(input_path), settings)

            self.current_gcode = gcode
            self.current_paths = paths
            self.viewer.draw_paths(paths)

            self.log.append(f"Generated Gcode from: {str(input_path)}")
        except Exception as err:
            self.log.append(f"Error: {err}")
            raise

    def save_as(self):
        if not self.current_gcode:
            self.log.append("No G-code to save. Generate G-code first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save G-code As",
            "",
            "G-code Files (*.gcode);;NC Files (*.nc);;Text Files (*.txt)"
        )

        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.current_gcode))

        self.log.append(f"Saved as: {file_path}")

    def preview_paths(self):
        if not self.current_paths:
            self.log.append("No paths to preview. Generate G-code first.")
            return

        self.viewer.draw_paths(self.current_paths)

def run_app():
    app = QApplication([])
    window = PlotterApp()
    window.show()
    app.exec()