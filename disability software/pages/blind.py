from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
import webbrowser

class BlindPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Blind Mode")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        btn_vision = QPushButton("Vision Assist")
        btn_pdf = QPushButton("PDF Reader")
        btn_exam = QPushButton("Exam Mode")
        btn_back = QPushButton("Back")

        # ✅ FIXED — use real indexes from main_window
        btn_vision.clicked.connect(lambda:
            self.main_window.stacked.setCurrentIndex(self.main_window.index_vision)
        )

        btn_pdf.clicked.connect(lambda:
            self.main_window.stacked.setCurrentIndex(self.main_window.index_pdf)
        )

        btn_exam.clicked.connect(lambda:
            webbrowser.open("http://192.168.137.140:5000")
        )

        btn_back.clicked.connect(lambda:
            self.main_window.stacked.setCurrentIndex(self.main_window.index_disability)
        )

        for b in (btn_vision, btn_pdf, btn_exam, btn_back):
            b.setMinimumHeight(45)
            layout.addWidget(b)

        layout.addStretch()
        self.setLayout(layout)
