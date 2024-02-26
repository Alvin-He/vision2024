#!/usr/bin/env python3

# import ntcore
# from networktables import NetworkTables
from argparse import ArgumentParser
import cv2 as cv
import numpy as np

from estimator import Estimator
import cameras

import world

import const as k
import cameras as c
import helpers

# def updateNetworkTag(tagTable, i, r, t):
#   table = tagTable.getSubTable(str(i))
#   rot = table.getSubTable("Rot")
#   trans = table.getSubTable("Trans")

#   rot.putNumber("X", r[0])
#   rot.putNumber("Y", r[1])
#   rot.putNumber("Z", r[2])

#   trans.putNumber("X", t[0])
#   trans.putNumber("Y", t[1])
#   trans.putNumber("Z", t[2])

# parser = ArgumentParser(
#   description = "AprilTag pose estimation solution meant to run on an NVIDIA Jetson Nano.",
#   add_help = True
# )

# parser.add_argument("-s", "--server")
# parser.add_argument("-c", "--camera_id")
# parser.add_argument("--nt3", action = "store_true")
# args = parser.parse_args()

# NetworkTables.initialize(server = args.server)
# mainTable = NetworkTables.getTable("SmartDashboard/VisionServer")
# tagTable = mainTable.getSubTable("Tags")

# video = cv.VideoCapture(int(args.camera_id))
video = cv.VideoCapture(2)
poseEstimator = Estimator(cameras.MAIN_45FOV)

# for tag in tagTable.getSubTables():
#   updateNetworkTag(tagTable, tag, [0, 0, 0], [0, 0, 0])

robot = world.RobotPositionTracker()

roboSize = (100, 70) #np.array([110,70])
frontCord = np.abs(100 - np.array([150, 100]))
pt1Cord = np.abs(100 - np.array([150, 100]))
# pt2Norm = 100 + roboSize/2
def drawRobot(rot):
  theta = np.deg2rad(rot)
  screen = np.zeros([200,200,3], dtype=np.uint8)

  xp1, yp1 = helpers.rotatePoint(*pt1Cord, theta)

  # r2 = np.sqrt(np.sum(np.power(pt2Norm, 2)))
  # xp2 = r2*np.cos(np.arctan(pt2Norm[1]/pt2Norm[0]) + theta)
  # yp2 = r2*np.sin(np.arctan(pt2Norm[1]/pt2Norm[0]) + theta)
  
  # draw robot 
  rect = cv.RotatedRect((100,100), roboSize, rot)
  screen = cv.drawContours(screen, [np.array(rect.points(), dtype=int)], -1, (100, 0, 60), 3) # robot

  # robot front
  frect = cv.RotatedRect((100 + helpers.rotatePoint(*frontCord, theta)).astype(np.int8), (5,30), rot)
  screen = cv.drawContours(screen, [np.array(frect.points(), dtype=int)], -1, (0, 0, 155), -1) 

  screen = cv.circle(screen, (int(100 + xp1), int(100 + yp1)), 2, (0, 255, 0), -1) #camera
  cv.imshow("robot mini map", screen)


while True:
  ret, image = video.read()
  # image = cv.rotate(image, cv.ROTATE_180)
  # image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

  tagPoses = poseEstimator.estimate(image)
  robot.update(c.MAIN_45FOV, tagPoses)
  robot_pos = robot.getPos()
  # print(robot_pos.x, robot_pos.y)
  drawRobot(robot_pos.theta)
  for i in tagPoses:
    distance = (np.sqrt(i.tvecs[0]**2 + i.tvecs[1]**2 + i.tvecs[2]**2) * k.APRILTAG_BLOCK_SIZE_mm) / 10
    # print(distance)
  # for i, (r, t) in enumerate(tagPoses):
  #   updateNetworkTag(tagTable, i, r, t)

  if cv.waitKey(30) == 1: break
