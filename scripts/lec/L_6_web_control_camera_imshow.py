from flask import Flask, render_template, request
import afb
import afb_web
import threading
import time
import cv2

app = Flask(__name__)
afb.gpio.init()
afb.camera.init(640, 480, 30)
afb_web.start_server()  # 영상 서버 실행

servo_angle = 90

# 🔁 실시간 영상 전송 루프
def camera_loop():
    while True:
        frame = afb.camera.get_image()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        afb_web.im_show("AFB Camera", frame_rgb, slot=0)
        time.sleep(0.03)

# 백그라운드로 실행
threading.Thread(target=camera_loop, daemon=True).start()

@app.route('/')
def index():
    return render_template("index3.html")

@app.route('/key', methods=["POST"])
def key():
    global servo_angle
    key = request.form.get("key")

    if key == "ArrowUp":
        afb.gpio.motor(30, 1, 1)
    elif key == "ArrowDown":
        afb.gpio.motor(30, -1, 1)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)  # 영상은 5000, 제어는 8000
