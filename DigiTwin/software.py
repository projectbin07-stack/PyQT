from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QAction, QStatusBar, QDockWidget, QTextEdit, QPushButton, QSpacerItem, QSizePolicy, QLabel, QLineEdit
from PyQt5.QtCore import QTimer, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter
import sys
import pygame
import serial
import cv2
import time
import math
import folium


class PygameWidget(QWidget):
    serial_data_received = pyqtSignal(str)

    def __init__(self, parent=None):
        super(PygameWidget, self).__init__(parent)
        self.initPygame()
        self.initUI()

    def initPygame(self):
        pygame.init()
        self.size = (800, 600)
        self.screen = pygame.Surface(self.size)
        self.clock = pygame.time.Clock()

        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)

        self.pointer_x = self.size[0] * 3 // 4
        self.pointer_y = self.size[1] // 2
        self.pointer_angle = 0

        self.POINTER_SPEED = 2
        self.POINTER_SIZE = 7
        self.LINE_THICKNESS = 5

        self.drawing_points = []
        self.path_points = []

        self.joystick_commands = []

        try:
            self.ser = serial.Serial('COM3', 9600)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.ser = None

        self.joy1X_timer_start = None

        self.returning = False
        self.return_completed = False
        self.replaying = False
        self.replay_index = 0

        self.drawing_mode = False
        self.mouse_pressed = False

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePygame)
        self.timer.start(30)

        self.button_position = Qt.AlignBottom | Qt.AlignRight
        self.button_size = QSize(100, 50)
        self.button_spacing = 10

        self.button_layout = QVBoxLayout()
        self.button_layout.setSpacing(self.button_spacing)

        self.button1 = QPushButton("Reset")
        self.button2 = QPushButton("Return")
        self.button3 = QPushButton("Follow Path")
        self.button4 = QPushButton("Draw")

        self.button1.clicked.connect(self.resetPath)
        self.button2.clicked.connect(self.returnToStart)
        self.button3.clicked.connect(self.replayPath)
        self.button4.clicked.connect(self.button4Action)

        self.button1.setFixedSize(self.button_size)
        self.button2.setFixedSize(self.button_size)
        self.button3.setFixedSize(self.button_size)
        self.button4.setFixedSize(self.button_size)

        self.button_layout.addWidget(self.button1)
        self.button_layout.addWidget(self.button2)
        self.button_layout.addWidget(self.button3)
        self.button_layout.addWidget(self.button4)

        self.hbox = QHBoxLayout()
        self.hbox.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.hbox.addLayout(self.button_layout)

        self.layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addLayout(self.hbox)

    def updatePygame(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.KEYDOWN:
                self.handleKeyPress(event.key)
                if self.ser:
                    if event.key == pygame.K_w:
                        self.ser.write(b'w\n')
                    elif event.key == pygame.K_a:
                        self.ser.write(b'a\n')
                    elif event.key == pygame.K_s:
                        self.ser.write(b's\n')
                    elif event.key == pygame.K_d:
                        self.ser.write(b'd\n')
                    elif event.key == pygame.K_SPACE:
                        self.ser.write(b'space\n')
                    elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        self.ser.write(b'ctrl\n')

        if not self.returning and not self.replaying:
            if self.ser and self.ser.in_waiting > 0:
                try:
                    data = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    self.serial_data_received.emit(data)
                    if data == "button1":
                        self.resetPath()
                    elif data == "button2":
                        self.returnToStart()
                    elif data == "button3":
                        self.replayPath()
                    elif data == "button4":
                        self.button4Action()
                    else:
                        data = data.split(',')
                        if len(data) == 2:
                            joy1X = int(data[0])
                            joy1Y = int(data[1])

                            command = None

                            if joy1Y > 600:
                                self.pointer_y -= self.POINTER_SPEED * \
                                    math.cos(math.radians(self.pointer_angle))
                                self.pointer_x += self.POINTER_SPEED * \
                                    math.sin(math.radians(self.pointer_angle))
                                command = 'f'
                            elif joy1Y < 100:
                                self.pointer_y += self.POINTER_SPEED * \
                                    math.cos(math.radians(self.pointer_angle))
                                self.pointer_x -= self.POINTER_SPEED * \
                                    math.sin(math.radians(self.pointer_angle))
                                command = 'b'

                            current_time = time.time()
                            if joy1X > 600:
                                if self.joy1X_timer_start is None:
                                    self.joy1X_timer_start = current_time
                                else:
                                    elapsed_time = current_time - self.joy1X_timer_start
                                    self.pointer_angle -= 45 * \
                                        (elapsed_time / 1.0)
                                    self.joy1X_timer_start = current_time
                                command = 'r'
                            elif joy1X < 100:
                                if self.joy1X_timer_start is None:
                                    self.joy1X_timer_start = current_time
                                else:
                                    elapsed_time = current_time - self.joy1X_timer_start
                                    self.pointer_angle += 45 * \
                                        (elapsed_time / 1.0)
                                    self.joy1X_timer_start = current_time
                                command = 'l'
                            else:
                                self.joy1X_timer_start = None

                            if command:
                                self.joystick_commands.append(command)
                                print(command)

                except UnicodeDecodeError as e:
                    print(f"Decoding error: {e}")

            if self.drawing_points:
                self.return_completed = False
            self.drawing_points.append((self.pointer_x, self.pointer_y))
            self.path_points.append((self.pointer_x, self.pointer_y))

        elif self.returning:
            if self.drawing_points:
                self.pointer_x, self.pointer_y = self.drawing_points.pop()
            else:
                self.returning = False
                self.return_completed = True
        elif self.replaying:
            if self.replay_index < len(self.path_points):
                self.pointer_x, self.pointer_y = self.path_points[self.replay_index]
                self.replay_index += 1
            else:
                self.replaying = False
                self.replay_index = 0

        self.screen.fill(self.WHITE)

        if len(self.drawing_points) > 1:
            adjusted_points = [(x - self.pointer_x + self.size[0] // 2, y -
                                self.pointer_y + self.size[1] // 2) for x, y in self.drawing_points]
            pygame.draw.lines(self.screen, self.RED, False,
                              adjusted_points, self.LINE_THICKNESS)

        pygame.draw.circle(
            self.screen, self.RED, (self.size[0] // 2, self.size[1] // 2), self.POINTER_SIZE)

        self.update()

    def paintEvent(self, event):
        image = QImage(self.screen.get_buffer().raw,
                       self.size[0], self.size[1], QImage.Format_RGB32)
        pixmap = QPixmap.fromImage(image)
        painter = QPainter(self)
        painter.drawPixmap(0, 0, pixmap)

    def resizeEvent(self, event):
        self.size = (self.width(), self.height())
        self.screen = pygame.Surface(self.size)
        super(PygameWidget, self).resizeEvent(event)

    def sizeHint(self):
        return QSize(self.size[0], self.size[1])

    def resetPath(self):
        self.drawing_points.clear()
        self.joystick_commands.clear()
        self.return_completed = False
        self.path_points.clear()
        self.pointer_angle = 0
        self.update()

    def closeEvent(self, event):
        if self.ser and self.ser.is_open:
            self.ser.close()
        super(PygameWidget, self).closeEvent(event)

    def returnToStart(self):
        if not self.return_completed:
            self.returning = True
            if self.ser:
                self.ser.write(b'return\n')

    def replayPath(self):
        if self.path_points:
            self.pointer_x, self.pointer_y = self.path_points[0]
            self.replaying = True
            self.replay_index = 0
            if self.ser:
                self.ser.write(b'follow\n')

    def button4Action(self):
        print("Draw action triggered")
        self.drawing_mode = True
        self.button4.setText("Stop Drawing")
        self.button4.clicked.disconnect()
        self.button4.clicked.connect(self.stopDrawing)

    def stopDrawing(self):
        print("Stop drawing action triggered")
        self.drawing_mode = False
        self.button4.setText("Draw")
        self.button4.clicked.disconnect()
        self.button4.clicked.connect(self.button4Action)

    def mousePressEvent(self, event):
        if self.drawing_mode and event.button() == Qt.LeftButton:
            self.mouse_pressed = True

    def mouseMoveEvent(self, event):
        if self.drawing_mode and self.mouse_pressed:
            self.pointer_x = event.x()
            self.pointer_y = event.y()
            self.drawing_points.append((self.pointer_x, self.pointer_y))
            self.path_points.append((self.pointer_x, self.pointer_y))
            self.update()

    def mouseReleaseEvent(self, event):
        if self.drawing_mode and event.button() == Qt.LeftButton:
            self.mouse_pressed = False


class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super(CameraWidget, self).__init__(parent)
        self.initUI()
        self.capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.current_resolution = (640, 480)

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.input_layout = QVBoxLayout()
        self.layout.addLayout(self.input_layout, 0)

        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText(
            "IP address")
        self.input_layout.addWidget(self.ip_input, 0, Qt.AlignCenter)

        self.start_button = QPushButton("Start Stream", self)
        self.start_button.clicked.connect(self.on_start_button_clicked)
        self.input_layout.addWidget(self.start_button, 0, Qt.AlignCenter)

        self.error_label = QLabel(self)
        self.layout.addWidget(self.error_label, 0, Qt.AlignCenter)

        self.label = QLabel(self)
        self.layout.addWidget(self.label, 0, Qt.AlignCenter)

    def on_start_button_clicked(self):
        ip_address = self.ip_input.text().strip()
        if ip_address:
            url = f"http://{ip_address}:81/stream"
            if self.start_camera(url):
                self.error_label.setText("")
                self.ip_input.hide()
                self.start_button.hide()
                self.timer.start(30)
            else:
                self.error_label.setText(
                    "Invalid IP address or unable to connect to the stream.")
        else:
            self.error_label.setText("Please enter a valid IP address.")

    def start_camera(self, ip_address):
        self.capture = cv2.VideoCapture(ip_address)
        return self.capture.isOpened()

    def set_resolution(self, resolution):
        self.current_resolution = resolution
        if self.capture and self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    def update_frame(self):
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.resize(frame, self.current_resolution)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(
                    frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        if self.capture and self.capture.isOpened():
            self.capture.release()
        super(CameraWidget, self).closeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Pygame in Qt')
        self.setGeometry(0, 0, 1121, 895)

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.menuFILE = QMenu("File", self)
        self.menubar.addMenu(self.menuFILE)

        self.menuView = QMenu("Edit", self)
        self.menubar.addMenu(self.menuView)

        self.menuEdit = QMenu("View", self)
        self.menubar.addMenu(self.menuEdit)

        self.menuResolution = QMenu("Resolution", self)
        self.menubar.addMenu(self.menuResolution)

        self.menuAbout = QMenu("About", self)
        self.menubar.addMenu(self.menuAbout)

        self.create_file_actions()
        self.create_view_actions()
        self.create_resolution_actions()

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.create_dock_widgets()

        self.joy1X = 0
        self.joy1Y = 0

    def create_file_actions(self):
        self.actionRefresh = QAction("Refresh", self)
        self.actionRefresh.triggered.connect(self.refresh_code)
        self.menuFILE.addAction(self.actionRefresh)

        self.actionReset = QAction("Reset", self)
        self.actionReset.triggered.connect(self.reset_code)
        self.menuFILE.addAction(self.actionReset)

        self.actionFlash = QAction("Flash", self)
        self.actionFlash.triggered.connect(self.Flash)
        self.menuFILE.addAction(self.actionFlash)

    def create_view_actions(self):
        self.actionWidgetBox = QAction("3D View", self, checkable=True)
        self.menuEdit.addAction(self.actionWidgetBox)
        self.actionWidgetBox.toggled.connect(self.toggle_dock_widget)

        self.actionSerialMonitor = QAction(
            "Serial Monitor", self, checkable=True)
        self.menuEdit.addAction(self.actionSerialMonitor)
        self.actionSerialMonitor.toggled.connect(self.toggle_dock_widget)

        self.actionReadings = QAction("Readings", self, checkable=True)
        self.menuEdit.addAction(self.actionReadings)
        self.actionReadings.toggled.connect(self.toggle_dock_widget)

        self.actionPropertyEditor = QAction("Camera", self, checkable=True)
        self.menuEdit.addAction(self.actionPropertyEditor)
        self.actionPropertyEditor.toggled.connect(self.toggle_dock_widget)

        self.actionResourceBrowser = QAction("Path", self, checkable=True)
        self.menuEdit.addAction(self.actionResourceBrowser)
        self.actionResourceBrowser.toggled.connect(self.toggle_dock_widget)

        self.actionActionEditor = QAction("Project", self, checkable=True)
        self.menuEdit.addAction(self.actionActionEditor)
        self.actionActionEditor.toggled.connect(self.toggle_dock_widget)

        self.actionSignalSlotEditor = QAction("Code", self, checkable=True)
        self.menuEdit.addAction(self.actionSignalSlotEditor)
        self.actionSignalSlotEditor.toggled.connect(self.toggle_dock_widget)

    def create_resolution_actions(self):
        self.resolution_actions = []
        resolutions = [
            ("UXGA (1600x1200)", (1600, 1200)),
            ("SXGA (1280x1024)", (1280, 1024)),
            ("HD (1280x720)", (1280, 720)),
            ("XGA (1024x768)", (1024, 768)),
            ("SVGA (800x600)", (800, 600)),
            ("VGA (640x480)", (640, 480)),
            ("HVGA (480x320)", (480, 320)),
            ("CIF (400x296)", (400, 296)),
            ("QVGA (320x240)", (320, 240)),
            ("240x240", (240, 240)),
            ("HQVGA (240x176)", (240, 176)),
            ("QCIF (176x144)", (176, 144)),
            ("QQVGA (160x120)", (160, 120)),
            ("96x96", (96, 96))
        ]

        for label, resolution in resolutions:
            action = QAction(label, self, checkable=True)
            action.triggered.connect(
                lambda checked, res=resolution: self.set_resolution(res))
            self.menuResolution.addAction(action)
            self.resolution_actions.append(action)

    def set_resolution(self, resolution):
        self.camera_widget.set_resolution(resolution)
        for action in self.resolution_actions:
            action.setChecked(False)
        sender = self.sender()
        sender.setChecked(True)

    def create_dock_widgets(self):
        self.dockWidgetBox = QDockWidget("3D View", self)
        self.dockWidgetBox.setWidget(QTextEdit())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidgetBox)
        self.dockWidgetBox.hide()
        self.dockWidgetBox.visibilityChanged.connect(
            lambda visible: self.actionWidgetBox.setChecked(visible))

        self.dockSerialMonitor = QDockWidget("Serial Monitor", self)
        self.serial_monitor = QTextEdit()
        self.dockSerialMonitor.setWidget(self.serial_monitor)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSerialMonitor)
        self.dockSerialMonitor.hide()
        self.dockSerialMonitor.visibilityChanged.connect(
            lambda visible: self.actionSerialMonitor.setChecked(visible))

        self.dockReadings = QDockWidget("Readings", self)
        self.readings_display = QTextEdit()
        self.dockReadings.setWidget(self.readings_display)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockReadings)
        self.dockReadings.hide()
        self.dockReadings.visibilityChanged.connect(
            lambda visible: self.actionReadings.setChecked(visible))

        self.dockPropertyEditor = QDockWidget("Camera", self)
        self.camera_widget = CameraWidget(self)
        self.dockPropertyEditor.setWidget(self.camera_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockPropertyEditor)
        self.dockPropertyEditor.hide()
        self.dockPropertyEditor.visibilityChanged.connect(
            lambda visible: self.actionPropertyEditor.setChecked(visible))

        self.dockResourceBrowser = QDockWidget("Path", self)
        self.pygame_widget = PygameWidget(self)
        self.pygame_widget.serial_data_received.connect(
            self.update_serial_monitor)
        self.pygame_widget.serial_data_received.connect(self.update_Readings)
        self.dockResourceBrowser.setWidget(self.pygame_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockResourceBrowser)
        self.dockResourceBrowser.show()
        self.dockResourceBrowser.visibilityChanged.connect(
            lambda visible: self.actionResourceBrowser.setChecked(visible))

        self.dockActionEditor = QDockWidget("Project", self)
        self.dockActionEditor.setWidget(QTextEdit())
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockActionEditor)
        self.dockActionEditor.hide()
        self.dockActionEditor.visibilityChanged.connect(
            lambda visible: self.actionActionEditor.setChecked(visible))

        self.dockSignalSlotEditor = QDockWidget("Code", self)
        self.dockSignalSlotEditor.setWidget(QTextEdit())
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockSignalSlotEditor)
        self.dockSignalSlotEditor.hide()
        self.dockSignalSlotEditor.visibilityChanged.connect(
            lambda visible: self.actionSignalSlotEditor.setChecked(visible))

    def toggle_dock_widget(self, checked):
        sender = self.sender()
        if sender == self.actionWidgetBox:
            self.dockWidgetBox.setVisible(checked)
        elif sender == self.actionSerialMonitor:
            self.dockSerialMonitor.setVisible(checked)
        elif sender == self.actionReadings:
            self.dockReadings.setVisible(checked)
        elif sender == self.actionPropertyEditor:
            self.dockPropertyEditor.setVisible(checked)
        elif sender == self.actionResourceBrowser:
            self.dockResourceBrowser.setVisible(checked)
        elif sender == self.actionActionEditor:
            self.dockActionEditor.setVisible(checked)
        elif sender == self.actionSignalSlotEditor:
            self.dockSignalSlotEditor.setVisible(checked)

    def update_serial_monitor(self, data):
        data_parts = data.split(',')
        if len(data_parts) == 16:
            self.joy1X = int(data_parts[0])
            self.joy1Y = int(data_parts[1])

        self.serial_monitor.append(f"Data: {data}, joy1X: {
                                   self.joy1X}, joy1Y: {self.joy1Y}")

    def update_Readings(self, data):
        dataset = data.split(',')
        if len(dataset) == 16:
            joyx = int(dataset[0])
            joyy = int(dataset[1])
            lat = float(dataset[2])
            latdir = str(dataset[3])
            long = float(dataset[4])
            longdir = str(dataset[5])
            volt = int(dataset[6])
            current = int(dataset[7])
            power = int(dataset[8])
            date = int(dataset[9])
            month = int(dataset[10])
            year = int(dataset[11])
            hour = int(dataset[12])
            minute = int(dataset[13])
            second = int(dataset[14])
            sat = int(dataset[15])

            self.readings_display.append(
                f"Latitude: {lat}°\n"
                f"Longitude: {long}{latdir}°\n"
                f"Voltage: {volt}{longdir} V\n"
                f"Current: {current} mA\n"
                f"Power: {power} mW\n"
                f"Date: {date}/{month}/{year}\n"
                f"Time: {hour}:{minute}:{second}\n"
                f"Satellites: {sat}\n"
                "----------------------------------------"
            )

    def refresh_code(self):
        self.close()
        self.__init__()
        self.show()
        print("refreshed")

    def reset_code(self):
        if hasattr(self.pygame_widget, 'ser') and self.pygame_widget.ser:
            self.pygame_widget.ser.write(b'Reset\n')
            print("Code reset")

    def Flash(self):
        if hasattr(self.pygame_widget, 'ser') and self.pygame_widget.ser:
            self.pygame_widget.ser.write(b'Flash\n')
            print("Flash")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())