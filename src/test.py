

import const
import cam_calib_20240202_23_43_19 as calib
import cv2
from helpers import h

left = cv2.VideoCapture(2)
right = cv2.VideoCapture(4)
if (not left.isOpened()) or (not right.isOpened()):
    print("Cannot open camera")
    exit()

h.setCapRes640x480(left)
h.setCapRes640x480(right)

while True:
    _, imgL = left.read()
    _, imgR = right.read()
    cv2.imshow("Left image before rectification", imgL)
    cv2.imshow("Right image before rectification", imgR)
    
    Left_nice= cv2.remap(imgL,calib.data['stereo_maps']['left']['x'], calib.data['stereo_maps']['left']['y'], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
    Right_nice= cv2.remap(imgR,calib.data['stereo_maps']['right']['x'], calib.data['stereo_maps']['right']['y'],cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
    
    cv2.imshow("Left image after rectification", Left_nice)
    cv2.imshow("Right image after rectification", Right_nice)
    cv2.waitKey(30)