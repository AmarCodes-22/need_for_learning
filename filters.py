import os
import traceback
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

project_dir = os.getcwd()
paths = {
    'project_dir': project_dir,
    'input_videos': os.path.join(project_dir, 'data', 'videos'),
    'output_videos': os.path.join(project_dir, 'data', 'outputs')
}

files = {
    'input_video': os.path.join(paths['input_videos'], 'highway_footage_high_res_hood.avi')
}

class HSVFilter:
  def __init__(self, filter_=[None]*6):
    '''
    Parameters:
      self
      filter_ (list): [hmin, hmax, smin, smax, vmin ,vmax]
    '''
    self.hmin = filter_[0]
    self.hmax = filter_[1]
    self.smin = filter_[2]
    self.smax = filter_[3]
    self.vmin = filter_[4]
    self.vmax = filter_[5]
        
  def apply_filter(self, original_image):
    '''
    Applies the hsv filter to the image and converts it back to BGR
    Parameters:
        original_image (np.ndarray): The image pixel intensity values.
    Returns:
        result (np.ndarray): The image pixel intensity values for the converted image
    '''
    image_hsv = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)
    
    lower = np.array([self.hmin, self.smin, self.vmin])
    upper = np.array([self.hmax, self.smax, self.vmax])
    
    mask = cv.inRange(image_hsv, lower, upper)
    image_threshold = cv.bitwise_and(image_hsv, image_hsv, mask=mask)
    result = cv.cvtColor(image_threshold, cv.COLOR_HSV2BGR)
    
    return result
      
  def get_new_filter(self, window_name='Trackbars'):
    '''
    Returns the new initialized state of the filter
    Parameters:
    self (HSVFilter object): The filter that takes the information from the trackbar window.
    window_name (str): Name of the trackbar window.
    Returns:
    filter_object (HSVFilter object): The filter with new initialized values
    '''
    self.hmin = cv.getTrackbarPos('Hmin', window_name)
    self.hmax = cv.getTrackbarPos('Hmax', window_name)
    self.smin = cv.getTrackbarPos('Smin', window_name)
    self.smax = cv.getTrackbarPos('Smax', window_name)
    self.vmin = cv.getTrackbarPos('Vmin', window_name)
    self.vmax = cv.getTrackbarPos('Vmax', window_name)
    
    # return self
  
  @staticmethod  
  def nothing(position):
    '''
    I do nothing.
    Parameters:
        position
    '''
    pass
  
  @staticmethod
  def create_trackbar_window(window_name='Trackbars'):
    '''
    Creates the trackbar in the window_name specified.
    Parameters:
        window_name (str): Window name for the trackbar window.
    Returns:
        None
    '''
    cv.createTrackbar('Hmin', window_name, 25, 179, HSVFilter.nothing)
    cv.createTrackbar('Hmax', window_name, 45, 179, HSVFilter.nothing)
    cv.createTrackbar('Smin', window_name, 0, 255, HSVFilter.nothing)
    cv.createTrackbar('Smax', window_name, 225, 255, HSVFilter.nothing)
    cv.createTrackbar('Vmin', window_name, 175, 255, HSVFilter.nothing)
    cv.createTrackbar('Vmax', window_name, 255, 255, HSVFilter.nothing)


class LABFilter:
    def __init__(self, filter_:list):
        """
        Initiates a LABFilter object
        Parameters:
          self
          filter_ (list): [lmin, lmax, amin, amax, bmin, bmax]
        """
        self.lmin = filter_[0]
        self.lmax = filter_[1]
        self.amin = filter_[2]
        self.amax = filter_[3]
        self.bmin = filter_[4]
        self.bmax = filter_[5]
    
    def apply_filter(self, original_frame:np.ndarray):
        """
        Converts the input image to lab and applies the filter.
        Parameters:
          self
          original_frame (np.ndarray): Pixel intensity values in BGR color space.
        Returns:
          result (np.ndarray): Pixel intensity values in BGR color space.
        """
        frame_lab = cv.cvtColor(original_frame, cv.COLOR_BGR2LAB)
        
        lower = np.array([self.lmin, self.amin, self.bmin])
        upper = np.array([self.lmax, self.amax, self.bmax])
        
        mask = cv.inRange(frame_lab, lower, upper)
        frame_thresholded = cv.bitwise_and(frame_lab, frame_lab, mask=mask)
        result = frame_thresholded
        # result = cv.cvtColor(frame_thresholded, cv.COLOR_LAB2BGR)
        
        return result
    
    def get_new_filter(self, window_name='Trackbars'):
        """
        Gets the filter value from the trackbar window and restates the LAB filter object
        Parameters:
            self (LABFilter object):
            window_name (str): Get the trackbar position from this window
        Returns:
            filter_object (LABFilter object): The new state of the filter object
        """
        self.lmin = cv.getTrackbarPos('Lmin', window_name)
        self.lmax = cv.getTrackbarPos('Lmax', window_name)
        self.amin = cv.getTrackbarPos('Amin', window_name)
        self.amax = cv.getTrackbarPos('Amax', window_name)
        self.bmin = cv.getTrackbarPos('Bmin', window_name)
        self.bmax = cv.getTrackbarPos('Bmax', window_name)
    
    @staticmethod
    def nothing(position):
        """
        I do nothing
        """
        pass
    
    @staticmethod
    def create_trackbar_window(window_name:str = 'Trackbars'):
        """
        Creates trackbar in the window name specified.
        Parameters:
          window_name (str): The name of the window to make the trackbars in
        Returns:
          None
        """
        cv.createTrackbar('Lmin', window_name, 0, 255, LABFilter.nothing)
        cv.createTrackbar('Lmax', window_name, 255, 255, LABFilter.nothing)
        cv.createTrackbar('Amin', window_name, 0, 255, LABFilter.nothing)
        cv.createTrackbar('Amax', window_name, 255, 255, LABFilter.nothing)
        cv.createTrackbar('Bmin', window_name, 0, 255, LABFilter.nothing)
        cv.createTrackbar('Bmax', window_name, 255, 255, LABFilter.nothing)