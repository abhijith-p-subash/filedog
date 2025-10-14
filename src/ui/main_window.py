from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QFileDialog,
    QLabel
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path
from core.organizer import FileOrganizer

class OrganizerThread(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int)

    def __init__(self, /, folder_path):
        super().__init__()
        self.folder_path = Path(folder_path)
        self.organizer = FileOrganizer(logger=self.emit_log)

    def emit_log(self, message):
        self.log_signal.emit(message)

    def run(self):
        self.organizer.organize(self.folder_path)
        self.progress_signal.emit(100)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("orgDog")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        self.folder_label = QLabel(f"Folder: {Path.home() / 'Downloads'}")
        layout.addWidget(self.folder_label)

        self.select_btn = QPushButton("Select Folder")
        self.select_btn.clicked.connect(self.select_folder)
        layout.addWidget(self.select_btn)

        self.start_btn = QPushButton("Organize Files")
        self.start_btn.clicked.connect(self.start_organizing)
        layout.addWidget(self.start_btn)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.folder_path = Path.home() / 'Downloads'
        self.thread = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", str(self.folder_path))
        if folder:
            self.folder_path = Path(folder)
            self.folder_label.setText(f"Folder: {self.folder_path}")

    def start_organizing(self):
        self.log_output.clear()
        self.progress.setValue(0)
        self.thread = OrganizerThread(self.folder_path)
        self.thread.log_signal.connect(self.append_log)
        self.thread.progress_signal.connect(self.progress.setValue)
        self.thread.start()

    def append_log(self, text):
        self.log_output.append(text)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())