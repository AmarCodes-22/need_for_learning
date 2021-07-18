import os 
from Xlib import display, X
from PIL import Image
import cv2 as cv
import re
import numpy as np

class ScreenCapture:
    '''
    Fast screen capture class.
    '''

    window_id = None
    window_dim = None
    x, y = None, None
    width, height = None, None

    def __init__(self):
        self.get_window_id()
        self.get_screen_location()
        pass

    def get_window_id(self):
        '''
        Uses wmctrl command to get the window id of the game screen
        Called when the object of ScreenCapture class is created
        '''
        window_list = os.popen('wmctrl -l').read().split('\n')
        target = None
        for window in window_list:
            if 'Wine' in window:
                target = window
                self.window_dim = []
                break

        target = target.split(' ')[0]

        self.window_id = target

    def get_screen_location(self):
        '''
        Used xwininfo to get the location of the game screen based on window id
        Called when the object of the ScreenCapture class is created
        '''
        window_info = os.popen('xwininfo -id {}'.format(self.window_id)).read()
        window_info = window_info.split('\n')
        for info in window_info:
            info = info.replace(' ', '')

            if 'Absolute' in info or 'Width' in info or 'Height' in info:
                if re.match('.*?([0-9]+)$', info) == None:
                    last_digits = None
                else:
                    last_digits = int(re.match('.*?([0-9]+)$', info).group(1))
                
                self.window_dim.append(last_digits)

    def get_screenshot(self):
        '''
        Gets a snapshot of the game screen, converts it to a numpy array and returns it.
        ''' 
        top_left_x = self.window_dim[0]
        top_left_y = self.window_dim[1]
        width = self.window_dim[2]
        height = self.window_dim[3]
        dsp = display.Display()
            
        try:
            root = dsp.screen().root
            raw = root.get_image(top_left_x, top_left_y, width, height, X.ZPixmap, 0xffffffff)
            image = Image.frombytes('RGB', (width, height), raw.data, 'raw', 'BGRX')
            image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            return image
        except:
            print('inside except')
            return None
