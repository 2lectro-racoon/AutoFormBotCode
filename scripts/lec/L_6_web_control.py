import sys
sys.path.append("/home/afbpi/afb")

from flask import Flask, render_template, request
import afb

app = Flask(__name__)

afb.gpio.init()
servo_angle = 90

@app.route('/')
def index():
    return render_template("index1.html")

@app.route('/key', methods=["POST"])
def key():
    global servo_angle
    key = request.form.get("key")

    if key == "ArrowUp":
        afb.gpio.motor(30, 1, 1)
    elif key == "ArrowDown":
        afb.gpio.motor(30, -1, 1)
    elif key == "ArrowLeft":
        afb.gpio.servo(40)
        servo_angle = 40
    elif key == "ArrowRight":
        afb.gpio.servo(140)
        servo_angle = 140
    elif key == "stop":
        afb.gpio.motor(0, 1, 1)
        afb.gpio.servo(90)
        servo_angle = 90

    return '', 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

