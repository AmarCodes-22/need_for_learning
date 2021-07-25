import os
import time
import cv2 as cv
from screen_capture import ScreenCapture
from lane_detection import LaneDetector

# game_screen = ScreenCapture()
lane_detector = LaneDetector()

looptime = time.time()
count = 0

input_video_path = os.path.join(os.getcwd(), 'data', 'videos', 'highway_footage_tpp.avi')
# output_video_path = os.path.join(os.getcwd(), 'data', 'outputs', 'highway_footage_tpp_pers_wo_morph.avi')

cap = cv.VideoCapture(input_video_path)
# out = cv.VideoWriter(output_video_path,cv.VideoWriter_fourcc('M','J','P','G'), 10, (640,480))

while True:
    #* For live game footage
    # screenshot = game_screen.get_screenshot()
    # lanes = get_lanes(screenshot)
    # cv.imshow('Lanes', lanes)

    #* For prerecorded videos
    ret, frame = cap.read()
    lanes = lane_detector.get_lanes(frame)
    # out.write(lanes)
    cv.imshow('Lanes', lanes)

    if count % 25 == 0:
        print('FPS: {}'.format(1/(time.time()-looptime)))
        count = 0
    looptime = time.time()
    count += 1

    if cv.waitKey(1) == ord('q'):
        break

# out.release()