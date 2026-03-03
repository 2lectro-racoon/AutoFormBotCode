import afb

afb.gpio.init()

try:
    while True:
        cmd = input("전조등 제어 (q: 좌 ON, w: 우 ON, e: 양쪽 ON, r: OFF): ").strip().lower()

        if cmd == "q":
            # 여기에 코드 작성
        elif cmd == "w":
            # 여기에 코드 작성
        elif cmd == "e":
            # 여기에 코드 작성
        elif cmd == "r":
            # 여기에 코드 작성
        else:
            print("잘못된 입력입니다.")

except KeyboardInterrupt:
    print("종료")

finally:
    # 여기에 코드 작성