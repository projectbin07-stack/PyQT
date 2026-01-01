import sys, json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

from assign import send_pickup_data
from keypad import KeypadWidget
from config import LOCKER_COUNT, BACKGROUND_COLOR


class LockIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 80)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color = QColor("white")
        pen = QPen(color)
        pen.setWidth(6)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        path = QPainterPath()
        shackle_w = 28
        shackle_h = 30
        shackle_x = (self.width() - shackle_w) / 2
        shackle_y = 10

        path.moveTo(shackle_x, shackle_y + shackle_h)
        path.lineTo(shackle_x, shackle_y + shackle_h / 2)
        path.arcTo(QRectF(shackle_x, shackle_y, shackle_w, shackle_w), 180, -180)
        path.lineTo(shackle_x + shackle_w, shackle_y + shackle_h)

        painter.drawPath(path)

        body_w = 50
        body_h = 38
        body_x = (self.width() - body_w) / 2
        body_y = shackle_y + shackle_h - 5

        painter.setBrush(QColor("white"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(body_x, body_y, body_w, body_h), 6, 6)

        painter.setBrush(QColor("#1e3a8a"))
        painter.drawEllipse(QRectF(self.width() / 2 - 3, body_y + body_h / 2 - 3, 6, 6))


class OpeningPage(QWidget):
    def __init__(self, locker_no, on_done):
        super().__init__()

        self.setStyleSheet(f"""
            QWidget {{ background:{BACKGROUND_COLOR}; color:white; font-family:Inter,'Segoe UI'; }}
            QLabel {{ background: transparent; }}
        """)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)

        title = QLabel("OPENING LOCKER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:32px; font-weight:700;")

        sub = QLabel(f"LOCKER {locker_no}")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("font-size:18px; color:rgba(255,255,255,0.8);")

        layout.addWidget(title)
        layout.addWidget(sub)

        QTimer.singleShot(1500, on_done)


class DonePage(QWidget):
    def __init__(self, on_finish):
        super().__init__()

        self.setStyleSheet(f"""
            QWidget {{ background:{BACKGROUND_COLOR}; color:white; font-family:Inter,'Segoe UI'; }}
            QLabel {{ background: transparent; }}
        """)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("DONE")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size:40px; font-weight:700;")

        layout.addWidget(label)

        QTimer.singleShot(1200, on_finish)


