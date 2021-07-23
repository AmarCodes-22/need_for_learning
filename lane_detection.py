import os
import cv2 as cv
import numpy as np
from numpy.lib.function_base import blackman
from hsv_filter import HSVFilter

hsv_filter = HSVFilter(0,0,100,30,255,255)

vertices = np.array([[0,480], [0,240], [80,200], [560,200], [640,240], [640,480]]) 
                    #  [480,480], [375,275], [275,275], [160,480]])

def preprocess(original_image):
    processed_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)

    #* Custom edge detector
    kernel = np.array([[1,0,-1],
                       [1,0,-1],
                       [1,0,-1]])

    processed_image = cv.filter2D(processed_image, -1, kernel)
    _, processed_image = cv.threshold(processed_image, 25, 200, cv.THRESH_BINARY)

    
    #* Dilation and erosion
    # erode_kernel = np.ones((3,3),np.uint8)
    # dilation_kernel = np.ones((3,3),np.uint8)
    # processed_image = cv.dilate(processed_image,dilation_kernel,iterations = 1)
    # processed_image = cv.erode(processed_image,erode_kernel,iterations = 1)

    # processed_image = cv.GaussianBlur(processed_image, (3,3), 0)
    # processed_image = cv.Canny(processed_image, 150, 250)

    return processed_image

def roi(frame, vertices):
    mask = np.ones_like(frame)
    cv.fillPoly(mask, vertices, 255)
    masked = cv.bitwise_and(frame, mask)
    return masked

def draw_lines(frame, lines):
    blank = np.zeros_like(frame)
    try:
        for line in lines:
            coords = line[0]
            x1, y1, x2, y2 = coords
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            # print(coords, angle, type(angle))
            if 30 < abs(angle) < 60 and max(y1, y2) > 350:
                cv.line(frame, (x1, y1), (x2, y2), (255,255,255), 4, lineType=cv.LINE_4)
            # break

        return frame
    except: 
        return frame

def hough_lines(frame):
    lines = cv.HoughLinesP(frame, 1, np.pi/180, 50, minLineLength=50,maxLineGap=10)
    # print(lines)
    frame = draw_lines(frame, lines)
    return frame

def get_edges(frame):
    frame = preprocess(frame)
    frame = roi(frame, [vertices])
    frame = hough_lines(frame)
    return frame

