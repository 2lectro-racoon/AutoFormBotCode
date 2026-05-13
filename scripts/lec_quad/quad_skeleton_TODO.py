# ------------------------------------------------------------
# 학생이 작성할 부분:
#   TODO 1: AR마커 검출
#   TODO 2: 마커 정보 계산 및 정면 마커 선택
#   TODO 3: 회전 함수 구현
#   TODO 4: OpenAI 결과 정규화
#   TODO 5: 마커 트리거 판단
#   TODO 6: ID별 미션 처리
#   TODO 7: 메인 루프
#   TODO 8: CHATGPT 프롬프트 변경하기
#   TODO 9: 필요 시 AR마커 1번을 인식하고 중복 인식이 안되도록 설정하기
# ------------------------------------------------------------

from __future__ import annotations

import base64
import os
import threading
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import afb2
import cv2
import numpy as np
from openai import OpenAI

from A_crawl_drive import CrawlDriver, Cmd


# ============================================================
# 1. 기본 설정
# ============================================================
CAM_W = 640
CAM_H = 480
CAM_FPS = 30

CENTER_X_RATIO = 0.35

#----------------- 파라미터 수정 파트 시작 -----------------#
#해당 TRIGGER_AREA 이상일 경우 인식을 하는 것
ID1_TRIGGER_AREA = #AR마커 1번의 면적을 작성하시오 (ex.2000)
ID2_TRIGGER_AREA = #AR마커 2번의 면적을 작성하시오 (ex.2000)
ID3_TRIGGER_AREA = #AR마커 3번의 면적을 작성하시오 (ex.2000)
ID4_TRIGGER_AREA = #AR마커 4번의 면적을 작성하시오 (ex.2000)

#해당 스텝만큼 회전을 진행
TURN_90_LEFT_STEPS = #스텝 숫자를 채우시오. 임의 값이 아닌 실험적으로 찾는 값 (ex. 2)
TURN_90_RIGHT_STEPS = #스텝 숫자를 채우시오. 임의 값이 아닌 실험적으로 찾는 값 (ex. 2)

TURN_45_LEFT_STEPS = #스텝 숫자를 채우시오. 임의 값이 아닌 실험적으로 찾는 값 (ex. 1)
TURN_45_RIGHT_STEPS = #스텝 숫자를 채우시오. 임의 값이 아닌 실험적으로 찾는 값 (ex. 1)
#----------------- 파라미터 수정 파트 끝 ------------------#

MARKER_COOLDOWN_SEC = 5
MARKER_PRINT_INTERVAL = 0.25

SHOW_CAMERA = True
USE_OPENAI_ANALYSIS = True
OPENAI_MODEL = "gpt-4.1-mini"



FORWARD_AFTER_TURN_STEPS = 2

STEP_INTERVAL = 0.12
TURN_STEP_INTERVAL = 0.03

CMD_FORWARD = Cmd(vx=+1, vy=0, wz=0)
CMD_TURN_LEFT = Cmd(vx=0, vy=0, wz=+1)
CMD_TURN_RIGHT = Cmd(vx=0, vy=0, wz=-1)


# ============================================================
# 2. 전역 상태
# ============================================================
driver = CrawlDriver()

latest_marker = None
latest_frame = None
latest_display_frame = None
openai_display_frame = None

camera_running = False
camera_thread = None
camera_lock = threading.Lock()

last_marker_print_t = 0.0
last_trigger_t = 0.0
last_state = None
is_stopped = False
should_exit = False
start_time = None

openai_client = None
aruco_detector = None


@dataclass
class MarkerInfo:
    marker_id: int
    cx: int
    cy: int
    area: float


# ============================================================
# 3. 카메라 / AR 마커 검출
# ============================================================
def init_camera():
    afb2.camera.init(CAM_W, CAM_H, CAM_FPS)


def create_aruco_detector():
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    return cv2.aruco.ArucoDetector(aruco_dict, parameters)


