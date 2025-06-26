# afb_web.py
from flask import Flask, Response
import cv2
import threading
import time

app = Flask(__name__)
streams = {}

def im_show(title, frame, slot=0):
    streams[slot] = frame

def generate(slot):
    while True:
        frame = streams.get(slot, None)
        if frame is not None:
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed/<int:slot>')
def video_feed(slot):
    return Response(generate(slot), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_server():
    thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000), daemon=True)
    thread.start()
