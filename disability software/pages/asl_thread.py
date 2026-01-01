from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import mediapipe as mp

class ASLCameraThread(QThread):
    frame_signal = pyqtSignal(object, str)

    def __init__(self, asl_model, ui_page):
        super().__init__()
        self.asl_model = asl_model
        self.ui_page = ui_page   # reference to ASLPage
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            pred, hand, _ = self.asl_model.predict_frame(
                frame,
                detect_alpha=self.ui_page.cb_alpha.isChecked(),
                detect_number=self.ui_page.cb_number.isChecked()
            )

            if hand:
                self.asl_model.drawer.draw_landmarks(
                    frame, hand, mp.solutions.hands.HAND_CONNECTIONS
                )

            self.frame_signal.emit(frame, pred)

        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
