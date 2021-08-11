import cv2 as cv
import numpy as np
from numpy.lib.type_check import imag

class Cache:
    def __init__(self):
        self.left_points = list()
        self.right_points = list()

    def store_in_cache(self, points, lane:str):
        if lane == 'left':
            self.left_points = list()
            self.left_points.append(points)
        elif lane == 'right':
            self.right_points = list()
            self.right_points.append(points)

    def get_from_cache(self, lane:str):
        if lane == 'left':
            ret = np.array(self.left_points)
            return ret
        elif lane == 'right':
            ret = np.array(self.right_points)
            return ret
        
