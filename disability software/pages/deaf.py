from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class DeafPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Deaf Mode")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        btn_stt = QPushButton("Live Speech → Text")   # (you will make this later)
        btn_asl = QPushButton("ASL → Text")           # go to ASL page
        btn_chat = QPushButton("Chat Mode")           # (future feature)
        btn_back = QPushButton("Back")

        # NAVIGATION FIXES:
        btn_asl.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(6))
        btn_stt.clicked.connect(lambda: print("STT page not made yet"))
        btn_chat.clicked.connect(lambda: print("Chat page not made yet"))
        btn_back.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(0))

        for b in (btn_stt, btn_asl, btn_chat, btn_back):
            b.setMinimumHeight(45)
            layout.addWidget(b)

        layout.addStretch()
        self.setLayout(layout)
