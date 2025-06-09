TARGET_SIZE = (640, 480)  # (width, height)
import threading
from flask import Flask, Response
import cv2
import time

app = Flask(__name__)
streams = [None] * 4  # index 0–3
server_started = False

def flask_thread():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

@app.route('/video_feed/<int:slot>')
def video_feed(slot):
    def generate():
        while True:
            frame = streams[slot]
            if frame is None:
                time.sleep(0.01)
                continue
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html>
    <head><title>AutoFormBot Multi Stream</title></head>
    <body>
        <h1>Multi Stream Viewer</h1>
        <table>
        <tr>
            <td><h3>Slot 0</h3><img src="/video_feed/0" width="320" height="240"></td>
            <td><h3>Slot 1</h3><img src="/video_feed/1" width="320" height="240"></td>
        </tr>
        <tr>
            <td><h3>Slot 2</h3><img src="/video_feed/2" width="320" height="240"></td>
            <td><h3>Slot 3</h3><img src="/video_feed/3" width="320" height="240"></td>
        </tr>
        </table>
    </body>
    </html>
    '''

def imshow(name, frame, slot):
    global server_started
    frame = cv2.resize(frame, TARGET_SIZE)
    if 0 <= slot < 4:
        streams[slot] = frame

    if not server_started:
        threading.Thread(target=flask_thread, daemon=True).start()
        server_started = True