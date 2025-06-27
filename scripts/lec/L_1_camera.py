import afb
import time
import cv2 

afb.camera.init(640, 480, 30)

while True:
    frame = afb.camera.get_image()
    
    # BGR → RGB 변환
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # RGB로 웹 전송
    afb.flask.imshow("AFB Camera", frame_rgb, 0)