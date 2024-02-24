import cv2
import const as k
from helpers import h
import helpers
import os
import numpy
from pathlib import Path
import threading
import time

left = cv2.VideoCapture(2)
right = cv2.VideoCapture(4)
if (not left.isOpened()) or (not right.isOpened()):
    print("Cannot open camera")
    exit()

h.setCapRes640x480(left)
h.setCapRes640x480(right)

destParent = "./CalibImages"
leftDir = destParent + "/left"
rightDir = destParent + "/right"


leftList = []
rightList = []
_, i = left.read()
leftCur = numpy.zeros(i.shape)
rightCur = numpy.zeros(i.shape)
leftRender = numpy.zeros(i.shape)
rightRender = numpy.zeros(i.shape)
capped = False
numCapped = 0
def capture():
    global leftCur, rightCur, leftRender, rightRender
    global capped
    retl, leftImg = left.read()
    retr, rightImg = right.read()
    if (not retl) or (not retr):
        print("Failed to read image")
        return
    
    gray_fl = cv2.cvtColor(leftImg,cv2.COLOR_BGR2GRAY)
    gray_fr = cv2.cvtColor(rightImg,cv2.COLOR_BGR2GRAY)

    retl, corners_l = cv2.findChessboardCorners(gray_fl, k.CHECKERBOARD, flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    retr, corners_r = cv2.findChessboardCorners(gray_fr, k.CHECKERBOARD, flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

    if (not retl) or (not retr):
        print("Failed to find corners")
        return
    capped = True
    leftCur = leftImg.copy()
    rightCur = rightImg.copy()
    leftWithCorners = cv2.drawChessboardCorners(leftImg, k.CHECKERBOARD, corners_l, retl)
    rightWithCorners = cv2.drawChessboardCorners(rightImg, k.CHECKERBOARD, corners_r, retr)
    leftRender = leftWithCorners
    rightRender = rightWithCorners
    print("Showing Capturued Image")

def accept():
    global capped, leftList, rightList, numCapped
    if not capped: return print("hvane't captured anything")
    leftList.append(leftCur)
    rightList.append(rightCur)
    capped = False 
    numCapped += 1
    print("Accepted Image, now {} captured".format(str(numCapped)))
def reject():
    global capped
    capped = False
    print("Going back to normal stream, last capture not saved")

def save():
    print("{} pairs of images will be saved, Current Save directory: {}".format(numCapped, destParent)); 
    status = input("If continue, enter Y, any other key is cancel")
    if not status.strip().lower() == 'y':
        print("suscessfully canceled operation.")
        return
    print("Saving...")
    left = Path(leftDir).mkdir(parents=True, exist_ok=True)
    right = Path(rightDir).mkdir(parents=True, exist_ok=True)
    for i in range(numCapped):
        cv2.imwrite(leftDir + "/{}.png".format(str(i)), leftList[i]) 
        cv2.imwrite(rightDir + "/{}.png".format(str(i)), rightList[i]) 
    print("Saved {} images to {}".format( numCapped, destParent))
    h.thr_q()
    exit()


tti = helpers.tti()
tti.add_command("capture", "capture an image for calib", [], capture)
tti.add_alias("c", "capture")
tti.add_command("accept", "accept a captured image", [], accept)
tti.add_alias("a", "accept")
tti.add_command("reject","reject a captured image", [], reject)
tti.add_alias("r", "reject")
tti.add_command("save", "save the images to your local fs", [], save)

tti_thread = threading.Thread(target=tti.listen)
tti_thread.setDaemon(True)
tti_thread.start()

def main_loop():
    cv2.waitKey(1)
    global leftRender, rightRender
    if capped: 
        cv2.imshow("left", leftRender)
        cv2.imshow("right", rightRender)
        return
    
    retl, leftImg = left.read()
    retr, rightImg = right.read()
    if (not retl) or (not retr):
        return
    cv2.imshow("left", rightImg)
    cv2.imshow("right", leftImg)
    
    

while True:
    time_start = time.time_ns()
    main_loop()
    delta_left = (time_start + k.LIMIT_TIME_30_FPS_NS) - time.time_ns()

    time.sleep(h.non_negative_or_0(delta_left * (1/(1000*1000*1000))))