from flask import Flask, render_template, request, Response
import afb
import time
import cv2
import threading

app = Flask(__name__)

afb.gpio.init()
afb.camera.init(640, 480, 30)
servo_angle = 90

# 실시간 카메라 스트리밍 생성기
def generate():
    while True:
        frame = afb.camera.get_image()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, jpeg = cv2.imencode('.jpg', frame_rgb)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.03)


# 메인 페이지
@app.route('/')
def index():
    return render_template("index2.html")

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

# 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
