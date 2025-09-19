import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal
from PySide6.QtGui import QPixmap

# Worker thread for running one-shot commands without blocking the GUI
class CommandWorker(QObject):
    finished = Signal()

    def __init__(self, script_path, command):
        super().__init__()
        self.script_path = script_path
        self.command = command

    def run(self):
        print(f"Worker sending command: {self.command}")
        try:
            subprocess.run(["python3", self.script_path, self.command], timeout=10)
        except Exception as e:
            print(f"Error in worker for command '{self.command}': {e}")
        self.finished.emit()

class SlideshowControl(QWidget):
    def __init__(self):
        super().__init__()
        self.script_path = os.path.join(os.path.dirname(__file__), "wallpaper_slideshow.py")
        self.current_wallpaper_file = os.path.expanduser("~/.cache/current_wallpaper.txt")
        
        self.current_displayed_path = None
        self.command_thread = None
        self.command_worker = None

        self.initUI()
        self.init_timer()

    def initUI(self):
        self.setWindowTitle("Slideshow Monitor")
        self.main_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.btn_prev = QPushButton("Previous (p)")
        self.btn_prev.clicked.connect(lambda: self.run_command("previous"))
        self.button_layout.addWidget(self.btn_prev)

        self.btn_pause = QPushButton("Pause (space)")
        self.btn_pause.clicked.connect(lambda: self.run_command("pause"))
        self.button_layout.addWidget(self.btn_pause)

        self.btn_next = QPushButton("Next (n)")
        self.btn_next.clicked.connect(lambda: self.run_command("next"))
        self.button_layout.addWidget(self.btn_next)

        self.filename_label = QLabel("Searching for current wallpaper...")
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.filename_label)

        self.image_preview_label = QLabel()
        self.image_preview_label.setAlignment(Qt.AlignCenter)
        self.image_preview_label.setMinimumSize(400, 225)
        self.main_layout.addWidget(self.image_preview_label)

        self.setFixedSize(450, 300)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.check_for_update)
        self.timer.start()

    def showEvent(self, event):
        super().showEvent(event)
        self.check_for_update()

    def check_for_update(self):
        try:
            if not os.path.exists(self.current_wallpaper_file):
                self.filename_label.setText("Waiting for slideshow to start...")
                return

            with open(self.current_wallpaper_file, "r") as f:
                new_path = f.read().strip()

            if new_path and new_path != self.current_displayed_path:
                self.current_displayed_path = new_path
                self.update_display(new_path)

        except Exception as e:
            self.filename_label.setText(f"Error reading state file: {e}")

    def update_display(self, wallpaper_path):
        self.filename_label.setText(os.path.basename(wallpaper_path))
        pixmap = QPixmap(wallpaper_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(self.image_preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview_label.setPixmap(scaled_pixmap)
        else:
            self.image_preview_label.setText("Cannot load image preview.")

    def run_command(self, command):
        self.command_thread = QThread()
        self.command_worker = CommandWorker(self.script_path, command)
        self.command_worker.moveToThread(self.command_thread)
        self.command_thread.started.connect(self.command_worker.run)
        self.command_worker.finished.connect(self.command_thread.quit)
        self.command_worker.finished.connect(self.command_worker.deleteLater)
        self.command_thread.finished.connect(self.command_thread.deleteLater)
        self.command_thread.start()

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key_P:
                self.run_command("previous")
            case Qt.Key_N:
                self.run_command("next")
            case Qt.Key_Space:
                self.run_command("pause")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SlideshowControl()
    ex.show()
    sys.exit(app.exec())