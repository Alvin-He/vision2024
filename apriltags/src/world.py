from estimator import EstimationResult
import numpy as np
import time 
import helpers

#https://stackoverflow.com/a/45399188 #1.2 works pretty well to kick out more than ~5 cm of difference
def reject_outliers_2(data, m=1.2):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return data[s < m]

ns_to_sec = lambda x: x * (1/(1000*1000*1000))
cm_to_m = lambda x: x * (1/100)
## Blue alliance bottom left corner with the Source Station is 0,0
## alliance walls are X and the other 2 sides areY
## the right direction is 0 deg or 0 rad --> 
##   the robot should start facing 0 on blue and start facing -180 on red
#### EVERYTHING IS IN CM AND DEGREES

class RobotPos:
    def __init__(self, x, y, theta) -> None:
        self.x = x
        self.y = y
        self.theta = theta
        
# c1: camera axis1, c2: camera acis2, cInitRot: camera initial rotation, tx: tag world axis1, ty: tag world axis2, rRot: robot current rotation
# The order of axis (x or y) doesn't matter
# NOTE: THIS DOES NOT OUTPUT A DETERMINISTIC COORDINDATE, NEED TO HAVE ANOTHER CAMERA TO LOOK AT IT BE SURE
def camRelativeToAbsoulote(c1, c2, cInitRot, t1, t2, rRot) -> list[np.double, np.double]:
    theta = np.array(cInitRot + rRot, dtype=np.double) # force datatype

    # see discrod pin message for math
    b = (t1*np.cos(theta) - t2*np.sin(theta))
    r_1 = b + np.sqrt(b**2 + c1**2 + c2**2 - t1**2 - t2**2)
    r_2 = b - np.sqrt(b**2 + c1**2 + c2**2 - t1**2 - t2**2)
    
    cord1 = [r_1 * np.cos(theta), r_1 * np.sin(theta)]
    cord2 = [r_2 * np.cos(theta), r_2 * np.sin(theta)]

    return [cord1, cord2]
    


APRILTAG_MAX_ID_EXIST = 16
SINGLE_SPEED_LIMIT_MPS = 10

# source to main alliance wall angle is 120 deg
WORLD_SIZE = (1654, 821)
WORLD_TAG_LOCATIONS = { # x,y,z,yaw
    "0": (0, 0, 0, 0), # testing tag, doesn't actually exist on the field
    "1": (1507.9472, 24.5872, 135.5852, 120), 
    "2": (1618.5134, 88.2904, 135.5852, 120),
    "3": (1657.9342, 498.2718, 145.1102, 180),
    "4": (1657.9342, 218.42, 145.1102, 180),
    "5": (1470.0758, 820.42, 135.5852, 270),
    "6": (184.15, 820.42, 135.5852, 270),
    "7": (-3.81, 554.7868, 145.1102, 0), 
    "8": (-3.81, 498.2818, 145.1102, 0), 
    "9": (35.6108, 88.3666, 135.5852, 60),
    "10":(146.1516, 24.5872, 135.5852, 60),
    "11":(1190.4726, 371.3226, 132.08, 300),
    "12":(1190.4726, 449.834, 132.08, 60),
    "13":(1122.0196, 410.5148, 132.08, 180),
    "14":(532.0792, 410.5148, 132.08, 0),
    "15":(464.1342, 449.834, 132.08, 120),
    "16":(464.1342, 371.3226, 132.08, 240),
}


#x, y, z of robot dimensions
ROBOT_SIZE_cm = (800, 500, 600)


class RobotPositionTracker:
    def __init__(self) -> None:
        self.previousLocations = []# buffer
        self._prevLocBufLimit = 20

        self.visionBestLocation = RobotPos(0, 0, 0)
        self.lastTrustWorthyUpdateFrameTimeNs = 0

    def update(self, camera, results: list[EstimationResult]):
        if len(results) < 1: return
        cameraTrans = camera["camToRobotPos"]

        all_cords_possible = []
        all_yaw = []
        # all_z = []
        # convert camera relative cords into world cords
        for i in results:
            if i.id > APRILTAG_MAX_ID_EXIST: 
                del results[i]
                print("Found a tag with ID: {}, this tag doesn't exist".format(i.id))
                continue
            tag_x = WORLD_TAG_LOCATIONS[str(i.id)][0]
            tag_y = WORLD_TAG_LOCATIONS[str(i.id)][1]
            tag_yaw = WORLD_TAG_LOCATIONS[str(i.id)][3]

            # camera axis mapping
            yaw = helpers.normAngle(-i.rvecs[1] + 180 - tag_yaw)
            all_yaw.append(yaw)
            cords = camRelativeToAbsoulote(i.tvecs[0], i.tvecs[2], cameraTrans[3], tag_x, tag_y, yaw)
            all_cords_possible.extend(cords)
            # all_z.append(i.tvecs[0])

        # normalize data and kick out outliars due to detection incorrections
        yaw = np.average(reject_outliers_2(np.array(all_yaw)))

        # conclude all the cords into 2, hopefully 1 set of cords


        # apply camera transformations
        x += cameraTrans[0]
        y += cameraTrans[1]
        # don'y worry about z
        yaw += cameraTrans[3]


        print(int(x), int(y), int(yaw))

        curTimeNs = time.time_ns()
        # if (cm_to_m(abs(x - self.visionBestLocation.x))/ns_to_sec(curTimeNs - self.lastTrustWorthyUpdateFrameTimeNs) > SINGLE_SPEED_LIMIT_MPS or
        #   cm_to_m(abs(y - self.visionBestLocation.y))/ns_to_sec(curTimeNs - self.lastTrustWorthyUpdateFrameTimeNs)):
        #     print("Exceed speed limit, loc update at time: {} will not be considered".format(curTimeNs))
        #     return
        
        # stores new locations if physics is obeyed
        self.previousLocations.append(self.visionBestLocation)
        if len(self.previousLocations) > self._prevLocBufLimit: del self.previousLocations[0]
        self.visionBestLocation = RobotPos(x, y, yaw) # TODO: CALCULATE ORIENTATION
        self.lastTrustWorthyUpdateFrameTimeNs = curTimeNs

            



    def getPos(self):
        return self.visionBestLocation

