import os
import cv2 as cv
import numpy as np
from screen_capture import ScreenCapture

project_dir_path = os.getcwd()
highway_video_path = os.path.join(project_dir_path, 'data', 'videos', 'highway_footage.avi')

game_screen = ScreenCapture()
screen_dim = game_screen.window_dim
print(screen_dim)

out = cv.VideoWriter(highway_video_path, 
                     cv.VideoWriter_fourcc('M','J','P','G'), 
                     60, 
                     (screen_dim[2], screen_dim[3]))

count = 0
while True:
    screenshot = game_screen.get_screenshot()
    out.write(screenshot)
    # cv.imshow('Test', screenshot)

    if count % 50 == 0:
        print('Recording')
        count = 0
    count += 1

    if cv.waitKey(1) == ord('q'):
        break


out.release()
