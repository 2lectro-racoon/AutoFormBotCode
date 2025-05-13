# gpio_control.py

import lgpio
import atexit
from gpio_pins import PINS
# Create global lgpio instance
pi = lgpio.gpiochip_open(0)
atexit.register(lambda: stop_all())

# Initialization
def init_gpio():
    # Motor pins
    for pin in [PINS.M1_IN1, PINS.M1_IN2, PINS.M1_PWM,
                PINS.M2_IN1, PINS.M2_IN2, PINS.M2_PWM, PINS.STBY]:
        lgpio.gpio_claim_output(pi, pin, 0)

    # Servo
    lgpio.gpio_claim_output(pi, PINS.SERVO_PIN, 0)

    # LEDs
    lgpio.gpio_claim_output(pi, PINS.LED_RIGHT, 0)
    lgpio.gpio_claim_output(pi, PINS.LED_LEFT, 0)

    # Battery pins (optional input mode if needed)
    # for pin in [PINS.BAT_100, PINS.BAT_75, PINS.BAT_50, PINS.BAT_25]:
    for pin in [PINS.BAT_100, PINS.BAT_50, PINS.BAT_10]:
        lgpio.gpio_claim_input(pi, pin)

    # Motor enable
    lgpio.gpio_write(pi, PINS.STBY, 1)


# Servo control (angle: 0 ~ 180)
def set_servo_angle(angle):
    pulse = 500 + (angle / 180.0) * 2000  # 500~2500us
    duty = pulse / 20000 * 100.0
    lgpio.tx_pwm(pi, PINS.SERVO_PIN, 50, duty)


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
        lgpio.gpio_write(pi, IN1, 1)
        lgpio.gpio_write(pi, IN2, 0)
    elif speed * inverse < 0:
        lgpio.gpio_write(pi, IN1, 0)
        lgpio.gpio_write(pi, IN2, 1)
    else:
        lgpio.gpio_write(pi, IN1, 0)
        lgpio.gpio_write(pi, IN2, 0)

    duty = min(abs(speed), 255) / 255 * 100.0
    lgpio.tx_pwm(pi, PWM, 1000, duty)


# LED control
def set_led(left_on=False, right_on=False):
    lgpio.gpio_write(pi, PINS.LED_LEFT, 1 if left_on else 0)
    lgpio.gpio_write(pi, PINS.LED_RIGHT, 1 if right_on else 0)


# Clean shutdown
def stop_all():
    set_motor_speed(1, 0)
    set_motor_speed(2, 0)
    lgpio.tx_pwm(pi, PINS.SERVO_PIN, 50, 0)
    set_led(False, False)
    lgpio.gpio_write(pi, PINS.STBY, 0)

# Battery level reading
def get_battery_level():
    """
    Read battery status from input GPIOs and return battery level (0–100).
    Priority: BAT_100 > BAT_50 > BAT_10
    """
    if lgpio.gpio_read(pi, PINS.BAT_100):
        return 100
    elif lgpio.gpio_read(pi, PINS.BAT_50):
        return 50
    elif lgpio.gpio_read(pi, PINS.BAT_10):
        return 10
    else:
        return 0