import os
import cv2 as cv
import numpy as np
from hsv_filter import HSVFilter

hsv_filter = HSVFilter(0,0,200,30,255,255)


def preprocess(original_image):
    processed_image = cv.GaussianBlur(original_image, (7,7), 0)
    processed_image = cv.Canny(processed_image, 100, 200)
    return processed_image

input_video_path = os.path.join(os.getcwd(), 'data', 'videos', 'highway_footage_tpp.avi')
cap = cv.VideoCapture(input_video_path)

while True:
    ret, frame = cap.read()

    hsv_frame = hsv_filter.apply_filter(frame)
    hsv_edge_frame = preprocess(hsv_frame)

    cv.imshow('with preprocessing', hsv_edge_frame)
    # cv.imshow('without preprocessing', hsv_frame)
    if cv.waitKey(10) == ord('q'):
        break
    
cap.release()