class CenterScreen(QWidget):
    def __init__(self, child):
        super().__init__()

        self.setStyleSheet(f"""
            QWidget {{ background:{BACKGROUND_COLOR}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        layout.addWidget(child, alignment=Qt.AlignCenter)
        layout.addStretch(1)




# Error popup timeout in milliseconds
ERROR_POPUP_TIMEOUT = 3000

class ErrorPopup(QWidget):
    """In-page error popup that auto-dismisses after timeout"""
    def __init__(self, message, timeout_ms=ERROR_POPUP_TIMEOUT, on_close=None, parent=None):
        super().__init__(parent)
        self.on_close = on_close
        
        self.setStyleSheet(f"""
            QWidget {{
                background: rgba(239, 68, 68, 0.95);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
            }}
            QLabel {{
                background: white;
                color: black;
                font-size: 14px;
                font-weight: 700;
                padding: 12px 20px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        self.setFixedSize(260, 65)
        
        # Auto-dismiss timer
        QTimer.singleShot(timeout_ms, self._dismiss)
    
    def _dismiss(self):
        self.hide()
        if self.on_close:
            self.on_close()
        self.deleteLater()


class PickupWidget(QWidget):
    def __init__(self, mode="PICKUP", parent=None):
        super().__init__(parent)
        self.mode = mode  # Store the operation mode (PICKUP or DROPOFF)

        # Page-level sizing: expand to fill the main window central area
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.stage = "LOCKER"
        self.locker_no = None
        self.pin_buffer = ""
        self.pin_attempts = 0  # Track PIN retry attempts
        self.max_pin_attempts = 3

        self.load_data()

        self.setStyleSheet(f"""
            QWidget {{ background:{BACKGROUND_COLOR}; color:white; font-family:Inter,'Segoe UI'; }}
            QLabel {{ background:transparent; }}
            QPushButton {{ background:transparent; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # Store root layout for popup overlay
        self.root_layout = root

        # 1. Top Bar
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(20, 20, 20, 0)
        
        back = QPushButton("← BACK")
        back.setFixedSize(120, 44)
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 0;
            }
            QPushButton:hover {
                border-color: rgba(255, 255, 255, 0.9);
                background: rgba(255, 255, 255, 0.05);
            }
        """)
        back.clicked.connect(self.go_back)
        top_bar.addWidget(back)
        top_bar.addStretch()
        
        root.addLayout(top_bar)

        # 2. Upper Spacer
        root.addSpacing(10)

        # 3. Icon
        root.addWidget(LockIcon(), alignment=Qt.AlignCenter)

        # 4. Title
        title = QLabel(f"Stashit System - {self.mode}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:26px; font-weight:700; color: white; margin-top: 10px;")
        root.addWidget(title, alignment=Qt.AlignCenter)

        # 5. Instruction
        self.instruction = QLabel(f"ENTER LOCKER NUMBER (1 – {LOCKER_COUNT})")
        self.instruction.setAlignment(Qt.AlignCenter)
        self.instruction.setStyleSheet("font-size:16px; color:rgba(255,255,255,0.7); font-weight:500; margin-top: 5px;")
        root.addWidget(self.instruction, alignment=Qt.AlignCenter)

        # 6. Spacer
        root.addStretch(1)

        # 7. Interaction Area (Display + Keypad + Enter)
        interaction_layout = QVBoxLayout()
        interaction_layout.setSpacing(8)
        interaction_layout.setAlignment(Qt.AlignCenter)

        # Display
        self.display = QLabel("")
        self.display.setFixedSize(222, 50)
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setStyleSheet("""
            background: transparent;
            border: 2px solid rgba(255, 255, 255, 0.22);
            border-radius: 8px;
            font-size: 24px;
            font-weight: 600;
            color: white;
            letter-spacing: 3px;
        """)
        interaction_layout.addWidget(self.display, alignment=Qt.AlignHCenter)

        # Keypad (Smaller to fit screen)
        keypad = KeypadWidget(btn_w=60, btn_h=50, h_spacing=10, v_spacing=10)
        keypad.keyPressed.connect(self.key_pressed)
        interaction_layout.addWidget(keypad, alignment=Qt.AlignHCenter)
        
        # Enter Button
        enter = QPushButton("ENTER")
        enter.setFixedSize(200, 46)
        enter.setCursor(Qt.PointingHandCursor)
        enter.setStyleSheet("""
            QPushButton {
                background: white;
                border: none;
                border-radius: 12px;
                color: #15202b;
                font-size: 20px;
                font-weight: 800;
                letter-spacing: 1px;
            }
            QPushButton:pressed {
                background: #e2e8f0;
            }
        """)
        enter.clicked.connect(self.enter_pressed)
        interaction_layout.addWidget(enter, alignment=Qt.AlignHCenter)

        root.addLayout(interaction_layout)

        # 8. Lower Spacer
        root.addStretch(1)

    def load_data(self):
        with open("data.json", "r") as f:
            self.data = json.load(f)

    def find_locker(self, no):
        for l in self.data["lockers"]:
            if l["L.no"] == no:
                return l
        return None

    def key_pressed(self, key):
        if key == "CLEAR":
            self.display.setText("")
            self.pin_buffer = ""
            return

        if key == "X":
            if self.stage == "PIN":
                self.pin_buffer = self.pin_buffer[:-1]
                self.display.setText("●" * len(self.pin_buffer))
            else:
                self.display.setText(self.display.text()[:-1])
            return

        if self.stage == "PIN":
            self.pin_buffer += key
            self.display.setText("●" * len(self.pin_buffer))
        else:
            self.display.setText(self.display.text() + key)

    def enter_pressed(self):
        if self.stage == "LOCKER":
            if not self.display.text().isdigit():
                return self.show_error_popup("INVALID LOCKER NUMBER", self.reset_to_locker_entry)

            self.locker_no = int(self.display.text())
            if not (1 <= self.locker_no <= LOCKER_COUNT):
                return self.show_error_popup("INVALID LOCKER NUMBER", self.reset_to_locker_entry)
            
            # Check if locker exists and is assigned
            locker = self.find_locker(self.locker_no)
            if not locker:
                return self.show_error_popup("INVALID LOCKER NUMBER", self.reset_to_locker_entry)
            
            if locker["status"] != "assigned":
                return self.show_error_popup("LOCKER NOT ASSIGNED", self.reset_to_locker_entry)

            # Valid locker - proceed to PIN entry
            self.stage = "PIN"
            self.pin_attempts = 0  # Reset PIN attempts for this locker
            self.display.setText("")
            self.instruction.setText(f"ENTER PIN FOR LOCKER {self.locker_no}")

        elif self.stage == "PIN":
            locker = self.find_locker(self.locker_no)

            # Validate PIN
            if not self.pin_buffer.isdigit() or int(self.pin_buffer) != locker["pin"]:
                self.pin_attempts += 1
                
                if self.pin_attempts >= self.max_pin_attempts:
                    # Too many failed attempts - return to home
                    return self.show_error_popup("TOO MANY FAILED ATTEMPTS", self.force_go_home)
                else:
                    # Wrong PIN - allow retry
                    return self.show_error_popup("WRONG PIN", self.reset_to_pin_entry)

            # Correct PIN - proceed with locker operation
            send_pickup_data(self.locker_no, self.pin_buffer, mode=self.mode)

            # Navigation Logic using main.load_page(widget)
            main = self.window()
            if not hasattr(main, "load_page"):
                for w in QApplication.topLevelWidgets():
                    if hasattr(w, "load_page"):
                        main = w
                        break

            def _go_home():
                if hasattr(main, "load_page"):
                    main.load_page(None)

            def _show_done_screen():
                if hasattr(main, "load_page"):
                     main.load_page(CenterScreen(DonePage(_go_home)))

            if hasattr(main, "load_page"):
                main.load_page(CenterScreen(OpeningPage(self.locker_no, _show_done_screen)))

    def show_done(self):
        main = self.window()
        if hasattr(main, "load_page"):
            main.load_page(CenterScreen(DonePage(self.go_home)))

    def go_back(self):
        # Reset state when going back to home
        self.pin_attempts = 0
        self.locker_no = None
        self.pin_buffer = ""
        self.stage = "LOCKER"
        
        main = self.window()
        if hasattr(main, "load_page"):
            main.load_page(None)

    def go_home(self):
        # Reset state when going home
        self.pin_attempts = 0
        self.locker_no = None
        self.pin_buffer = ""
        self.stage = "LOCKER"
        
        main = self.window()
        if hasattr(main, "load_page"):
            main.load_page(None)

    def show_error_popup(self, message, on_close_callback=None):
        """Show error popup overlay with auto-dismiss"""
        popup = ErrorPopup(message, ERROR_POPUP_TIMEOUT, on_close_callback, self)
        
        # Position popup centered horizontally and vertically
        popup_x = (self.width() - popup.width()) // 2
        popup_y = (self.height() - popup.height()) // 2 - 35
        popup.move(popup_x, popup_y)
        
        popup.raise_()
        popup.show()
    
    def reset_to_locker_entry(self):
        """Reset to locker number entry screen"""
        self.stage = "LOCKER"
        self.locker_no = None
        self.pin_buffer = ""
        self.pin_attempts = 0
        self.display.setText("")
        self.instruction.setText(f"ENTER LOCKER NUMBER (1 – {LOCKER_COUNT})")
    
    def reset_to_pin_entry(self):
        """Reset PIN entry (keep locker number, clear PIN)"""
        self.pin_buffer = ""
        self.display.setText("")
    
    def force_go_home(self):
        """Force return to home page and reset all state"""
        self.stage = "LOCKER"
        self.locker_no = None
        self.pin_buffer = ""
        self.pin_attempts = 0
        
        main = self.window()
        if hasattr(main, "load_page"):
            main.load_page(None)

    def error(self, msg):
        """Legacy error method - kept for compatibility"""
        self.display.setText("")
        self.pin_buffer = ""
        self.instruction.setText(msg)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QMainWindow
    from config import WINDOW_SIZE, LOCKER_COUNT

    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setCentralWidget(PickupWidget())
    win.resize(*WINDOW_SIZE)
    win.show()
    sys.exit(app.exec_())
