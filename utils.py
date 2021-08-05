import cv2 as cv
import numpy as np
from numpy.lib.type_check import imag

class Cache:
    def __init__(self):
        self.past = list()
        pass

    def store_in_cache(self, lines):
        self.past.append(lines)
        if len(self.past) == 6:
            self.past.pop(0)

    def get_from_cache(self):
        lanes = np.array(self.past)
        # print(np.array(np.median(lanes, axis=0), dtype=np.uint8))
        return np.array(np.median(lanes, axis=0), dtype=np.uint8)


def draw_line(image, lines):
    for line in lines:
        image = cv.line(image, line[0:2], line[2:4], (255), thickness=3)
    return image