import afb

afb.gpio.init()

print("🛞 모터 제어 시작!")
print("명령어 안내:")
print("  w : 앞으로 이동")
print("  s : 뒤로 이동")
print("  a : 정지")
print("  q : 종료")

try:
    while True:
        cmd = input("👉 명령 입력 (w/s/a/q): ").strip().lower()

        if cmd == "w":
            print("앞으로 이동")
            

        elif cmd == "s":
            print("뒤로 이동")
            

        elif cmd == "a":
            print("정지")
            

        elif cmd == "q":
            print("종료합니다.")
            break

        else:
            print("⚠️ 잘못된 입력입니다. 다시 입력하세요.")

except KeyboardInterrupt:
    print("\n사용자 강제 종료")

finally:
    afb.gpio.stop_all()
