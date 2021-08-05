from os import error
import cv2 as cv
import numpy as np
from filters import HSVFilter, LABFilter
from utils import Cache, draw_line

hsv_filter = HSVFilter([25, 45, 0, 255, 175, 255])
lab_filter = LABFilter([0, 255, 0, 255, 150, 255])
cache = Cache()

class LaneDetector:

    count_both_sides, count_one_side, no_line = 0, 0, 0

    def __init__(self):
        self.roi_vertices = np.array([[0, 480], [0, 280], [160, 200], [480, 200], [640, 280], [640, 480]], np.int32)
        self.ref_vertices = np.array([[120, 440], [240, 300], [400, 300], [520, 440]], np.int32)
        self.roi_vertices.reshape((-1,1,2))
        self.ref_vertices.reshape((-1,1,2))
        self.pers1 = np.float32([[160, 200], [480, 200], [40, 360], [600, 360]])
        self.pers2 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
        self.pers_matrix = cv.getPerspectiveTransform(self.pers1, self.pers2)

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
        frame_lab = lab_filter.apply_filter(original_frame)
        frame_hsv = hsv_filter.apply_filter(original_frame)

        processed_frame = ((frame_lab // 2) + (frame_hsv * 2)) // 2
        processed_frame = cv.cvtColor(processed_frame, cv.COLOR_BGR2GRAY)

        ret, processed_frame = cv.threshold(processed_frame, 75, 255, cv.THRESH_BINARY)

        processed_frame = self.cleaner(processed_frame, [self.roi_vertices], [self.ref_vertices])
        processed_frame = self.morphological(processed_frame)

        warped = cv.warpPerspective(processed_frame, self.pers_matrix, (640, 480))
        lines = self.get_hough_lines(warped)
        print(lines)
        lines_on_warped = draw_line(warped, lines)

        # sorted_lines = np.sort(lines, axis=0)
        # processed_frame = cv.polylines(processed_frame, [self.pers1], True, (255), 2)
        # lanes = self.validate_lines(lines)
        # processed_frame = self.color_it(original_frame, lanes)
        return lines_on_warped
        # return processed_frame
    
    def get_hough_lines(self, processed_image):
        '''
        Draws the lines from processed image as detected by 
        hough-lines algorithm onto the original image
        parameters:
            processed_image (np.ndarray): Thresholded grayscale image containing lanes
            original_image (np.ndarray): Original color frame from the game/video
        Returns:
            lines (np.ndarray): points returned in x1, y1, x2, y2 format
        '''
        lines = cv.HoughLinesP(np.uint8(processed_image), 1, np.pi/180, 25, minLineLength=25, maxLineGap=100)
        lines_and_angles = []
        if lines is not None:
            for line in lines:
                coords = line[0]
                x1, y1, x2, y2 = coords
                angle = int(np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi)

                if 15 < abs(angle) < 60:
                    lines_and_angles.append([x1, y1, x2, y2, angle])

        return np.array(lines_and_angles)

    def validate_lines(self, lines):
        final_lines = []
        if len(lines) < 2:
            final_lanes = cache.get_from_cache()
            return np.array(final_lanes, dtype=np.int32)

        if len(lines) >= 2:
            angle_med = np.median(lines, axis=0)[4]

            left_mask = np.where(lines[:, 4] <= angle_med)
            right_mask = np.where(lines[:, 4] >= angle_med)

            left_lines = lines[left_mask]
            right_lines = lines[right_mask]

            left_y1_med, left_y2_med = np.median(left_lines, axis=0)[[1, 3]]
            right_y1_med, right_y2_med = np.median(right_lines, axis=0)[[1, 3]]
            
            if left_y1_med < left_y2_med:
                final_left_y1 = min(left_lines[:, 1])
                final_left_y2 = max(left_lines[:, 3])
                final_left_x1 = left_lines[np.where(left_lines[:, 1] == final_left_y1)[0]][:, 0][0]
                final_left_x2 = left_lines[np.where(left_lines[:, 3] == final_left_y2)[0]][:, 2][0]
                final_lines.append([final_left_x1, final_left_y1, final_left_x2, final_left_y2])

            else:
                final_left_y1 = max(left_lines[:, 1])
                final_left_y2 = min(left_lines[:, 3])
                final_left_x1 = left_lines[np.where(left_lines[:, 1] == final_left_y1)[0]][:, 0][0]
                final_left_x2 = left_lines[np.where(left_lines[:, 3] == final_left_y2)[0]][:, 2][0]
                final_lines.append([final_left_x1, final_left_y1, final_left_x2, final_left_y2])

            if right_y1_med < right_y2_med:
                final_right_y1 = min(right_lines[:, 1])
                final_right_y2 = max(right_lines[:, 3])
                final_right_x1 = right_lines[np.where(right_lines[:, 1] == final_right_y1)[0]][:, 0][0]
                final_right_x2 = right_lines[np.where(right_lines[:, 3] == final_right_y2)[0]][:, 2][0]
                final_lines.append([final_right_x1, final_right_y1, final_right_x2, final_right_y2])

            else:
                final_right_y1 = max(right_lines[:, 1])
                final_right_y2 = min(right_lines[:, 3])
                final_right_x1 = right_lines[np.where(right_lines[:, 1] == final_right_y1)[0]][:, 0][0]
                final_right_x2 = right_lines[np.where(right_lines[:, 3] == final_right_y2)[0]][:, 2][0]
                final_lines.append([final_right_x1, final_right_y1, final_right_x2, final_right_y2])
        
            cache.store_in_cache(final_lines)
            return np.array(final_lines, dtype=np.int32)

    @staticmethod
    def cleaner(frame, roi_points, ref_points):
        '''
        Cleans the thresholded image by applying the roi and removing the road reflections
        parameters:
            roi_points (np.ndarray): Polygon defining the ROI
            ref_points (np.ndarray): Polygon defining the area with car reflections
        Returns:
            masked (np.ndarray): The array returned without reflections and defined ROI.
        '''
        mask_roi = np.zeros_like(frame)
        # mask_ref = np.ones_like(frame)

        mask_roi = cv.fillPoly(mask_roi, roi_points, 1)
        # mask_ref = cv.fillPoly(mask_ref, ref_points, 0)

        masked_roi = cv.bitwise_and(frame, mask_roi)
        # masked_ref = cv.bitwise_and(frame, mask_ref)
        # masked = cv.bitwise_and(masked_roi, masked_ref)
        masked = np.array(masked_roi, dtype=np.float32)
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

# todo Define a smaller and more accurate ROI, and use it for perspective transform.
# todo Color the box made by the points from the previous step.