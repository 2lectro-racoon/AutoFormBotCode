# 🚀 AutoFormBotCode

AutoFormBot의 코드 파일  
2025.04.17 기준 RPI5 BOOKWORM 환경에서 정상 동작 확인  

### 다음과 같은 기능 제공

0.91" OLED에서 IP와 현재 연결된 SSID 확인 가능  
wlan0 상황에 따라 AP/STA 모드 자동 전환  
사전 지정된 GPIO 핀맵  
스크립트를 통한 자동 설치

---

### 주의사항

네트워크 국가는 KR, wpa_supplicant을 통한 네트워크 관리가 아닌 NetworkManger를 통한 네트워크 관리

---

## 폴더 구성

| 폴더명 | 설명 |
|--------|------|
| `install/` | install 스크립트 위치 |
| `scripts/` | 각 기능별 설치 스크립트 및 기능 스크립트 모음|

---

## How To Install

### 0. Install Raspberrypi OS (BookWorm 64bit)

### 1. git clone && Run the install.sh

### 2. Check AP & oled

---

## 라이선스

이 프로젝트는 비상업적인 목적에 한하여 자유롭게 사용, 수정, 배포하실 수 있습니다.  
반드시 출처를 명시해야 하며, 상업적 이용은 금지되어 있습니다.  
자세한 내용은 [LICENSE.txt](LICENSE.txt)를 참조하세요.

© 2025 Neogul (https://github.com/2lectro-racoon)  
© 2025 Echoglow