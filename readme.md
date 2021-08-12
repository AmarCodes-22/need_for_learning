# Lanes detection
Overview:
In this project we try to find lanes in Need for speed Most Wanted 2005.  

Even though the project focuses primarily on the game, the concepts used are inspired by real world lane detection procedures.  
The complete project consists of multiple subtasks each of which is a stepping stone to the final output where the lanes are detected.  
### Subtask 1: Game screen capture  
There are multiple ways to capture a screen in a python script.  
1. I am running the project on Ubuntu 20.04, so to capture the screen i had to use a couple of linux commands (*wmctrl & xwininfo*). These commands are run from inside the screen_capture.py script using the os built-in module.  
Using this approach i was able to achieve upwards of **120 fps** (if only my screen supported that) on prerecorded videos.  

2. We can also use PIL from python, but it happens to be very slow for live capturing the screen. I was only able to achieve 10-20 fps (and that is without any calculations).  

### Subtask 2: Color space filtering  
Color spaces can be used to filter out the parts of an image with certain colors. Lane lines are usually **white** or **yellow**. To filter out these colors, i used two color spaces: HSV and LAB.  
#### HSV  
Usually images are in the **RGB** color space. OpenCV works with **BGR** that is just inverted RGB (similar enough). In **HSV** format, the images are converted to have 3 channels (H: Hue, S: Saturation, V:Value).  
![](https://github.com/AmarCodes-22/need_for_learning/blob/main/readme_stuff/HSV_color_space.png)


Subtask 3: Lane detection  