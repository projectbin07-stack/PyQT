# pages/vision_thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from core.vision import YOLOEngine

class VisionThread(QThread):
    frame_signal = pyqtSignal(object)      # send frame to UI
    speak_ready_signal = pyqtSignal(list)  # send detections to UI when asked

    def __init__(self, cam_index=0):
        super().__init__()
        self.cam_index = cam_index
        self.running = True
        self.yolo = YOLOEngine()

        self._request_speak = False   # Flag set when user clicks Speak button or presses Space

    def request_speak(self):
        """Called by UI to trigger speech."""
        self._request_speak = True

    def run(self):
        cap = cv2.VideoCapture(self.cam_index)
        if not cap.isOpened():
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            detections = self.yolo.detect(frame)
            detected_pairs = []   # list of (label, position)

            # Draw bounding boxes & prepare TTS data
            for d in detections:
                x, y, w, h = d["box"]
                label = d["label"]
                pos = d["position"]

                pair = (label, pos)
                if pair not in detected_pairs:
                    detected_pairs.append(pair)

                text = f"{label} ({pos})"

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(frame, text, (x, max(y-6,10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            # Emit updated frame
            self.frame_signal.emit(frame)

            # Handle speech request
            if self._request_speak:
                self._request_speak = False  # reset flag
                self.speak_ready_signal.emit(detected_pairs)

        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
