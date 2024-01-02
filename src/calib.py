
# a combination of https://github.com/THRYLLR/opencv-testing/blob/0cacfc76a06e5592ce0bb22b491f13d01c5c97a8/opencv-calibrate.py
# and opencv totorials 

import cv2
import numpy as np
import os
import glob
import sys
import io
import re

import threading
import time
import json

import const as k
import helpers
h = helpers.namespace_global

# Defining the dimensions of checkerboard
# (rows, columns), counting inner corners so it would be # of block per direction - 1
CHECKERBOARD = (6, 9) 
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Creating vector to store vectors of 3D points for each checkerboard image
objpoints = []
# Creating vector to store vectors of 2D points for each checkerboard image
imgpoints_l = [] 
imgpoints_r = []
 
# Defining the world coordinates for 3D points
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
prev_img_shape = None

# open camera streams
left = cv2.VideoCapture(k.CAM_ID_LEFT)
right = cv2.VideoCapture(k.CAM_ID_RIGHT) 

# cam = cv2.VideoCapture(int(input("Enter cam id for calib <int>:\n")))

cv2.namedWindow('left')
cv2.namedWindow('right')

def show_imgs(left, right):
    cv2.imshow('left', left)
    cv2.imshow('right', right)
    cv2.waitKey(1)

command_capture = False
command_continue = True
command_continuous = False
command_exist = False

img_left = None
img_right = None

