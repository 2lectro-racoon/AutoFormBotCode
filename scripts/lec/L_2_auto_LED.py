import afb
import time

afb.gpio.init()  # GPIO 초기화

try:
    while True:
        print("왼쪽 전조등 ON")
        afb.gpio.led(True, False)
        time.sleep(1)

        print("오른쪽 전조등 ON")
        afb.gpio.led(False, True)
        time.sleep(1)

        print("전조등 OFF")
        afb.gpio.led(False, False)
        time.sleep(1)

except KeyboardInterrupt:
    print("사용자 종료")

finally:
    afb.gpio.stop_all()  # 전체 해제