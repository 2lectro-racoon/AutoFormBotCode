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

카메라 프레임 불러오기  

```python
frame = afb.camera.get_image()
```
카메라 해제  

```python
afb.camera.release_camera()
```

---