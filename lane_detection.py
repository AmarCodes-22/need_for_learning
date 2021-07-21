import os
import cv2 as cv
import numpy as np

def preprocess(original_image):
    processed_image = cv.GaussianBlur(original_image, (5,5), 0)
    processed_image = cv.Canny(processed_image, 100, 200)
    return processed_image
    pass

input_video_path = os.path.join(os.getcwd(), 'data', 'videos', 'highway_footage_tpp.avi')
cap = cv.VideoCapture(input_video_path)

while True:
    ret, frame = cap.read()
    # frame = preprocess(frame)
    cv.imshow('test', frame)
    if cv.waitKey(10) == ord('q'):
        break
    
cap.release()

print(input_video_path)
# TODO: 0.requires some HSV manipulation as the image is just too bright, need to distinguish the lanes and roads more.
# TODO: 1.take an input video.
# TODO: 2.show the input video
# TODO: 3.blur and grayscale  
# TODO: 
# TODO: 
# TODO: 
# TODO: 