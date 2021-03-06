import os
import cv2 as cv
import numpy as np
from screen_capture import ScreenCapture
import uuid


project_dir_path = os.getcwd()
output_video_path = os.path.join(project_dir_path, 
                                 'data', 
                                 'videos', 
                                 'highway_footage_straight_hood.avi')
images_path = os.path.join(project_dir_path, 
                           'data', 
                           'images')

#* Video footage capture
game_screen = ScreenCapture()
screen_dim = game_screen.window_dim
print(screen_dim)

out = cv.VideoWriter(output_video_path,
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

#* Image capture for hsv thresholding using prerecorded game footage
# count = 0
# cap = cv.VideoCapture(highway_video_path)
# while True:
#     ret, frame = cap.read()

#     if count % 50 == 0:
#         cv.imshow('frame to be saved', frame)
#         file_name = os.path.join(images_path, str(uuid.uuid4())+ '.jpg')
#         cv.imwrite(file_name, frame)
#         count = 0
#     count += 1

#     if cv.waitKey(1) == ord('q'):
#         break
