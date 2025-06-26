import afb
import time

afb.gpio.init()

try:
    while True:
        print("앞으로 전진")
        afb.gpio.motor(70)   # 왼쪽 모터
        time.sleep(2)

        print("정지")
        afb.gpio.motor(0)
        time.sleep(1)

        print("뒤로 후진")
        afb.gpio.motor(-70)
        time.sleep(2)

        print("정지")
        afb.gpio.motor(0)
        time.sleep(1)

except KeyboardInterrupt:
    print("사용자 종료")

finally:
    afb.gpio.stop_all()
