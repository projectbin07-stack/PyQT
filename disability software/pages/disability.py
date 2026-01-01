# pages/disability.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
)
from PyQt5.QtCore import Qt


class DisabilityPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Title
        title = QLabel("Choose Support Type")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # GRID for buttons (2x2)
        grid = QGridLayout()
        grid.setSpacing(30)

        # Create buttons
        btn_deaf = QPushButton("Deaf")
        btn_blind = QPushButton("Blind")
        btn_mute = QPushButton("Mute")
        btn_other = QPushButton("Other Disabilities")

        buttons = [btn_deaf, btn_mute, btn_blind, btn_other]

        # Styling for boxed buttons
        btn_style = """
            QPushButton{
                background: #ffffff;
                border: 2px solid #d0d0d0;
                border-radius: 12px;
                padding: 18px;
                font-size: 20px;
                min-width: 260px;
                min-height: 90px;
            }
            QPushButton:hover{
                border: 2px solid #7fbfff;
                background: #fbfdff;
            }
            QPushButton:pressed{
                background: #e8f4ff;
            }
        """

        for b in buttons:
            b.setStyleSheet(btn_style)

        # Add to grid (2x2) and center each cell
        grid.addWidget(btn_deaf, 0, 0, alignment=Qt.AlignCenter)
        grid.addWidget(btn_mute, 0, 1, alignment=Qt.AlignCenter)
        grid.addWidget(btn_blind, 1, 0, alignment=Qt.AlignCenter)
        grid.addWidget(btn_other, 1, 1, alignment=Qt.AlignCenter)

        layout.addLayout(grid)
        layout.addStretch()
        self.setLayout(layout)

        # Navigation (use main_window.stacked indices)
        btn_deaf.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_deaf))
        btn_blind.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_blind))
        btn_mute.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_mute_main))
        btn_other.clicked.connect(lambda: self.main_window.stacked.setCurrentIndex(self.main_window.index_other))
        