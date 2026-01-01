from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
import webbrowser

class OtherDisabilityPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Other Disabilities")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        label = QLabel("Choose what you want to do:")
        label.setStyleSheet("font-size: 20px;")
        layout.addWidget(label)

        btn_vision = QPushButton("Vision Assist")
        btn_asl = QPushButton("ASL Detection")
        btn_pdf = QPushButton("PDF Reader")
        btn_exam = QPushButton("Exam Mode")
        btn_back = QPushButton("Back")

        # 🔥 Correct navigation using real indexes
        btn_vision.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_vision))
        btn_asl.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_asl))
        btn_pdf.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_pdf))
        btn_exam.clicked.connect(lambda: webbrowser.open("http://192.168.137.140:5000"))
        btn_back.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_disability))

        for b in (btn_vision, btn_asl, btn_pdf, btn_exam, btn_back):
            b.setMinimumHeight(45)
            layout.addWidget(b)

        layout.addStretch()
        self.setLayout(layout)
