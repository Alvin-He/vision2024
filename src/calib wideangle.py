import cv2
import numpy

import const
import helpers


leftImages = []
rightImages = []

loadPath = '/home/administrator/Desktop/vision/src/CalibImages/'
for i in range(13):
    leftImages.append(cv2.imread(loadPath + 'left/' + str(i) + '.png', cv2.IMREAD_ANYCOLOR))
    rightImages.append(cv2.imread(loadPath + 'right/' + str(i) + '.png', cv2.IMREAD_ANYCOLOR))

