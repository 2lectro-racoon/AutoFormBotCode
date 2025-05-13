# AutoFormBot afp package

## ✨ Overview

AuotFormBot에 구동에 필요한 커스텀 패키지

---

## 폴더 구성

| 폴더명 | 설명 |
|--------|---------|
| `/afb/_gpio_pins.py` | 사전 정의 된 gpio pins |
| `/afb/camera.py` | 카메라 관련 |
| `/afb/gpio.py` | gpio 제어  |

---

## How To Use

### 0. Activate AutoFormBot_venv

파이썬 가상환경 활성화  

```bash
source AutoFormBot_venv/bin/activate
```
파이썬 파일에서 패키지 임포트  

```python
import afb
```

### 1. Camera

카메라 초기설정  

```python
afb.camera.init(width, height, framerate) # 기본값 640, 480, 30
```

카메라 프레임 불러오기  

```python
frame = afb.camera.get_image()
```

카메라 해제  

```python
afb.camera.release_camera()
```

### 2. Gpio

gpio 초기설정  

```python
afb.gpio.init()
```

조향 제어

```python
afb.gpio.servo(angle) # 기본값 90(중심) 30~150 권장
```

구동모터 제어

```python
afb.gpio.motor(speed, motor_id, inverse) # -255~255(기본값 0), 1 or 2(기본값 1채널), 1 or -1(기본값 1, 역방향 구동시 -1)
```

전조등(LED) 제어

```python
afb.gpio.led(left, right) # True or False (기본값 False)
```

배터리 잔량 확인

```python
afb.gpio.battery() # 100, 50, 10, 0 4가지 결과 출력
```

전체 해제

```python
afb.gpio.stop_all()
```
---