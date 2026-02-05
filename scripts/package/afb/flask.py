TARGET_SIZE = (640, 480)  # (width, height)
import threading
from flask import Flask, Response, request, jsonify
import cv2
import time
import afb

app = Flask(__name__)

@app.route('/angles')
def angles_api():
    """Return last-sent servo angles for debugging.

    Notes:
    - Values come from `afb.quad.getAngle()`.
    - If quad cache is not available, return 12x None.
    """
    try:
        angles = afb.quad.getAngle()  # expected: list of length 12
    except Exception:
        angles = [None] * 12

    # Always return exactly 12 values to keep the UI stable.
    if not isinstance(angles, list):
        angles = list(angles)
    if len(angles) < 12:
        angles = angles + [None] * (12 - len(angles))
    elif len(angles) > 12:
        angles = angles[:12]

    return jsonify({"angles": angles})

streams = [{"frame": None, "name": None} for _ in range(4)]  # index 0–3
server_started = False

latest_frame = None
servo_angle = 90

def flask_thread():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def startServer() -> None:
    """Start the Flask server if it is not already running.

    This allows using the web UI (e.g. /stream, /angles) without calling imshow().
    """
    global server_started
    if not server_started:
        threading.Thread(target=flask_thread, daemon=True).start()
        server_started = True

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
            .angles {
                width: 100%;
                max-width: 980px;
                margin: 20px auto;
                padding: 12px;
                border: 1px solid #ccc;
                background: #fff;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            }
            .angles-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            .angles-table td {
                border: 1px solid #ddd;
                text-align: center;
                padding: 8px;
            }
            .angles-ch {
                font-weight: 700;
            }
            .angles-val {
                font-size: 18px;
                line-height: 1.2;
            }
        </style>
        <script>
            const ORDER = [11, 10, 9, 0, 1, 2, 8, 7, 6, 3, 4, 5];

            async function fetchAngles() {
                try {
                    const res = await fetch('/angles', { cache: 'no-store' });
                    const data = await res.json();
                    const angles = (data && data.angles) ? data.angles : [];

                    for (let i = 0; i < ORDER.length; i++) {
                        const ch = ORDER[i];
                        const el = document.getElementById('angle-' + ch);
                        if (!el) continue;
                        const v = angles[ch];
                        el.textContent = (v === null || v === undefined) ? 'NL' : String(v);
                    }
                } catch (e) {
                    // Ignore fetch errors (server might be starting)
                }
            }

            document.addEventListener('DOMContentLoaded', () => {
                fetchAngles();
                setInterval(fetchAngles, 200);
            });
        </script>
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

        <div class="angles">
            <h3>Servo Angles (last sent)</h3>
            <table class="angles-table">
                <tr>
                    <td class="angles-ch">CH11</td>
                    <td class="angles-ch">CH10</td>
                    <td class="angles-ch">CH9</td>
                    <td class="angles-ch">CH0</td>
                    <td class="angles-ch">CH1</td>
                    <td class="angles-ch">CH2</td>
                </tr>
                <tr>
                    <td class="angles-val"><span id="angle-11">NL</span></td>
                    <td class="angles-val"><span id="angle-10">NL</span></td>
                    <td class="angles-val"><span id="angle-9">NL</span></td>
                    <td class="angles-val"><span id="angle-0">NL</span></td>
                    <td class="angles-val"><span id="angle-1">NL</span></td>
                    <td class="angles-val"><span id="angle-2">NL</span></td>
                </tr>
                <tr>
                    <td class="angles-ch">CH8</td>
                    <td class="angles-ch">CH7</td>
                    <td class="angles-ch">CH6</td>
                    <td class="angles-ch">CH3</td>
                    <td class="angles-ch">CH4</td>
                    <td class="angles-ch">CH5</td>
                </tr>
                <tr>
                    <td class="angles-val"><span id="angle-8">NL</span></td>
                    <td class="angles-val"><span id="angle-7">NL</span></td>
                    <td class="angles-val"><span id="angle-6">NL</span></td>
                    <td class="angles-val"><span id="angle-3">NL</span></td>
                    <td class="angles-val"><span id="angle-4">NL</span></td>
                    <td class="angles-val"><span id="angle-5">NL</span></td>
                </tr>
            </table>
            <p style="margin-top:10px; color:#666;">Updates every 200ms via <code>/angles</code></p>
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
        afb.car.motor(100)
        # afb.gpio.motor(100, 1, 1)
    elif key == "ArrowDown":
        afb.car.motor(-100)
        # afb.gpio.motor(100, -1, 1)
    elif key == "ArrowLeft":
        if servo_angle != 40:
            afb.car.servo(40)
            # afb.gpio.servo(40)
            servo_angle = 40
    elif key == "ArrowRight":
        if servo_angle != 140:
            afb.car.servo(140)
            # afb.gpio.servo(140)
            servo_angle = 140
    elif key == "stop":
        # afb.gpio.motor(0, 1, 1)
        afb.car.motor(0)
        if servo_angle != 90:
            afb.car.servo(90)
            # afb.gpio.servo(90)
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

    startServer()

def capture():
    """Backward-compatible helper to start the Flask server."""
    startServer()