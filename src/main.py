import cv2
import numpy as np


left = cv2.VideoCapture(2)
right = cv2.VideoCapture(4)
if (not left.isOpened()) or (not right.isOpened()):
    print("Cannot open camera")
    exit()

# Setting parameters for StereoSGBM algorithm
minDisparity = 0
numDisparities = 64
blockSize = 8
disp12MaxDiff = 1
uniquenessRatio = 10
speckleWindowSize = 10
speckleRange = 8
 
# Creating an object of StereoSGBM algorithm
stereo = cv2.StereoSGBM().create(minDisparity = minDisparity,
    numDisparities = numDisparities,
    blockSize = blockSize,
    disp12MaxDiff = disp12MaxDiff,
    uniquenessRatio = uniquenessRatio,
    speckleWindowSize = speckleWindowSize,
    speckleRange = speckleRange
)

def update_res(event, x, y, flags, param):
    if event != cv2.EVENT_RBUTTONDOWN: return
    newWidth=int(cv2.getTrackbarPos("res_X", "control_panel"))
    newHeight=int(cv2.getTrackbarPos("res_Y", "control_panel"))
    left.set(cv2.CAP_PROP_FRAME_WIDTH, newWidth)
    right.set(cv2.CAP_PROP_FRAME_WIDTH, newWidth)
    left.set(cv2.CAP_PROP_FRAME_HEIGHT, newHeight)
    right.set(cv2.CAP_PROP_FRAME_HEIGHT, newHeight)

def nothing(_=None):
    pass

cv2.namedWindow("control_panel")

cv2.createTrackbar("res_X", "control_panel", int(left.get(cv2.CAP_PROP_FRAME_WIDTH)), cv2.CAP_PROP_GIGA_FRAME_WIDTH_MAX, nothing)
cv2.createTrackbar("res_Y", "control_panel", int(left.get(cv2.CAP_PROP_FRAME_HEIGHT)), cv2.CAP_PROP_GIGA_FRAME_HEIGH_MAX, nothing)

cv2.setMouseCallback("control_panel", update_res)

while True:
    # Capture frame-by-frame
    ret1, frameLeft = left.read()
    ret2, frameRight = right.read()
    # if frame is read correctly ret is True
    if not (ret1 and ret2):
        print("Can't receive frame (stream end?). Exiting ...")
        continue
    # Our operations on the frame come here
    # grayLeft = cv2.cvtColor(frameLeft, cv2.COLOR_BGR2GRAY)
    # grayRight = cv2.cvtColor(frameRight, cv2.COLOR_BGR2GRAY)
    # Display the resulting frame
    # disp = stereo.compute(grayLeft, grayRight).astype(np.float32)
    cv2.imshow('left', frameLeft)
    cv2.imshow('right', frameRight)
    if cv2.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
left.release()
right.release()

