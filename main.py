from time import time
import cv2 as cv
from screen_capture import ScreenCapture
from lane_detection import get_lanes

game_screen = ScreenCapture()
looptime = time()
count = 0

while True:
    screenshot = game_screen.get_screenshot()
    lanes = get_lanes(screenshot)
    cv.imshow('Lanes', lanes)

    if count % 25 == 0:
        print('FPS: {}'.format(1/(time()-looptime)))
        count = 0
    looptime = time()
    count += 1

    if cv.waitKey(1) == ord('q'):
        break
