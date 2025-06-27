# 라이브러리 불러오기
import afb
import time
import threading
import cv2

# 초기화
afb.camera.init(640, 480, 30)
afb.gpio.init()

# 📸 카메라 프레임 반복 출력 (웹 스트리밍 유지용)
def camera_loop():
    while True:
        # 여기에 코드 작성
        time.sleep(0.03)  # 약 30 fps

# 🎮 명령어 입력 처리 루프
def control_loop():
    print("===== AFB 자동차 제어 실습 =====")
    print("사용 가능한 명령어:")
    print(" f : 전진")
    print(" b : 후진")
    print(" s : 정지")
    print(" l : 좌회전 조향")
    print(" r : 우회전 조향")
    print(" c : 조향 중립")
    print(" q : 종료")
    print("===============================")

    while True:
        cmd = input("명령어 입력 👉 ").strip().lower()

        if cmd == "f":
            # 여기에 코드 작성
        elif cmd == "b":
            # 여기에 코드 작성
        elif cmd == "s":
            # 여기에 코드 작성
        elif cmd == "l":
            # 여기에 코드 작성
        elif cmd == "r":
            # 여기에 코드 작성
        elif cmd == "c": 
            # 여기에 코드 작성
        elif cmd == "q":
            print("프로그램을 종료합니다.")
            break
        else:
            print("❌ 올바르지 않은 명령어입니다. 다시 시도하세요.")

    afb.gpio.stop_all()

try:
    # 카메라 루프를 백그라운드로 실행
    cam_thread = threading.Thread(target=camera_loop, daemon=True)
    cam_thread.start()

    # 입력 루프 실행
    control_loop()

except KeyboardInterrupt:
    print("사용자 강제 종료")

finally:
    # 여기에 코드 작성
