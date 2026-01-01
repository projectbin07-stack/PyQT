from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class MutePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Mute Mode")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        btn_asl = QPushButton("ASL → Text → Speak")
        btn_tts = QPushButton("Type to Speak")
        btn_quick = QPushButton("Quick Phrases")
        btn_back = QPushButton("Back")

        for b in (btn_asl, btn_tts, btn_quick, btn_back):
            b.setMinimumHeight(45)

        # NAVIGATION
        btn_asl.clicked.connect(lambda:
            self.main_window.stacked.setCurrentIndex(self.main_window.index_asl)
        )

        btn_tts.clicked.connect(lambda:
            self.main_window.stacked.setCurrentIndex(self.main_window.index_mute_tts)
        )

        btn_quick.clicked.connect(lambda:
            print("→ Quick Phrases pressed (not implemented)")
        )

        btn_back.clicked.connect(lambda:
            self.main_window.stacked.setCurrentIndex(self.main_window.index_disability)
        )

        layout.addWidget(btn_asl)
        layout.addWidget(btn_tts)
        layout.addWidget(btn_quick)
        layout.addWidget(btn_back)

        self.setLayout(layout)
