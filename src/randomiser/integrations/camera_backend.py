from __future__ import annotations

from typing import Any


class OpenCVCameraBackend:
    def __init__(self, device_index: int = 0) -> None:
        self.device_index = device_index

    def is_available(self) -> bool:
        try:
            import cv2
        except ImportError:
            return False

        capture = cv2.VideoCapture(self.device_index)
        try:
            return bool(capture.isOpened())
        finally:
            capture.release()

    def capture_frame(self) -> Any | None:
        import cv2

        capture = cv2.VideoCapture(self.device_index)
        try:
            if not capture.isOpened():
                return None
            ok, frame = capture.read()
            if not ok:
                return None
            return frame
        finally:
            capture.release()