def detect_front_marker() -> Tuple[Optional[MarkerInfo], np.ndarray]:
    """
    TODO 1, 2:
    카메라에서 이미지를 가져와 ArUco 마커를 검출하고,
    화면 중앙에 가까운 마커 중 면적이 가장 큰 마커를 반환하시오.
    """
    global latest_frame, last_marker_print_t

    frame = afb2.camera.get_image()

    with camera_lock:
        latest_frame = frame.copy()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # TODO 1:
    # aruco_detector.detectMarkers(gray)를 사용해 corners, ids를 얻으시오.
    corners = None
    ids = None

    if ids is None:
        return None, frame

    image_cx = CAM_W / 2.0
    center_limit = CAM_W * CENTER_X_RATIO
    best = None

    for i in range(len(ids)):
        # TODO 2-1:
        # marker_id, pts, cx, cy, area를 계산하시오.
        marker_id = None
        pts = None
        cx = None
        cy = None
        area = None

        # 시각화 코드
        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        cv2.putText(
            frame,
            f"ID:{marker_id} A:{int(area)}",
            (cx, cy - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            2,
        )

        now = time.time()
        if now - last_marker_print_t >= MARKER_PRINT_INTERVAL:
            print(f"marker id={marker_id} area={int(area)}", flush=True)
            last_marker_print_t = now

        # TODO 2-2:
        # 화면 중앙에서 멀리 떨어진 마커는 continue로 제외하시오.
        pass

        info = MarkerInfo(marker_id=marker_id, cx=cx, cy=cy, area=area)

        # TODO 2-3:
        # best가 None이거나 info.area가 best.area보다 크면 best를 갱신하시오.
        pass

    return best, frame


def camera_loop():
    global latest_marker, latest_display_frame, openai_display_frame

    while camera_running:
        try:
            marker, frame = detect_front_marker()

            with camera_lock:
                latest_marker = marker
                latest_display_frame = frame.copy()
                openai_frame = None if openai_display_frame is None else openai_display_frame.copy()

            if SHOW_CAMERA:
                afb2.flask.imshow(
                    "Contest",
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    0,
                )

                if openai_frame is not None:
                    afb2.flask.imshow(
                        "openai",
                        cv2.cvtColor(openai_frame, cv2.COLOR_BGR2RGB),
                        1,
                    )

        except Exception as e:
            print(f"[CAMERA] 카메라 스레드 오류: {e}", flush=True)
            time.sleep(0.1)

        time.sleep(0.001)


def start_camera_thread():
    global camera_running, camera_thread

    if camera_running:
        return

    camera_running = True
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()


def stop_camera_thread():
    global camera_running, camera_thread

    camera_running = False

    if camera_thread is not None:
        camera_thread.join(timeout=1.0)
        camera_thread = None


def get_latest_marker():
    with camera_lock:
        return latest_marker


def get_raw_frame():
    with camera_lock:
        if latest_frame is None:
            return None
        return latest_frame.copy()


# ============================================================
# 4. 로봇 기본 동작
# ============================================================
def forward_step():
    global last_state

    if last_state != "go":
        print("go", flush=True)
        last_state = "go"

    driver.crawl_step(CMD_FORWARD)


def stop_in_place():
    global last_state, is_stopped

    if last_state != "stop":
        print("stop", flush=True)
        last_state = "stop"

    is_stopped = True


def turn_by_command(state_name: str, command: Cmd, step_count: int):
    """
    TODO 3:
    회전 공통 함수를 완성하시오.

    조건:
      1. last_state가 state_name과 다르면 state_name을 출력하고 갱신한다.
      2. driver.go_stand(duration=0.25)를 호출한다.
      3. step_count만큼 driver.crawl_step(command)를 반복한다.
      4. 반복마다 time.sleep(TURN_STEP_INTERVAL)을 넣는다.
      5. 마지막에 driver.go_stand(duration=0.25)를 호출한다.
    """
    global last_state

    # 여기에 작성
    pass


def turn_left_90():
    turn_by_command("left", CMD_TURN_LEFT, TURN_90_LEFT_STEPS)


def turn_right_90():
    turn_by_command("right", CMD_TURN_RIGHT, TURN_90_RIGHT_STEPS)


def turn_left_45():
    turn_by_command("left", CMD_TURN_LEFT, TURN_45_LEFT_STEPS)


def turn_right_45():
    turn_by_command("right", CMD_TURN_RIGHT, TURN_45_RIGHT_STEPS)


def forward_after_turn():
    for _ in range(FORWARD_AFTER_TURN_STEPS):
        forward_step()
        time.sleep(STEP_INTERVAL)


# ============================================================
# 5. OpenAI 방향 분석
# ============================================================
def normalize_direction(text: str) -> str:
    """
    TODO 4:
    OpenAI 응답 문자열을 LEFT, RIGHT, NONE 중 하나로 정규화하시오.
    """
    # 여기에 작성
    pass


def analyze_arrow_once() -> Optional[str]:
    global openai_display_frame

    if openai_client is None:
        return None

    frame = get_raw_frame()

    if frame is None:
        print("[OPENAI] 사용할 수 있는 카메라 프레임이 없습니다.", flush=True)
        return None

    if SHOW_CAMERA:
        with camera_lock:
            openai_display_frame = frame.copy()
        print("DEBUG_OPENAI_IMG", flush=True)

    ok, buffer = cv2.imencode(".jpg", frame)

    if not ok:
        print("[OPENAI] 카메라 프레임 JPEG 인코딩 실패", flush=True)
        return None

    img_base64 = base64.b64encode(buffer).decode("utf-8")

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                    # TODO 8:
                                    # CHATGPT 프롬프트 작성하기
                                "프롬프트 1 작성하기 "
                                "필요하면 여기에 다음줄도 작성하기"
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}",
                            },
                        },
                    ],
                }
            ],
        )

    except Exception as e:
        print(f"[OPENAI] 이미지 분석 실패: {e}", flush=True)
        return None

    result = normalize_direction(response.choices[0].message.content)
    print(f"[OPENAI] arrow={result}", flush=True)
    return result


