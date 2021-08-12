from os import error
import cv2 as cv
import numpy as np
from numpy.core.defchararray import count
import seaborn as sns
import matplotlib.pyplot as plt
from filters import HSVFilter, LABFilter
from utils import Cache

hsv_filter = HSVFilter([25, 45, 0, 255, 175, 255])
lab_filter = LABFilter([0, 255, 0, 255, 150, 255])
cache = Cache()

class LaneDetector:

    count_both_sides, count_one_side, no_line = 0, 0, 0

    def __init__(self):
        self.roi = np.array([[220, 240], [420, 240], [600, 360], [40, 360]], np.int32)
        self.ref_vertices = np.array([[120, 480], [240, 300], [400, 300], [520, 480]], np.int32)
        self.roi.reshape((-1, 1, 2))
        self.ref_vertices.reshape((-1,1,2))
        self.pers1 = np.float32([[220, 240], [420, 240], [40, 360], [600, 360]])
        self.pers2 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
        self.pers_matrix = cv.getPerspectiveTransform(self.pers1, self.pers2)
        self.rev_pers_matrix = cv.getPerspectiveTransform(self.pers2, self.pers1)
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

        left_lane_x, left_lane_y, right_lane_x, right_lane_y = self.find_lanes(filtered_frame, left_x_base, right_x_base)
        self.fit_and_draw(warped, (left_lane_x, left_lane_y, right_lane_x, right_lane_y))
        
        unwarped = cv.warpPerspective(warped, self.rev_pers_matrix, (640, 480))
        blank = np.ones(original_frame.shape, dtype=np.uint8) * 255
        blank = cv.fillPoly(blank, [self.roi], (0, 0, 0))
        # print(blank.dtype, original_frame.dtype)
        original_masked = cv.bitwise_and(original_frame, blank)
        test = cv.bitwise_or(original_masked, unwarped)
        # result = cv.addWeighted(original_masked, 1, unwarped, 0.5, 0)

        return test
    
    def fit_and_draw(self, original_frame, lanes):
        """Takes the points that are considered to be in the lane 
        and draws them on the original image

        Args:
            original_frame (np.ndarray): the pixel values for the game screenshot
            lanes (tuple): (left_x, left_y, right_x, right_y)

        Returns:
            None
        """
        left_x, left_y, right_x, right_y = lanes

        #* Drawing left lane on the processed frame
        uniques_left_x = np.unique(left_x)
        if uniques_left_x.shape[0] > 0:
            uniques_left_y_range = np.ptp(left_y)
            if 200 < uniques_left_y_range < 500:
                left_fit = np.polyfit(left_x, left_y, 2)
                left_draw_y = np.polyval(left_fit, np.array(uniques_left_x, dtype=np.float32))
                left_draw_y = 480 - left_draw_y
                left_draw_points = (np.asarray([uniques_left_x, left_draw_y]).T).astype(np.int32)
                cache.store_in_cache(left_draw_points, 'left')
                cv.polylines(original_frame, [left_draw_points], False, (255, 0, 0), thickness=15)
            else:
                left_draw_points = cache.get_from_cache('left')
                cv.polylines(original_frame, [left_draw_points], False, (255, 0, 0), thickness=15)
        else:
            left_draw_points = cache.get_from_cache('left')
            cv.polylines(original_frame, [left_draw_points], False, (255, 0, 0), thickness=15)
            
        #* Drawing right lane on the processed frame
        uniques_right_x = np.unique(right_x)
        if uniques_right_x.shape[0] > 0:
            uniques_right_y_range = np.ptp(right_y)
            if 200 < uniques_right_y_range < 500:
                right_fit = np.polyfit(right_x, right_y, 2)
                right_draw_y = np.polyval(right_fit, np.array(np.unique(right_x), dtype=np.float32))
                right_draw_y = 480 - right_draw_y
                right_draw_points = (np.asarray([np.unique(right_x), right_draw_y]).T).astype(np.int32)
                cache.store_in_cache(right_draw_points, 'right')
                cv.polylines(original_frame, [right_draw_points], False, (0, 0, 255), thickness=15)
            else:
                right_draw_points = cache.get_from_cache('right')
                cv.polylines(original_frame, [right_draw_points], False, (0, 0, 255), thickness=15)
        else:
            right_draw_points = cache.get_from_cache('right')
            cv.polylines(original_frame, [right_draw_points], False, (0, 0, 255), thickness=15)


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
        shift_corr_left_lane, shift_corr_right_lane = left_base[0]-48, right_base[0]-48
        cache_left_diff, cache_right_diff = 0, 0
        for i in range(10):
            # frame = cv.rectangle(frame, 
            #                     (left_base[0]-48, left_base[1]-24), 
            #                     (left_base[0]+48, left_base[1]+24), 
            #                     (255), 
            #                     2, 
            #                     cv.LINE_4)
            # frame = cv.rectangle(frame, 
            #                     (right_base[0]-48, right_base[1]-24), 
            #                     (right_base[0]+48, right_base[1]+24), 
            #                     (255), 
            #                     2, 
            #                     cv.LINE_4)
            # frame = cv.circle(frame, left_base, 10, (255), 2)
            # frame = cv.circle(frame, right_base, 10, (255), 2)


            #* Getting the little boxes
            little_left_box = frame[left_base[1]-24:left_base[1]+24,
                                    left_base[0]-48:left_base[0]+48] 
            little_right_box = frame[right_base[1]-24:right_base[1]+24,
                                     right_base[0]-48:right_base[0]+48]

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

        return left_lane_xs, left_lane_ys, right_lane_xs, right_lane_ys 

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
