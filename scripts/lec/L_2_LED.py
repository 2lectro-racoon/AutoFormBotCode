import afb

afb.gpio.init()

try:
    while True:
        cmd = input("전조등 제어 (q: 좌 ON, w: 우 ON, e: 양쪽 ON, r: OFF): ").strip().lower()

        if cmd == "q":
            
        elif cmd == "w":
            
        elif cmd == "e":
            
        elif cmd == "r":
            
        else:
            print("잘못된 입력입니다.")

except KeyboardInterrupt:
    print("종료")

finally:
    afb.gpio.stop_all()
