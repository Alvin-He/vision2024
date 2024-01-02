


import const
import cam_calib_20231231_16_01_02 as calib
import cv2


mtxL = calib.CAM_CALIB_DATA["Left"]["camera_matrix"]
distL = calib.CAM_CALIB_DATA['Left']["distortion_coeff"]
rvecsL = calib.CAM_CALIB_DATA['Left']["rotation_vectors"]
tvecsL = calib.CAM_CALIB_DATA['Left']['translation_vectors']


mtxR = calib.CAM_CALIB_DATA["Right"]["camera_matrix"]
distR = calib.CAM_CALIB_DATA['Right']["distortion_coeff"]
rvecsR = calib.CAM_CALIB_DATA['Right']["rotation_vectors"]
tvecsR = calib.CAM_CALIB_DATA['Right']['translation_vectors']




flags = 0
flags |= cv2.CALIB_FIX_INTRINSIC
# Here we fix the intrinsic camara matrixes so that only Rot, Trns, Emat and Fmat are calculated.
# Hence intrinsic parameters are the same 
 
criteria_stereo= (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
 
# This step is performed to transformation between the two cameras and calculate Essential and Fundamenatl matrix
retS, new_mtxL, distL, new_mtxR, distR, Rot, Trns, Emat, Fmat = cv2.stereoCalibrate(obj_pts, img_ptsL, img_ptsR, new_mtxL, distL, new_mtxR, distR, imgL_gray.shape[::-1], criteria_stereo, flags)
