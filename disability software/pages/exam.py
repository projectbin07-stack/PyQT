from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class ExamPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Exam Mode")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        self.question_label = QLabel("Question will appear here")
        self.question_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.question_label)

        btn_repeat = QPushButton("Repeat")
        btn_next = QPushButton("Next Question")
        btn_back = QPushButton("Back")

        btn_back.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(0))

        for b in (btn_repeat, btn_next, btn_back):
            b.setMinimumHeight(45)
            layout.addWidget(b)

        layout.addStretch()
        self.setLayout(layout)
