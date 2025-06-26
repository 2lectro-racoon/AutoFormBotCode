import afb
import time

afb.gpio.init()  # GPIO 초기화

try:
    while True:
        angle = int(input("조향 각도 입력 (30~150): "))
        afb.gpio.servo(angle)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("사용자 종료")

finally:
    afb.gpio.stop_all()  # 전체 모터/LED/서보 정지

