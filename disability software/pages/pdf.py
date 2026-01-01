import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt

from core.pdf_tools import PDFReaderEngine

class PDFReaderPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.engine = PDFReaderEngine()

        layout = QVBoxLayout()
        
        # Title
        title = QLabel("PDF Reader (Blind Mode)")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Open Button
        btn_open = QPushButton("Open PDF")
        btn_open.clicked.connect(self.open_pdf)
        layout.addWidget(btn_open)

        # Text Display
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.text_box)

        # Control Buttons
        btn_layout = QHBoxLayout()

        self.btn_prev = QPushButton("◀ Previous")
        self.btn_read = QPushButton("🔊 Read Page")
        self.btn_next = QPushButton("Next ▶")
        self.btn_all  = QPushButton("📖 Read All")
        self.btn_stop = QPushButton("🛑 Stop")

        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_read.clicked.connect(self.read_page)
        self.btn_all.clicked.connect(self.read_all)
        self.btn_stop.clicked.connect(self.stop_all)

        for b in [self.btn_prev, self.btn_read, self.btn_next, self.btn_all, self.btn_stop]:
            b.setMinimumHeight(40)
            btn_layout.addWidget(b)

        layout.addLayout(btn_layout)

        # Back Button
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(lambda: main_window.stacked.setCurrentIndex(0))
        layout.addWidget(btn_back)

        self.setLayout(layout)

    # -----------------------------------------------------
    # BUTTON FUNCTIONS
    # -----------------------------------------------------
    def open_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        num_pages = self.engine.load_pdf(path)
        if num_pages > 0:
            self.show_page()
        else:
            self.text_box.setText("Could not extract text.")

    def show_page(self):
        text = self.engine.get_page_text()
        self.text_box.setText(text)

    def next_page(self):
        if self.engine.current_page < len(self.engine.pages) - 1:
            self.engine.current_page += 1
            self.show_page()

    def prev_page(self):
        if self.engine.current_page > 0:
            self.engine.current_page -= 1
            self.show_page()

    def read_page(self):
        self.engine.speak_page()

    def read_all(self):
        self.engine.read_all()

    def stop_all(self):
        self.engine.stop()
