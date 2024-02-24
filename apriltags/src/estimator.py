import cv2 as cv
import numpy as np
import helpers

lineThingPoints = np.float32([
  (0, 0, 0), # origin
  (-2, 0, 0), # x 
  (0, -2, 0), # y 
  (0, 0, 2) # z
])
point = lambda t: (int(t[0][0]), int(t[0][1]))


class EstimationResult:
  def __init__(self, tag_id, rvecs, tvecs) -> None:
    self.id = tag_id
    self.rvecs = rvecs
    self.tvecs = tvecs

class Estimator:
  def __init__(self, camera):
    self.matrix = np.matrix(camera["matrix"])

    self.distCoeffs = np.matrix(camera["distCoeffs"])

    self.objectPoints = np.matrix([
      [-4, 4, 0], # every 1 distance is 33 mm
      [4, 4, 0],
      [4, -4, 0],
      [-4, -4, 0]
    ], dtype = "double")

    self.detector = cv.aruco.ArucoDetector(
      dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_36h11),
      detectorParams = cv.aruco.DetectorParameters()
    )

  def estimate(self, image) -> list[EstimationResult]:
    out = []
    image_old = image.copy()
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    corners, ids, rejected = self.detector.detectMarkers(image)
    for i in range(len(corners)):
      corner = corners[i]
      id = ids[i]

      ret, rvec, tvec = cv.solvePnP(self.objectPoints, corner, self.matrix, self.distCoeffs)
      rmat = cv.Rodrigues(rvec)[0]
      rmat = np.matrix(rmat).T
      pmat = -rmat * np.matrix(tvec)

      computedImagePoints, j = cv.projectPoints(self.objectPoints, rvec, tvec, self.matrix, self.distCoeffs)
      for [[x, y]] in computedImagePoints: cv.circle(image_old, (int(x), int(y)), 5, (0, 255, 0), -1)

      computedLineThingPoints, j = cv.projectPoints(lineThingPoints, rvec, tvec, self.matrix, self.distCoeffs)
      cv.line(image_old, point(computedLineThingPoints[0]), point(computedLineThingPoints[1]), (255, 0, 0), 3)
      cv.line(image_old, point(computedLineThingPoints[0]), point(computedLineThingPoints[2]), (0, 255, 0), 3)
      cv.line(image_old, point(computedLineThingPoints[0]), point(computedLineThingPoints[3]), (0, 0, 255), 3)

      cv.putText(image_old, "Rot: " + str(np.around(rvec * (180 / np.pi), 3)), (10, image.shape[0] - 40), cv.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
      cv.putText(image_old, "Trans: "+ str(np.around(tvec, 3)), (10, image.shape[0] - 10), cv.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)

      
      # out.append((np.ravel(rvec), np.ravel(pmat.reshape(1, 3))))
      out.append(EstimationResult(id, np.ravel(rvec), np.ravel(pmat.reshape(1, 3))))
      print(np.rad2deg(helpers.rodRotMatToEuler(cv.Rodrigues(rvec)[0])))
      
    
    image_old = helpers.image_resize(image_old, 1080, 920)
    cv.imshow("img", image_old)
    return out
