# pages/vision.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from pages.vision_thread import VisionThread
from core.speech import speak   # <-- YOUR working TTS
import cv2

class VisionPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.thread = None

        layout = QVBoxLayout()

        title = QLabel("Vision Assist (YOLO Positional Detection)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        layout.addWidget(self.video_label)

        # Speak button
        self.btn_speak = QPushButton("🔊 Speak Objects (SPACE)")
        self.btn_speak.setStyleSheet("font-size: 18px; padding: 10px;")

        btn_start = QPushButton("Start Vision Assist")
        btn_stop  = QPushButton("Stop Vision Assist")
        btn_back  = QPushButton("Back")

        self.btn_speak.clicked.connect(self.speak_clicked)
        btn_start.clicked.connect(self.start_vision)
        btn_stop.clicked.connect(self.stop_vision)
        btn_back.clicked.connect(self.go_back)

        layout.addWidget(self.btn_speak)
        layout.addWidget(btn_start)
        layout.addWidget(btn_stop)
        layout.addWidget(btn_back)

        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)

    # SPACE triggers speak
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.speak_clicked()

    def speak_clicked(self):
        if self.thread:
            self.thread.request_speak()

    def start_vision(self):
        if self.thread:
            return

        self.thread = VisionThread(cam_index=0)
        self.thread.frame_signal.connect(self.update_frame)
        self.thread.speak_ready_signal.connect(self.speak_detections)
        self.thread.start()

    def stop_vision(self):
        if self.thread:
            self.thread.stop()
            self.thread = None
        self.video_label.clear()

    def go_back(self):
        self.stop_vision()
        self.main_window.stacked.setCurrentIndex(0)

    def speak_detections(self, detected_pairs):
        if not detected_pairs:
            speak("No objects detected.")
            return

        parts = [f"a {label} {pos}" for label, pos in detected_pairs]

        if len(parts) == 1:
            sentence = f"Detected {parts[0]}."
        else:
            last = parts.pop()
            sentence = "Detected " + ", ".join(parts) + f", and {last}."

        speak(sentence)

    def update_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)

        pix = QPixmap.fromImage(img)
        pix = pix.scaled(
            self.video_label.width(),
            self.video_label.height(),
            aspectRatioMode=1
        )
        self.video_label.setPixmap(pix)
