import sys
import os
import subprocess
import json
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal
from PySide6.QtGui import QPixmap

# Worker thread for running one-shot commands without blocking the GUI
class CommandWorker(QObject):
    finished = Signal()
    stats_ready = Signal(dict)
    command_done = Signal()

    def __init__(self, script_path, command):
        super().__init__()
        self.script_path = script_path
        self.command = command

    def run(self):
        print(f"Worker sending command: {self.command}")
        try:
            if self.command == "stats":
                result = subprocess.run(["python3", self.script_path, self.command], capture_output=True, text=True, timeout=10)
                stats = json.loads(result.stdout)
                self.stats_ready.emit(stats)
            else:
                subprocess.run(["python3", self.script_path, self.command], timeout=10)
                self.command_done.emit()
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

        self.stats_layout = QHBoxLayout()
        self.main_layout.addLayout(self.stats_layout)

        self.total_label = QLabel("Total: -")
        self.stats_layout.addWidget(self.total_label)

        self.used_label = QLabel("Used: -")
        self.stats_layout.addWidget(self.used_label)

        self.remaining_label = QLabel("Remaining: -")
        self.stats_layout.addWidget(self.remaining_label)

        self.setFixedSize(450, 350)

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
            
            self.run_command("stats")

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

    def update_stats(self, stats):
        self.total_label.setText(f"Total: {stats['total']}")
        self.used_label.setText(f"Used: {stats['used']}")
        self.remaining_label.setText(f"Remaining: {stats['remaining']}")

    def run_command(self, command):
        self.command_thread = QThread()
        self.command_worker = CommandWorker(self.script_path, command)
        self.command_worker.moveToThread(self.command_thread)
        self.command_thread.started.connect(self.command_worker.run)
        if command == "stats":
            self.command_worker.stats_ready.connect(self.update_stats)
        else:
            self.command_worker.command_done.connect(self.check_for_update)
        self.command_worker.finished.connect(self.command_thread.quit)
        self.command_worker.finished.connect(self.command_worker.deleteLater)
        self.command_thread.finished.connect(self.command_thread.deleteLater)
        self.command_thread.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_P:
            self.run_command("previous")
        elif event.key() == Qt.Key_N:
            self.run_command("next")
        elif event.key() == Qt.Key_Space:
            self.run_command("pause")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SlideshowControl()
    ex.show()
    sys.exit(app.exec())