amount_captured = 0
def main_loop():
    global command_capture, command_exist, command_continue
    global img_left, img_right

    retl, frame_left = left.read()
    retr, frame_right = right.read()
    
    if not (retl or retr): 
        print("Faliled to get frame, skipping\n")
        return
    # if not capturing, show feed
    if (not command_continuous) and not command_capture: return show_imgs(frame_left, frame_right)
    # if capturing, but not coninuing, then show buffered image and wait for user input
    if (not command_continuous) and not command_continue: return show_imgs(img_left, img_right)

    gray_fl = cv2.cvtColor(frame_left,cv2.COLOR_BGR2GRAY)
    gray_fr = cv2.cvtColor(frame_right,cv2.COLOR_BGR2GRAY)

    retl, corners_l = cv2.findChessboardCorners(gray_fl, CHECKERBOARD, flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    retr, corners_r = cv2.findChessboardCorners(gray_fr, CHECKERBOARD, flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

    if (not retl) or (not retr): 
        command_capture = False
        if command_continuous: return show_imgs(frame_left, frame_right)
        return print("Faliled to find chess board, skipping")
    command_capture = True

    """
    If desired number of corner are detected,
    we refine the pixel coordinates and display 
    them on the images of checker board
    """
    
    # refining pixel coordinates for given 2d points.
    corners2_l = cv2.cornerSubPix(gray_fl, corners_l, (11,11),(-1,-1), criteria)
    corners2_r = cv2.cornerSubPix(gray_fr, corners_r, (11,11),(-1,-1), criteria)


    # Draw and display the corners
    img_left = cv2.drawChessboardCorners(frame_left, CHECKERBOARD, corners2_l, retl)
    img_right = cv2.drawChessboardCorners(frame_right, CHECKERBOARD, corners2_r, retr)

    if command_capture:
        objpoints.append(objp)

        imgpoints_l.append(corners2_l)
        imgpoints_r.append(corners2_r)
    
    command_continue = False
    print("Please etner `accept` if this image should be used for calibration or `reject` if not")
    if command_continuous: return show_imgs(img_left, img_right)



def generate_calibrate_data(cam_id, img, objpoints, imgpoints):
    h,w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    if (not ret):
        print("for some reason we refused to generate the final data, so you gotta start over again :)")

    new_mtx, roi= cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

    data = {
        "id": cam_id,
        "mtx": mtx, 
        "dist": dist,
        "rvecs": rvecs,
        "tvecs": tvecs, 
        "new_mtx": new_mtx,
        "roi": roi
    }
    return data

# yes, I have asboulotely no idea what's going on behind the scences, just following and copying a totorial
# will not question it 
def stero_calibrate():
    # camera calibration 
    d_left = generate_calibrate_data(k.CAM_ID_LEFT, img_left, objpoints, imgpoints_l)
    d_right = generate_calibrate_data(k.CAM_ID_RIGHT, img_right, objpoints, imgpoints_r)

    # stero calibration 
    flags = cv2.CALIB_FIX_INTRINSIC

    gray_size = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY).shape[::-1] # left and right cam have the same image size
    retS, new_mtxL, distL, new_mtxR, distR, Rot, Trns, Emat, Fmat = cv2.stereoCalibrate(objpoints, imgpoints_l, imgpoints_r, d_left["new_mtx"], d_left["dist"], d_right["new_mtx"], d_right["dist"], gray_size, criteria, flags)

    rectify_scale = 1
    rect_l, rect_r, proj_mat_l, proj_mat_r, Q, roiL, roiR= cv2.stereoRectify(new_mtxL, distL, new_mtxR, distR, gray_size, Rot, Trns, rectify_scale,(0,0))
    
    #generate the stero maps (still magic)
    Left_Stereo_Map= cv2.initUndistortRectifyMap(new_mtxL, distL, rect_l, proj_mat_l, gray_size, cv2.CV_16SC2)
    Right_Stereo_Map= cv2.initUndistortRectifyMap(new_mtxR, distR, rect_r, proj_mat_r, gray_size, cv2.CV_16SC2)

    data = {
        "size": gray_size,
        "left_id": k.CAM_ID_LEFT,
        "right_id": k.CAM_ID_RIGHT,
        "stereo_maps": {
            "left": {"x": Left_Stereo_Map[0], "y": Left_Stereo_Map[1]},
            "right": {"x":Right_Stereo_Map[0], "y": Right_Stereo_Map[1]}
        },
        "stero_rectify": {
            "rect_l": rect_l, "rect_r": rect_r, "proj_mat_l": proj_mat_l, "proj_mat_r": proj_mat_r, "Q": Q, "roiL": roiL, "roiR": roiR
        },
        "calibrations": {
            "stereo": {"retS": retS, "new_mtxL": new_mtxL, "distL": distL, "new_mtxR": new_mtxR, "distR": distR, "Rot": Rot, "Trns": Trns, "Emat": Emat, "Fmat": Fmat}, 
            "left": d_left,
            "right": d_right
        } 
    }
    return data

# UI (or me trying to do things so it lookslike I'm doing smth)
tti = helpers.tti()
def tti_capture():
    global command_capture
    command_capture = True
tti.add_command("capture", "capture an image to process for calib", [], tti_capture)
tti.add_alias("c", "capture")
def tti_accept():
    global command_continue, command_capture, amount_captured
    if command_continue != False: return print("Nothing saved, run capture first")
    command_continue =  True
    command_capture = False
    amount_captured += 1
    if amount_captured == k.CALIB_TARGET_IMAGES:
        print("Generating final calibration parameters... This will take a minute...")
        data = stero_calibrate()

        file = open("cam_calib_{}.py".format(time.strftime("%Y%m%d_%H_%M_%S", time.localtime())), "w+t")
        np.set_printoptions(threshold=sys.maxsize)
        print("import numpy as np\narray=np.array\n#⌄--START_DATA--⌄#\n\n", file=file)
        # j_data = json.JSONEncoder().encode(data)
        print("data=", file=file, end="")

        str_data = str(data)
        pattern = re.compile(r"(,\s*dtype=)(.*)(\))")

        proced_str_data = pattern.sub(r"\1np.\2\3", str_data)
        print(proced_str_data, file=file)
        print("\n\n#^--END_DATA--^#", file=file)
        file.flush()
        file.close()
        print("Calibration result written to:\n\t{}".format(os.path.realpath(file.name)))
        print("Finished calibrating, Please make sure the values are saved. ")
        print("\n\n\n")
        h.thr_q()
    print("Saved left and right calib data. Proceeding with video capture, still need: {} images".format(k.CALIB_TARGET_IMAGES-amount_captured))
tti.add_command("accept", "accept the captured image", [], tti_accept)
tti.add_alias("a", "accept")
def tti_reject():
    global command_continue, command_capture
    if command_continue != False: return print("Nothing saved, run capture first")
    command_continue =  True
    command_capture = False

    objpoints.pop()
    imgpoints_l.pop()
    imgpoints_r.pop()
    print("The capture was rejected. Resuming feed.")
tti.add_command("reject", "reject the captured image", [], tti_reject)
tti.add_alias("r", "reject")
def tti_continuous(flag):
    global command_continuous
    if flag == "yes" or flag == "y" or flag == "true" or flag == "enable":
        command_continuous = True
    else:
        command_continuous = False
    print("Continuous mode set to: " + str(command_continuous))
tti.add_command("set_continuous", "Weather to continuously check for checker boards, !! might lag !!.", ["yes_or_no"], tti_continuous)


tti_thread = threading.Thread(target=tti.listen)
tti_thread.setDaemon(True)
tti_thread.start()


time_start=time.time_ns()
while True:
    time_start = time.time_ns()
    main_loop()
    delta_left = (time_start + k.LIMIT_TIME_30_FPS_NS) - time.time_ns()
    
    time.sleep(h.non_negative_or_0(delta_left * (1/(1000*1000*1000))))


