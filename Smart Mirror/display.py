import sys
import os
import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

from api import get_all_data


# ================= CONFIG =================
REFRESH_INTERVAL = 20000  # ms
NUM_FORECAST_DAYS = 4
ICON_PATH = os.path.join(os.path.dirname(__file__), "icons")
# ==========================================


class SmartMirror(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Mirror")
        self.setGeometry(0, 0, 768, 1366)
        self.setStyleSheet("background-color: black;")

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setSpacing(15)

        self.load_icons()
        self.build_ui()
        self.start_timers()

    # ======================================================
    # ICONS
    # ======================================================
    def load_icons(self):
        def load(name):
            path = os.path.join(ICON_PATH, name)
            return QPixmap(path).scaled(
                60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

        self.icons = {
            "clear": load("sun.png"),
            "rain": load("rain.png"),
            "clouds": load("cloud.png"),
            "snow": load("snow.png"),
            "storm": load("storm.png"),
            "partly": load("partly_cloudy.png"),
            "default": load("default_weather.png"),
        }

    def get_weather_icon(self, desc):
        d = desc.lower()
        if "clear" in d or "sun" in d:
            return self.icons["clear"]
        if "rain" in d or "drizzle" in d:
            return self.icons["rain"]
        if "cloud" in d:
            return self.icons["partly"] if "partly" in d else self.icons["clouds"]
        if "snow" in d:
            return self.icons["snow"]
        if "storm" in d or "thunder" in d:
            return self.icons["storm"]
        return self.icons["default"]

    # ======================================================
    # UI
    # ======================================================
    def build_ui(self):
        # ---------------- TIME / DATE ----------------
        self.time_label = QLabel("--:--")
        self.time_label.setFont(QFont("Helvetica Neue", 80))
        self.time_label.setStyleSheet("color:white;")
        self.time_label.setAlignment(Qt.AlignCenter)

        self.date_label = QLabel("----")
        self.date_label.setFont(QFont("Helvetica", 16))
        self.date_label.setStyleSheet("color:lightgray;")
        self.date_label.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(self.time_label)
        self.main_layout.addWidget(self.date_label)

        # ---------------- TOP ROW ----------------
        top_row = QHBoxLayout()

        # NEWS
        self.news_frame = QFrame()
        self.news_frame.setStyleSheet("background:#111;")
        news_layout = QVBoxLayout(self.news_frame)

        title = QLabel("📰 Top Headlines")
        title.setFont(QFont("Helvetica", 18, QFont.Bold))
        title.setStyleSheet("color:white;")
        news_layout.addWidget(title)

        self.news_labels = []
        for _ in range(5):
            lbl = QLabel("")
            lbl.setStyleSheet("color:lightgray;")
            lbl.setWordWrap(True)
            news_layout.addWidget(lbl)
            self.news_labels.append(lbl)

        # WEATHER
        self.weather_frame = QFrame()
        weather_layout = QVBoxLayout(self.weather_frame)

        self.city_label = QLabel("📍 --")
        self.city_label.setFont(QFont("Helvetica", 16, QFont.Bold))
        self.city_label.setStyleSheet("color:white;")

        self.weather_icon = QLabel()
        self.weather_temp = QLabel("--°C | --")
        self.weather_temp.setFont(QFont("Helvetica", 18, QFont.Bold))
        self.weather_temp.setStyleSheet("color:white;")

        weather_layout.addWidget(self.city_label)
        weather_layout.addWidget(self.weather_icon)
        weather_layout.addWidget(self.weather_temp)

        # FORECAST
        self.forecast_layout = QHBoxLayout()
        self.forecast_cols = []

        for _ in range(NUM_FORECAST_DAYS):
            col = QVBoxLayout()

            day = QLabel("---")
            day.setStyleSheet("color:white; font-weight:bold;")

            icon = QLabel()
            high = QLabel("H: --°C")
            low = QLabel("L: --°C")

            high.setStyleSheet("color:#ff5252;")
            low.setStyleSheet("color:#40c4ff;")

            col.addWidget(day)
            col.addWidget(icon)
            col.addWidget(high)
            col.addWidget(low)

            self.forecast_layout.addLayout(col)
            self.forecast_cols.append((day, icon, high, low))

        weather_layout.addLayout(self.forecast_layout)

        top_row.addWidget(self.news_frame, 3)
        top_row.addWidget(self.weather_frame, 2)

        self.main_layout.addLayout(top_row)

        # ---------------- SYSTEM ----------------
        self.system_label = QLabel("")
        self.system_label.setFont(QFont("Helvetica", 14))
        self.system_label.setStyleSheet("color:orange;")
        self.system_label.setAlignment(Qt.AlignRight)
        self.main_layout.addWidget(self.system_label)

        # ---------------- THOUGHT ----------------
        self.thought_label = QLabel("")
        self.thought_label.setFont(QFont("Helvetica", 16, QFont.StyleItalic))
        self.thought_label.setStyleSheet("color:yellow;")
        self.thought_label.setAlignment(Qt.AlignCenter)
        self.thought_label.setWordWrap(True)
        self.main_layout.addWidget(self.thought_label)

    # ======================================================
    # TIMERS
    # ======================================================
    def start_timers(self):
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)

        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.update_display)
        self.data_timer.start(REFRESH_INTERVAL)

        self.update_display()

    # ======================================================
    # UPDATES
    # ======================================================
    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))
        self.date_label.setText(now.strftime("%A, %d %B %Y"))

    def update_display(self):
        data = get_all_data()

        # WEATHER
        weather = data.get("weather", {})
        forecast = weather.get("forecasts", [])

        self.city_label.setText(f"📍 {weather.get('city','--')}")
        self.weather_temp.setText(
            f"{weather.get('temp','--')}°C | {forecast[0]['desc'] if forecast else '--'}"
        )

        if forecast:
            self.weather_icon.setPixmap(
                self.get_weather_icon(forecast[0].get("desc", ""))
            )

        for i, col in enumerate(self.forecast_cols):
            if i < len(forecast):
                d, icon, h, l = col
                f = forecast[i]
                d.setText(f["day"].upper())
                icon.setPixmap(self.get_weather_icon(f["desc"]))
                h.setText(f"H: {f['max']}°C")
                l.setText(f"L: {f['min']}°C")

        # NEWS
        news = data.get("news", [])
        for i, lbl in enumerate(self.news_labels):
            lbl.setText(news[i] if i < len(news) else "")

        # SYSTEM
        sysd = data.get("system", {})
        self.system_label.setText(
            f"💻 CPU: {sysd.get('cpu','--')}%   "
            f"RAM: {sysd.get('ram','--')}%   "
            f"Disk: {sysd.get('disk','--')}%"
        )

        # THOUGHT
        self.thought_label.setText(
            f"💭 Thought of the Day:\n{data.get('thought','')}"
        )


# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SmartMirror()
    win.showFullScreen()
    sys.exit(app.exec_())
