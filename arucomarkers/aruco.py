import argparse
import sys
import imutils
from cv2 import cv2

ARUCO_DICT = {
"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}
# parse args
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
        help="path to input image containing ArUCo tag")
ap.add_argument("-t", "--type", type=str,
        default="DICT_ARUCO_ORIGINAL",
        help="type of ArUCo tag to detect")
args = vars(ap.parse_args())

print("Info: loading img")

img = cv2.imread(args["image"])
#might need to change this since img displayed is 300px... or not
img = imutils.resize(img, width=600)

# verify given aruco tag
if ARUCO_DICT.get(args["type"], None) is None:
    print("Info: Aruco tag of '{}' is not supported".format(args["type"]))
    sys.exit(0)

# load the relavant dict, grab params and detect markers
print("Info: detecting '{}' tags".format(args["type"]))

arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[args["type"]])
arucoParams = cv2.aruco.DetectorParameters_create()

(corners, ids, reject) = cv2.aruco.detectMarkers(img, arucoDict, parameters=arucoParams)

# visualize detected markers
if len(corners) > 0:
    ids=ids.flatten() #flatten ids list

    #loop through detected markers
    for (markerCorner, markerId) in zip(corners, ids):
        #extract marker corners
        #corners are stored in top-left, top-right,  bottom-right, bottom-left order
        corners = markerCorner.reshape((4,2))
        (topLeft, topRight, bottomRight, bottomLeft) = corners

        # convert x-y pairs to ints
        topLeft= tuple(map(int, topLeft))
        topRight = tuple(map(int, topRight))
        bottomRight= tuple(map(int, bottomRight))
        bottomLeft = tuple(map(int, bottomLeft))

        # draw bounding box of detection
        cv2.line(img, topLeft, topRight, (0,255,0), 2)
        cv2.line(img, topRight, bottomRight, (0,255,0), 2)
        cv2.line(img, topLeft, bottomLeft, (0,255,0), 2)
        cv2.line(img, bottomLeft, bottomRight, (0,255,0), 2)

        # compute and draw the center of the marker

        # center of diag
        cX = (topLeft[0] + bottomRight[0])//2
        cY = (topLeft[1] + bottomRight[1])//2

        cv2.circle(img, (cX,cY), 4, (0,0,255), -1)

        #draw id
        cv2.putText(img, str(markerId),
            (topLeft[0], topLeft[1]-15), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0,255,0),2)

        print("Info: Marker ID: {}".format(markerId))
        print("Info Top Left Corner: ({}, {})".format(topLeft[0], topLeft[1]))
        print("Info Top Right Corner: ({}, {})".format(topRight[0], topRight[1]))
        print("Info Bottom Left Corner: ({}, {})".format(bottomLeft[0], bottomLeft[1]))
        print("Info Bottom Right Corner: ({}, {})".format(bottomRight[0], bottomRight[1]))

        #display image
        cv2.imshow("image",img)
        cv2.waitKey(0)

else:
    print("Info: no images detected")
