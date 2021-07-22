import os
import cv2 as cv
import numpy as np



#* Making a custom data structure for hsv filter state
class HSVFilter:
    def __init__(self, hmin=None, smin=None, vmin=None,
                       hmax=None, smax=None, vmax=None):
        self.hmin = hmin
        self.smin = smin
        self.vmin = vmin
        self.hmax = hmax
        self.smax = smax
        self.vmax = vmax

    def apply_filter(self, image):
        image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

        lower = np.array([self.hmin, self.smin, self.vmin])
        upper = np.array([self.hmax, self.smax, self.vmax])

        mask = cv.inRange(image_hsv, lower, upper)
        image_thresholded = cv.bitwise_and(image_hsv, image_hsv, mask=mask)
        result = cv.cvtColor(image_thresholded, cv.COLOR_HSV2BGR)

        return result

#! (0,0,200), (30,255,255)


#* CODE THAT WAS USED TO FIND THE OPTIMAL FILTER
#* Paths
# images_dir = os.path.join(os.getcwd(), 'data', 'images')
# # print(len(os.listdir(images_dir)))

# #* Windows
# original_window_name = 'Original'
# thresholded_window_name = 'Thresholded'
# trackbar_window = 'Trackbars'

# cv.namedWindow(thresholded_window_name)
# cv.namedWindow(trackbar_window)
# cv.resizeWindow(trackbar_window, 350, 700)

# #* Creating the trackbars
# def nothing(position):
#     pass

# cv.createTrackbar('Hmin', trackbar_window , 0, 179, nothing)
# cv.createTrackbar('Hmax', trackbar_window , 0, 179, nothing)
# cv.createTrackbar('Smin', trackbar_window , 0, 255, nothing)
# cv.createTrackbar('Smax', trackbar_window , 0, 255, nothing)
# cv.createTrackbar('Vmin', trackbar_window , 0, 255, nothing)
# cv.createTrackbar('Vmax', trackbar_window , 0, 255, nothing)

# #* Testing
# while True:
#     for file_name in os.listdir(images_dir):

#         #* Initializing the hsv filter state
#         hsv_filter = HSVFilter()
#         hsv_filter.hmin = cv.getTrackbarPos('Hmin', trackbar_window)
#         hsv_filter.smin = cv.getTrackbarPos('Smin', trackbar_window)
#         hsv_filter.vmin = cv.getTrackbarPos('Vmin', trackbar_window)
#         hsv_filter.hmax = cv.getTrackbarPos('Hmax', trackbar_window)
#         hsv_filter.smax = cv.getTrackbarPos('Smax', trackbar_window)
#         hsv_filter.vmax = cv.getTrackbarPos('Vmax', trackbar_window)

#         file_path = os.path.join(images_dir, file_name)

#         image = cv.imread(file_path)
#         image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

#         lower = np.array([hsv_filter.hmin, hsv_filter.smin, hsv_filter.vmin])
#         upper = np.array([hsv_filter.hmax, hsv_filter.smax, hsv_filter.vmax])

#         mask = cv.inRange(image_hsv, lower, upper)
#         image_thresholded = cv.bitwise_and(image_hsv, image_hsv, mask=mask)
#         image_thresholded = cv.cvtColor(image_thresholded, cv.COLOR_HSV2BGR)
        
#         cv.imshow(thresholded_window_name, image_thresholded)

#         if cv.waitKey(500) == ord('q'):
#             break

#     if cv.waitKey(500) == ord('q'):
#             break
