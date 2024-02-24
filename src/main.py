import cv2
import numpy as np
from helpers import h

left = cv2.VideoCapture(2)
right = cv2.VideoCapture(4)
if (not left.isOpened()) or (not right.isOpened()):
    print("Cannot open camera")
    exit()

h.setCapRes640x480(left)
h.setCapRes640x480(right)

def nothing(_=None):
    pass

cv2.namedWindow("control_panel")

while True:
    # Capture frame-by-frame
    ret1, frameLeft = left.read()
    ret2, frameRight = right.read()
    # if frame is read correctly ret is True
    if not (ret1 and ret2):
        print("Can't receive frame (stream end?). Exiting ...")
        continue

    cv2.imshow('left', frameLeft)
    cv2.imshow('right', frameRight)
    if cv2.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
left.release()
right.release()

