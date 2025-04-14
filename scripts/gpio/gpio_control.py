# gpio_control.py

import pigpio
import atexit
from gpio_pins import PINS
# Create global pigpio instance
pi = pigpio.pi()
atexit.register(lambda: stop_all())

# Initialization
def init_gpio():
    # Motor pins
    for pin in [PINS.M1_IN1, PINS.M1_IN2, PINS.M1_PWM,
                PINS.M2_IN1, PINS.M2_IN2, PINS.M2_PWM, PINS.STBY]:
        pi.set_mode(pin, pigpio.OUTPUT)

    # Servo
    pi.set_mode(PINS.SERVO_PIN, pigpio.OUTPUT)

    # LEDs
    pi.set_mode(PINS.LED_RIGHT, pigpio.OUTPUT)
    pi.set_mode(PINS.LED_LEFT, pigpio.OUTPUT)

    # Battery pins (optional input mode if needed)
    for pin in [PINS.BAT_100, PINS.BAT_75, PINS.BAT_50, PINS.BAT_25]:
        pi.set_mode(pin, pigpio.INPUT)

    # Motor enable
    pi.write(PINS.STBY, 1)


# Servo control (angle: 0 ~ 180)
def set_servo_angle(angle):
    pulse = 500 + (angle / 180.0) * 2000  # 500~2500us
    pi.set_servo_pulsewidth(PINS.SERVO_PIN, int(pulse))


# Motor direction + speed
def set_motor_speed(motor_id, speed, inverse=1):
    """
    Control motor direction and speed.

    :param motor_id: 1 or 2 (M1 or M2 on TB6612FNG)
    :param speed: -255 ~ +255
    """
    if motor_id == 1:
        IN1, IN2, PWM = PINS.M1_IN1, PINS.M1_IN2, PINS.M1_PWM
    elif motor_id == 2:
        IN1, IN2, PWM = PINS.M2_IN1, PINS.M2_IN2, PINS.M2_PWM
    else:
        raise ValueError("motor_id must be 1 or 2")

    if speed * inverse > 0:
        pi.write(IN1, 1)
        pi.write(IN2, 0)
    elif speed * inverse < 0:
        pi.write(IN1, 0)
        pi.write(IN2, 1)
    else:
        pi.write(IN1, 0)
        pi.write(IN2, 0)

    pi.set_PWM_dutycycle(PWM, min(abs(speed), 255))


# LED control
def set_led(left_on=False, right_on=False):
    pi.write(PINS.LED_LEFT, 1 if left_on else 0)
    pi.write(PINS.LED_RIGHT, 1 if right_on else 0)


# Clean shutdown
def stop_all():
    set_motor_speed(1, 0)
    set_motor_speed(2, 0)
    pi.set_servo_pulsewidth(PINS.SERVO_PIN, 0)
    set_led(False, False)
    pi.write(PINS.STBY, 0)