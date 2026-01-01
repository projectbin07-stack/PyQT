from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QImage, QPixmap
from pages.asl_thread import ASLCameraThread
from core.asl_model import ASLModel
import cv2

class ASLPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # MODEL
        self.asl_model = ASLModel()
        self.thread = None

        layout = QVBoxLayout()

        title = QLabel("ASL Detection")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        # Prediction label
        self.pred_label = QLabel("Detected: ?")
        self.pred_label.setStyleSheet("font-size: 22px; color: green;")
        layout.addWidget(self.pred_label)

        # Checkboxes
        cb_layout = QHBoxLayout()
        self.cb_alpha = QCheckBox("A - Z")
        self.cb_number = QCheckBox("0 - 9")
        self.cb_alpha.setChecked(True)
        self.cb_number.setChecked(True)

        cb_layout.addWidget(self.cb_alpha)
        cb_layout.addWidget(self.cb_number)
        layout.addLayout(cb_layout)

        # Video output
        self.video_label = QLabel()
        layout.addWidget(self.video_label)

        # Buttons
        btn_start = QPushButton("Start ASL")
        btn_stop = QPushButton("Stop ASL")
        btn_back = QPushButton("Back")

        btn_start.clicked.connect(self.start_asl)
        btn_stop.clicked.connect(self.stop_asl)
        btn_back.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(0))

        layout.addWidget(btn_start)
        layout.addWidget(btn_stop)
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def start_asl(self):
        if self.thread:
            return

    # Pass the ASLPage instance itself
        self.thread = ASLCameraThread(self.asl_model, self)
        self.thread.frame_signal.connect(self.update_frame)
        self.thread.start()


    def stop_asl(self):
        if self.thread:
            self.thread.stop()
            self.thread = None

    def update_frame(self, frame, pred):
        self.pred_label.setText(f"Detected: {pred}")

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))