# ============================================================
# 6. 학생 작성 구간
# ============================================================
def is_marker_triggered(marker: MarkerInfo) -> bool:
    """
    TODO 5:
    마커 ID별 거리 조건을 완성하시오.
    """
    # 여기에 작성
    pass


def handle_marker(marker: MarkerInfo):
    """
    TODO 6:
    ID별 미션 동작을 완성하시오.
    """
    global should_exit, is_stopped

    print(f"marker id={marker.marker_id} area={int(marker.area)}", flush=True)

    # 여기에 작성
    pass


def mission_loop():
    """
    TODO 7:
    미션 메인 루프를 완성하시오.
    """
    global last_trigger_t

    last_step_t = 0.0

    while not should_exit:
        marker = get_latest_marker()
        now = time.time()
        can_trigger = (now - last_trigger_t) > MARKER_COOLDOWN_SEC

        # 여기에 작성
        pass


# ============================================================
# 7. 실행부
# ============================================================
def setup_openai():
    global openai_client

    if USE_OPENAI_ANALYSIS:
        if os.getenv("OPENAI_API_KEY"):
            openai_client = OpenAI()
        else:
            print("[OPENAI] OPENAI_API_KEY 환경변수가 없어 이미지 분석을 건너뜁니다.", flush=True)


def start():
    global aruco_detector, start_time

    init_camera()
    aruco_detector = create_aruco_detector()
    setup_openai()

    start_camera_thread()

    driver.reset()
    start_time = time.time()

    print("ready", flush=True)


def stop():
    stop_camera_thread()

    if start_time is not None:
        elapsed = time.time() - start_time
        print(f"[TIME] elapsed={elapsed:.1f} sec", flush=True)

    driver.bodyup(60, 120, -10, duration=0.8)
    time.sleep(1)
    driver.shutdown()


def main():
    try:
        start()
        mission_loop()

    except KeyboardInterrupt:
        print("\n[EXIT]")

    finally:
        stop()


if __name__ == "__main__":
    main()
