import afb
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import time
import os

# 모델 로드
model = load_model('cnn_goleftright_model.h5')
class_names = ['go', 'left', 'right']

# 시스템 초기화
afb.camera.init(640, 480, 15)
afb.gpio.init()

# 저장용 설정 (fps는 일단 5.0으로 초기화, 실제는 추론 기준)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('original_output.mp4', fourcc, 5.0, (640, 480))

prev_class = None
i = 0
prev_time = time.time()

try:
    while True:
        # 현재 시간 기록
        curr_time = time.time()
        elapsed = curr_time - prev_time
        prev_time = curr_time

        # 전진 모터 구동
        afb.gpio.motor(60)

        # 프레임 캡처
        frame = afb.camera.get_image()
        
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)  # 영상 저장

        # ROI 설정 (하단 절반)
        height = frame_bgr.shape[0]
        roi = frame_bgr[int(height * 0.5):, :]

        # CNN 입력 전처리
        input_img = cv2.resize(roi, (64, 64))
        input_img = input_img.astype(np.float32) / 255.0
        input_img = np.expand_dims(input_img, axis=0)

        # CNN 예측
        prediction = model.predict(input_img, verbose=0)
        pred_class = class_names[np.argmax(prediction)]
        confidence = np.max(prediction)

        # 서보 조향 (이전 결과와 다를 때만)
        if pred_class != prev_class:
            if pred_class == 'left':
                afb.gpio.servo(30)
            elif pred_class == 'right':
                afb.gpio.servo(150)
            elif pred_class == 'go':
                afb.gpio.servo(80)
            prev_class = pred_class

        # 디버깅 정보
        label = f"{pred_class.upper()} ({confidence:.2f})"
        cv2.putText(frame_bgr, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.rectangle(frame_bgr, (0, int(height * 0.5)), (640, 480), (255, 0, 0), 2)

        # 실시간 웹 스트리밍
        afb.flask.imshow("AFB Camera", frame_bgr, 0)

        # 프레임 처리 속도 측정 로그
        est_fps = 1 / elapsed if elapsed > 0 else 0
        print(f"[{i}] {pred_class} ({confidence:.2f}) | {elapsed:.2f}s per frame ≈ {est_fps:.2f} FPS")
        i += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    afb.gpio.stop_all()
    afb.camera.release_camera()
    out.release()
    cv2.destroyAllWindows()
