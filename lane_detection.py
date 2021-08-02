import cv2 as cv
import numpy as np
from filters import HSVFilter, LABFilter

hsv_filter = HSVFilter([25, 45, 0, 255, 175, 255])
lab_filter = LABFilter([0, 255, 0, 255, 150, 255])

class LaneDetector:

    def __init__(self):
        self.roi_vertices = np.array([[0, 480], [0, 280], [160, 200], [480, 200], [640, 280], [640, 480]], np.int32)
        self.ref_vertices = np.array([[120, 440], [240, 300], [400, 300], [520, 440]], np.int32)
        self.roi_vertices.reshape((-1,1,2))
        self.ref_vertices.reshape((-1,1,2))
        # self.pts1 = np.float32([[80, 200], [560, 200], [0, 480], [640, 480]])
        # self.pts2 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
        # self.matrix = cv.getPerspectiveTransform(self.pts1, self.pts2)

    def get_hough_lines(self, image):
        lines = cv.HoughLinesP(np.uint8(image), 1, np.pi/180, 50, minLineLength=75, maxLineGap=100)
        return lines
        # if lines is not None:
        #     for line in lines:
        #         coords = line[0]
        #         x1, y1, x2, y2 = coords
        #         pt1, pt2 = (x1, y1), (x2, y2)
        #         cv.line(image, pt1, pt2, (255,255,255), 3, cv.LINE_4)

    def get_lanes(self, original_frame):
        # cv.imshow('Test', original_frame)
        frame_lab = lab_filter.apply_filter(original_frame)
        frame_hsv = hsv_filter.apply_filter(original_frame)

        processsed_frame = ((frame_lab // 2) + (frame_hsv * 2)) // 2
        processsed_frame = cv.cvtColor(processsed_frame, cv.COLOR_BGR2GRAY)

        ret, processsed_frame = cv.threshold(processsed_frame, 75, 255, cv.THRESH_BINARY)

        processsed_frame = self.cleaner(processsed_frame, [self.roi_vertices], [self.ref_vertices])
        processsed_frame = self.morphological(processsed_frame)

        lines = self.get_hough_lines(processsed_frame)
        if lines is not None:
            for line in lines:
                coords = line[0]
                x1, y1, x2, y2 = coords
                pt1, pt2 = (x1, y1), (x2, y2)
                angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
                if 30 < abs(angle) < 60:
                    cv.line(original_frame, pt1, pt2, (0,255,0), 3, cv.LINE_4)

        return original_frame


    @staticmethod
    def cleaner(frame, roi_points, ref_points, draw_lines=False):
        '''
        Cleans the thresholded image by applying the roi and removing the road reflections
        '''
        mask_roi = np.zeros_like(frame)
        mask_ref = np.ones_like(frame)

        if draw_lines:
            cv.polylines(frame, roi_points, True, (255), thickness=2)

        mask_roi = cv.fillPoly(mask_roi, roi_points, 1)
        mask_ref = cv.fillPoly(mask_ref, ref_points, 0)

        masked_roi = cv.bitwise_and(frame, mask_roi)
        masked_ref = cv.bitwise_and(frame, mask_ref)
        masked = cv.bitwise_and(masked_roi, masked_ref)
        masked = np.array(masked, dtype=np.float32)

        return masked

    @staticmethod
    def morphological(frame):
        frame = cv.dilate(frame, (3,3))
        return frame
