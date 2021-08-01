import cv2 as cv
import numpy as np
from filters import HSVFilter, LABFilter

hsv_filter = HSVFilter([25, 45, 0, 255, 175, 255])
lab_filter = LABFilter([0, 255, 0, 255, 150, 255])

class LaneDetector:

    def __init__(self):
        self.roi_vertices = np.array([[0, 480], [0, 280], [160, 200], [480, 200], [640, 280], [640, 480]], np.int32)
        self.roi_vertices.reshape((-1,1,2))
        self.ref_vertices = np.array([[120, 440], [240, 300], [400, 300], [520, 440]], np.int32)
        self.ref_vertices.reshape((-1,1,2))
        self.pts1 = np.float32([[80, 200], [560, 200], [0, 480], [640, 480]])
        self.pts2 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
        self.matrix = cv.getPerspectiveTransform(self.pts1, self.pts2)

    def perspective_transform(self, screenshot):
        transformed = cv.warpPerspective(screenshot, self.matrix, (640, 480))
        return transformed

    def get_lanes(self, frame):
        frame_lab = lab_filter.apply_filter(frame)
        frame_hsv = hsv_filter.apply_filter(frame)

        frame = ((frame_lab // 2) + (frame_hsv * 2)) // 2
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        ret, frame = cv.threshold(frame, 75, 255, cv.THRESH_BINARY)
        frame = self.cleaner(frame, [self.roi_vertices], [self.ref_vertices])
        frame = self.morphological(frame)

        return frame


    @staticmethod
    def cleaner(frame, roi_points, ref_points):
        '''
        Cleans the thresholded image by applying the roi and removing the road reflections
        '''
        mask_roi = np.zeros_like(frame)
        mask_ref = np.ones_like(frame)

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
