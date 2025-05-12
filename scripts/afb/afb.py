# afb/camera.py

import cv2
import time
from picamera2 import Picamera2

_picam2 = None

def _start_camera():
    global _picam2
    if _picam2 is None:
        _picam2 = Picamera2()
        _picam2.configure(_picam2.create_preview_configuration(main={"size": (640, 480)}))
        _picam2.start()
        time.sleep(1)  # Allow camera to warm up

def get_image():
    global _picam2
    if _picam2 is None:
        _start_camera()
    return _picam2.capture_array()