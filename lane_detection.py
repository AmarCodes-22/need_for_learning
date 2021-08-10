from os import error
import cv2 as cv
import numpy as np
from numpy.core.defchararray import count
import seaborn as sns
import matplotlib.pyplot as plt
from filters import HSVFilter, LABFilter
from utils import Cache, draw_line

hsv_filter = HSVFilter([25, 45, 0, 255, 175, 255])
lab_filter = LABFilter([0, 255, 0, 255, 150, 255])
cache = Cache()

class LaneDetector:

    count_both_sides, count_one_side, no_line = 0, 0, 0

    def __init__(self):
        self.roi = np.float32([[220, 240], [420, 240], [600, 360], [40, 360]])
        self.ref_vertices = np.array([[120, 480], [240, 300], [400, 300], [520, 480]], np.int32)
        self.ref_vertices.reshape((-1,1,2))
        self.pers1 = np.float32([[220, 240], [420, 240], [40, 360], [600, 360]])
        self.pers2 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
        self.pers_matrix = cv.getPerspectiveTransform(self.pers1, self.pers2)
        self.rows = np.arange(1, 481)

    def get_lanes(self, original_frame):
        '''
        Main function of the class, returns the original frame with lanes detected.
        Converts the original frame into seperate parts for filtering
        Processes the image
        Draws lines on the original image
        Parameters:
            original_frame (np.ndarray): The original color frame from the game/video
        Returns:
            original_frame (np.ndarray): The original frame is returned but now with lanes detected
        '''
        warped = cv.warpPerspective(original_frame, self.pers_matrix, (640, 480))

        frame_lab = lab_filter.apply_filter(warped)
        frame_hsv = hsv_filter.apply_filter(warped)
        frame_lab_b = frame_lab[:, :, 2]/255.
        frame_hsv_h = frame_hsv[:, :, 0]/255.
        frame_hsv_v = frame_hsv[:, :, 2]/255.

        filtered_frame = (frame_lab_b + frame_hsv_h + frame_hsv_v) / 3
        ret, filtered_frame = cv.threshold(filtered_frame, 75/255, 255/255, cv.THRESH_BINARY)

        filtered_frame = self.cleaner(filtered_frame, [self.ref_vertices])

        weights = np.square(filtered_frame * self.rows[:, np.newaxis])
        weighted_counts = np.sum(weights, axis=0)

        left_x_base = np.array([np.argmax(weighted_counts[:320]), 456])
        right_x_base = np.array([np.argmax(weighted_counts[320:]) + 320, 456])

        filtered_frame = self.find_lanes(filtered_frame, left_x_base, right_x_base)

        return filtered_frame

    def find_lanes(self, frame, left_base, right_base):
        """Finds a polynomial fit to the lanes in the frame

        Args:
            frame (np.ndarray): The thresholded image with the lanes detected
            left_base (nd.ndarray): the base of the left lane
            right_base (np.ndarray): the base of the right lane

        Returns:
            frame (np.ndarray): The binary frame with the polyfit for the lanes
        """
        left_lane_xs, right_lane_xs, left_lane_ys, right_lane_ys = list(), list(), list(), list()
        shift_corr_left_lane, shift_corr_right_lane = left_base[0]-32, right_base[0]-32
        cache_left_diff, cache_right_diff = 0, 0
        for i in range(10):
            frame = cv.rectangle(frame, 
                                (left_base[0]-32, left_base[1]-24), 
                                (left_base[0]+32, left_base[1]+24), 
                                (255), 
                                2, 
                                cv.LINE_4)
            frame = cv.rectangle(frame, 
                                (right_base[0]-32, right_base[1]-24), 
                                (right_base[0]+32, right_base[1]+24), 
                                (255), 
                                2, 
                                cv.LINE_4)
            # frame = cv.circle(frame, left_base, 10, (255), 2)
            # frame = cv.circle(frame, right_base, 10, (255), 2)


            #* Getting the little boxes
            little_left_box = frame[left_base[1]-24:left_base[1]+24,
                                    left_base[0]-32:left_base[0]+32] 
            little_right_box = frame[right_base[1]-24:right_base[1]+24,
                                     right_base[0]-32:right_base[0]+32]

            #* Getting the lane pixel coordinates
            left_lane_y, left_lane_x = np.where(little_left_box == 1)
            right_lane_y, right_lane_x = np.where(little_right_box == 1)

            #* Shifting the points
            left_lane_x += shift_corr_left_lane
            right_lane_x += shift_corr_right_lane
            left_lane_y += i * 48
            right_lane_y += i * 48

            #* Adding the pixels from the current box to the list of the whole lane
            left_lane_xs += list(left_lane_x)
            right_lane_xs += list(right_lane_x)
            left_lane_ys += list(left_lane_y)
            right_lane_ys += list(right_lane_y)
            
            # if len(left_lane_xs) > 0: 
                # print(max(left_lane_xs), max(right_lane_xs), max(left_lane_ys), max(right_lane_ys))
                # print(max(left_lane_xs))

            #* Left lane detection
            if len(left_lane_x) > 0:
                #* average correction
                weight = len(left_lane_x)/300
                little_left_box_x_avg = int(np.mean(left_lane_x))
                left_diff = int(little_left_box_x_avg - left_base[0])
                # print('base', left_base[0], 'average', little_left_box_x_avg, 'diff', left_diff,  'weight', int(weight), 'shift', shift_corr_left_lane)

                #* base shifting
                if left_diff < 0:
                    left_base = left_base + [int(left_diff * weight), -48]
                    shift_corr_left_lane += int(left_diff * weight)
                    cache_left_diff = left_diff
                elif left_diff >= 0: 
                    left_base = left_base + [left_diff, -48]
                    shift_corr_left_lane += left_diff
                    cache_left_diff = left_diff
            else:
                little_left_box_x_avg = None
                # print('base', left_base[0], 'average', little_left_box_x_avg, 'diff', cache_left_diff, 'weight', int(weight), 'shift', shift_corr_left_lane)
                left_base = left_base + [cache_left_diff, -48]
                shift_corr_left_lane += cache_left_diff
            

            #* Right lane detection
            if len(right_lane_x) > 0:
                #* average correction
                weight = len(right_lane_x)/300
                little_right_box_x_avg = int(np.mean(right_lane_x))
                right_diff = int(little_right_box_x_avg - right_base[0])
                
                #* base shifting
                if right_diff < 0:
                    right_base = right_base + [right_diff, -48]
                    shift_corr_right_lane += right_diff
                    cache_right_diff = right_diff
                elif right_diff >= 0: 
                    right_base = right_base + [int(right_diff * weight), -48]
                    shift_corr_right_lane += int(right_diff * weight)
                    cache_right_diff = right_diff
            else:
                little_right_box_x_avg = None
                right_base = right_base + [cache_right_diff, -48]
                shift_corr_right_lane += cache_right_diff

        return frame 

    @staticmethod
    def cleaner(frame, ref_points):
        '''
        Cleans the thresholded image by applying the roi and removing the road reflections
        parameters:
            roi_points (np.ndarray): Polygon defining the ROI
            ref_points (np.ndarray): Polygon defining the area with car reflections
        Returns:
            masked (np.ndarray): The array returned without reflections and defined ROI.
        '''
        # mask_roi = np.zeros_like(frame)
        mask_ref = np.ones_like(frame)

        # mask_roi = cv.fillPoly(mask_roi, roi_points, 1)
        mask_ref = cv.fillPoly(mask_ref, ref_points, 0)

        # masked_roi = cv.bitwise_and(frame, mask_roi)
        masked_ref = cv.bitwise_and(frame, mask_ref)
        # masked = cv.bitwise_and(masked_roi, masked_ref)
        masked = np.array(masked_ref, dtype=np.float32)
        return masked

    @staticmethod
    def morphological(frame:np.ndarray):
        '''
        Dilates the points to make them clearer to see.
        Parameters:
            frame (np.ndarray): Thresholded black and white frame.
        '''
        frame = cv.erode(frame, (5,5))
        frame = cv.dilate(frame, (5,5))
        return frame

    @staticmethod
    def color_it(original_frame, lanes):
        lanes = lanes.reshape((-1, 1, 2))[:,0,:]
        colored = cv.fillPoly(original_frame, [lanes], color=(0, 255, 0))
        return colored
