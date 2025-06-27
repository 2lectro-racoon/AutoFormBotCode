import afb

afb.gpio.init()

print("모터 제어 시작!")
print(" w : 앞으로 이동")
print(" s : 뒤로 이동")
print(" a : 정지")
print(" q : 종료")

try:
    while True:
        cmd = input("👉 명령 입력 (w/s/a/q): ").strip().lower()

        if cmd == "w":
            print("앞으로 이동")
            # 여기에 코드 작성
        elif cmd == "s":
            print("뒤로 이동")
            # 여기에 코드 작성
        elif cmd == "a":
            print("정지")
            # 여기에 코드 작성
        elif cmd == "q":
            print("종료합니다.")
            break

        else:
            print("⚠️ 잘못된 입력입니다. 다시 입력하세요.")

except KeyboardInterrupt:
    print("\n강제 종료")

finally:
    # 여기에 코드 작성