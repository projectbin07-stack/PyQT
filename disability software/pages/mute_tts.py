from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt
from core.speech import speak

class MuteTTSPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Type to Speak")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        info = QLabel("Type your message below and press SPEAK")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size: 16px;")
        layout.addWidget(info)

        self.text_box = QTextEdit()
        self.text_box.setPlaceholderText("Type here...")
        self.text_box.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.text_box)

        btn_row = QHBoxLayout()

        btn_speak = QPushButton("🔊 SPEAK")
        btn_clear = QPushButton("❌ CLEAR")

        btn_speak.setMinimumHeight(45)
        btn_clear.setMinimumHeight(45)

        btn_speak.clicked.connect(self.speak_text)
        btn_clear.clicked.connect(lambda: self.text_box.clear())

        btn_row.addWidget(btn_speak)
        btn_row.addWidget(btn_clear)

        layout.addLayout(btn_row)

        # Back button
        btn_back = QPushButton("Back to Mute Menu")
        btn_back.setMinimumHeight(45)
        btn_back.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_mute_main))
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def speak_text(self):
        text = self.text_box.toPlainText().strip()
        if text:
            speak(text)
