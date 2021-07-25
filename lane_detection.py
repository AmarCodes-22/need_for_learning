import cv2 as cv
import numpy as np

class LaneDetector:
    def __init__(self):
        self.vertices = np.array([[0, 480], [0, 240], [80, 200], [560, 200], [640, 240], [640, 480]])
        self.pts1 = np.float32([[80, 200], [560, 200], [0, 480], [640, 480]])
        self.pts2 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
        self.matrix = cv.getPerspectiveTransform(self.pts1, self.pts2)
        pass

    def perspective_transform(self, screenshot):
        transformed = cv.warpPerspective(screenshot, self.matrix, (640, 480))
        return transformed

    def preprocess(self, original_image):
        processed_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)

        # * Custom edge detector(simple vertical edge detector)
        kernel = np.array([[1, 0, -1],
                           [1, 0, -1],
                           [1, 0, -1]])

        processed_image = cv.filter2D(processed_image, -1, kernel)
        _, processed_image = cv.threshold(processed_image, 25, 200, cv.THRESH_BINARY)

        # processed_image = cv.Canny(processed_image, 100, 200)

        return processed_image

    def morphological(self, original_image):
        kernel = np.ones((2,2), np.uint8)
        processed_image = cv.erode(original_image, kernel, iterations=1)
        return processed_image

    def get_lanes(self, frame):
        frame = self.perspective_transform(frame)
        frame = self.preprocess(frame)
        # frame = self.morphological(frame)
        return frame
