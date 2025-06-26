TARGET_SIZE = (640, 480)  # (width, height)
import threading
from flask import Flask, Response, request
import cv2
import time
import afb

app = Flask(__name__)
streams = [{"frame": None, "name": None} for _ in range(4)]  # index 0–3
server_started = False

latest_frame = None
servo_angle = 90

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

@app.route('/video_feed')
def single_video_feed():
    def generate():
        global latest_frame
        while True:
            frame = afb.camera.get_image()
            latest_frame = frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            _, jpeg = cv2.imencode('.jpg', frame_rgb)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(0.03)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream')
def stream_viewer():
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

@app.route('/capture', methods=['GET', 'POST'])
def capture_page():
    if request.method == 'POST':
        # handle capture action, e.g. save image or other
        pass
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
      <meta charset="UTF-8">
      <title>AFB 자동차 키보드 제어</title>
      <script>
        document.addEventListener("keydown", function(event) {
          fetch("/key", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: "key=" + event.key
          });
        });

        document.addEventListener("keyup", function(event) {
          fetch("/key", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: "key=stop"
          });
        });

        document.addEventListener("keydown", function(event) {
          if (event.key === "a") {
            fetch("/imwrite", { method: "POST" });
          }
        });
      </script>
    </head>
    <body>
      <h2>AFB 자동차 키보드 제어</h2>
      <p><strong>페이지 클릭 후 방향키(↑ ↓ ← →)로 제어하세요.</strong></p>
      <hr>
      <h3>🚗 실시간 카메라 영상</h3>
      <img src="/video_feed" width="640" height="480">
    </body>
    </html>
    '''

@app.route('/key', methods=['POST'])
def key_control():
    global servo_angle
    key = request.form.get('key')
    if key == "ArrowUp":
        afb.gpio.motor(100, 1, 1)
    elif key == "ArrowDown":
        afb.gpio.motor(100, -1, 1)
    elif key == "ArrowLeft":
        if servo_angle != 40:
            afb.gpio.servo(40)
            servo_angle = 40
    elif key == "ArrowRight":
        if servo_angle != 140:
            afb.gpio.servo(140)
            servo_angle = 140
    elif key == "stop":
        afb.gpio.motor(0, 1, 1)
        if servo_angle != 90:
            afb.gpio.servo(90)
            servo_angle = 90
    return ('', 204)

def imwrite():
    global latest_frame
    if latest_frame is not None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = f"captures/frame_{timestamp}.jpg"
        cv2.imwrite(path, cv2.cvtColor(latest_frame, cv2.COLOR_RGB2BGR))
        print(f"✅ 캡처됨: {path}")
    return '', 204

def imshow(name, frame, slot):
    global server_started
    frame = cv2.resize(frame, TARGET_SIZE)
    if 0 <= slot < 4:
        streams[slot]["frame"] = frame
        streams[slot]["name"] = name

    if not server_started:
        threading.Thread(target=flask_thread, daemon=True).start()
        server_started = True

def capture():
    global server_started
    if not server_started:
        flask_thread()
        server_started = True