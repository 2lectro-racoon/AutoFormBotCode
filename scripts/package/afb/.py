from flask import Flask, render_template, request, Response
import afb
import time
import cv2
import threading
import os

if not os.path.exists("captures"):
    os.makedirs("captures")

app = Flask(__name__)

afb.gpio.init()
afb.camera.init(640, 480, 30)
servo_angle = 90

latest_frame = None

def generate():
    global latest_frame
    while True:
        frame = afb.camera.get_image()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        latest_frame = frame_rgb.copy()  # 복사 저장
        _, jpeg = cv2.imencode('.jpg', frame_rgb)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.03)

@app.route('/capture', methods=["POST"])
def capture():
    global latest_frame
    if latest_frame is not None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = f"captures/frame_{timestamp}.jpg"
        cv2.imwrite(path, cv2.cvtColor(latest_frame, cv2.COLOR_RGB2BGR))
        print(f"✅ 캡처됨: {path}")
    return '', 204

# 메인 페이지
@app.route('/')
def index():
    return render_template("index4.html")

# 키보드 제어 처리
@app.route('/key', methods=["POST"])
def key():
    global servo_angle
    key = request.form.get("key")

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

    return '', 204

# 영상 스트리밍
@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Callable function to start the Flask app
def capture():
    app.run(host="0.0.0.0", port=5000)
