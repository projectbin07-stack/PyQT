import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from .services.admin_service import get_admin
from .views.login_view import LoginView
from .views.dashboard_view import DashboardView
from .views.locker_status import LockerStatusView
from .views.logs_view import LogsView
from .views.force_open import ForceOpenView
from .views.admin_info import AdminInfoView
from .views.system_health import SystemHealthView
from .constants import BACKGROUND_COLOR


class OpeningPage(QWidget):
    def __init__(self, locker_no, on_done):
        super().__init__()
        self.setStyleSheet(f"QWidget{{background:transparent;color:white;}}")
        from PyQt5.QtWidgets import QLabel, QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        t = QLabel("OPENING LOCKER")
        t.setStyleSheet("font-size:32px;font-weight:700;")
        t.setAlignment(Qt.AlignCenter)
        s = QLabel(f"LOCKER {locker_no}")
        s.setStyleSheet("font-size:18px;color:rgba(255,255,255,0.8);")
        s.setAlignment(Qt.AlignCenter)
        layout.addWidget(t)
        layout.addWidget(s)
        QTimer.singleShot(1500, on_done)


class DonePage(QWidget):
    def __init__(self, on_finish):
        super().__init__()
        from PyQt5.QtWidgets import QLabel, QVBoxLayout
        self.setStyleSheet(f"QWidget{{background:transparent;color:white;}}")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        d = QLabel("DONE")
        d.setStyleSheet("font-size:40px;font-weight:700;")
        d.setAlignment(Qt.AlignCenter)
        layout.addWidget(d)
        QTimer.singleShot(1200, on_finish)


class AdminWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.admin = get_admin()
        self.selected_locker = None

        self.setStyleSheet(f"QWidget {{ background:{BACKGROUND_COLOR}; color:white; font-family:Inter,'Segoe UI'; }}")
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)
        self.root.setAlignment(Qt.AlignCenter)

        self.current = None
        self.show_login()

    def _set_view(self, w):
        # clear
        while self.root.count():
            item = self.root.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self.current = w
        self.root.addWidget(w)

    def show_login(self):
        v = LoginView(self.admin)
        v.authenticated.connect(self.show_dashboard)
        self._set_view(v)

    def show_dashboard(self):
        v = DashboardView()
        v.locker_status.connect(self.show_locker_status)
        v.logs.connect(self.show_logs)
        v.force_open.connect(self.show_force_open)
        v.admin_info.connect(self.show_admin_info)
        v.system_health.connect(self.show_system_health)
        v.logout.connect(self.go_home)
        self._set_view(v)

    def show_locker_status(self):
        v = LockerStatusView()
        v.backRequested.connect(self.show_dashboard)
        self._set_view(v)

    def show_logs(self):
        v = LogsView()
        v.backRequested.connect(self.show_dashboard)
        self._set_view(v)

    def show_force_open(self):
        v = ForceOpenView(self.admin)
        v.backRequested.connect(self.show_dashboard)
        v.confirmed.connect(self._do_force_open)
        self._set_view(v)

    def _do_force_open(self):
        # Show opening -> done -> dashboard
        def after_open():
            self._set_view(DonePage(self.show_dashboard))

        self._set_view(OpeningPage(self.selected_locker or "-", after_open))

    def show_admin_info(self):
        v = AdminInfoView(self.admin)
        v.backRequested.connect(self.show_dashboard)
        self._set_view(v)

    def show_system_health(self):
        v = SystemHealthView()
        v.backRequested.connect(self.show_dashboard)
        self._set_view(v)

    def go_home(self):
        main = self.window()
        if not hasattr(main, "load_page"):
            from PyQt5.QtWidgets import QApplication
            for w in QApplication.topLevelWidgets():
                if hasattr(w, "load_page"):
                    main = w
                    break
        if hasattr(main, "load_page"):
            main.load_page(None)
