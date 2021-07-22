import os
import cv2 as cv
import numpy as np
from hsv_filter import HSVFilter

hsv_filter = HSVFilter(0,0,100,30,255,255)
# input_video_path = os.path.join(os.getcwd(), 'data', 'videos', 'highway_footage_tpp.avi')
vertices = np.array([[0,480], [0,240], [80,200], [560,200], [640,240], [640,480], [480,480], [375,275], [275,275], [160,480]])
# cap = cv.VideoCapture(input_video_path)

def roi(frame, vertices):
    b,g,r = cv.split(frame)

    mask = np.ones_like(b)
    cv.fillPoly(mask, vertices, 255)

    masked_b = cv.bitwise_and(b, mask)
    masked_g = cv.bitwise_and(g, mask)
    masked_r = cv.bitwise_and(r, mask)
    masked = cv.merge([masked_b, masked_g, masked_r])

    return masked

def preprocess(original_image):
    processed_image = cv.GaussianBlur(original_image, (7,7), 0)
    processed_image = cv.Canny(processed_image, 100, 200)
    return processed_image

def get_lanes(frame):
    frame = roi(frame, [vertices])
    frame = hsv_filter.apply_filter(frame)
    frame = preprocess(frame)
    return frame
