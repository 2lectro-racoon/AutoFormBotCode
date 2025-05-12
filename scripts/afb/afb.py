# afb/camera.py

import cv2
import subprocess
import time

_cap = None
_proc = None

def _start_stream():
    global _proc
    if _proc is None:
        _proc = subprocess.Popen([
            "libcamera-vid",
            "-t", "0",
            "--width", "640",
            "--height", "480",
            "--framerate", "30",
            "--listen",
            "-o", "tcp://0.0.0.0:8888"
        ])
        time.sleep(2)  # Wait for the stream to be ready

def _open_capture():
    global _cap
    if _cap is None:
        _cap = cv2.VideoCapture("tcp://localhost:8888", cv2.CAP_FFMPEG)
        while not _cap.isOpened():
            time.sleep(0.1)

def get_image():
    global _cap
    if _cap is None:
        _start_stream()
        _open_capture()
    ret, frame = _cap.read()
    if not ret:
        raise RuntimeError("Failed to capture frame from camera")
    return frame