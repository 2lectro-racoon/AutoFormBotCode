import threading
from flask import Flask, Response
import cv2
import time

app = Flask(__name__)
streams = {}  # name -> latest_frame
server_started = False

def flask_thread():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

@app.route('/<name>/video_feed')
def video_feed(name):
    def generate():
        while True:
            frame = streams.get(name)
            if frame is None:
                time.sleep(0.01)
                continue

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/<name>')
def index(name):
    return f'''
    <!doctype html>
    <html>
    <head>
        <title>AutoFormBot Video Feed - {name}</title>
    </head>
    <body>
        <h1>Stream: {name}</h1>
        <img src="/{name}/video_feed" width="640" height="480">
    </body>
    </html>
    '''

def imshow(name, frame):
    global server_started
    streams[name] = frame

    if not server_started:
        threading.Thread(target=flask_thread, daemon=True).start()
        server_started = True