TARGET_SIZE = (640, 480)  # (width, height)
import threading
from flask import Flask, Response
import cv2
import time

app = Flask(__name__)
streams = [{"frame": None, "name": None} for _ in range(4)]  # index 0–3
server_started = False

def flask_thread():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

@app.route('/video_feed/<int:slot>')
def video_feed(slot):
    def generate():
        try:
            while True:
                frame = streams[slot]["frame"]
                if frame is None:
                    time.sleep(0.01)
                    continue
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.03)
        except GeneratorExit:
            print(f"[INFO] Client disconnected from slot {slot}")
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    html = '''
    <!doctype html>
    <html>
    <head>
        <title>AFB Stream Viewer</title>
        <style>
            .container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }
            .stream {
                text-align: center;
                flex: 1 1 300px;
            }
            img {
                width: 100%;
                max-width: 480px;
                height: auto;
                border: 1px solid #ccc;
            }
        </style>
    </head>
    <body>
        <h1>AFB Stream Viewer</h1>
        <div class="container">
    '''
    for idx in range(4):
        label = streams[idx]["name"] if streams[idx]["name"] else f"Slot {idx}"
        html += f'''
            <div class="stream">
                <h3>{label}</h3>
                <img src="/video_feed/{idx}">
            </div>
        '''
    html += '''
        </div>
    </body>
    </html>
    '''
    return html

def imshow(name, frame, slot):
    global server_started
    frame = cv2.resize(frame, TARGET_SIZE)
    if 0 <= slot < 4:
        streams[slot]["frame"] = frame
        streams[slot]["name"] = name

    if not server_started:
        threading.Thread(target=flask_thread, daemon=True).start()
        server_started = True