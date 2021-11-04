import argparse
import sys
import numpy as np
import cv2

# Dict_4x4_50 the 4x4 denotes denotes 4*4 = 16 bits in the image
# the 50 denotes that there are 50 unique markers of this type
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

# Lets parse args and gen some markers
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
        help="path to output image containing aruco tag")
ap.add_argument("-i", "--id", type=int, required=True,
        help="ID of aruco tag to gen")
ap.add_argument("-t", "--type", type=str,
        default="DICT_4X4_50",
        help="type of ARUCO tag to generate")
args= vars(ap.parse_args())

# Lets verify some args
if ARUCO_DICT.get(args["type"], None) is None:
    print("[INFO] ArUCo tag of '{}' is not supported".format(args["type"]))
    sys.exit(0)

# load the aruco dict
arucodict = cv2.aruco.Dictionary_get(ARUCO_DICT[args["type"]])
print(ARUCO_DICT[args["type"]])

# lets gen some markers
print("[INFO] generating AruCo tag type '{}' with ID '{}'".format(args["type"], args["id"]))

tag = np.zeros((300, 300, 1), dtype="uint8")
cv2.aruco.drawMarker(arucodict, args["id"], 300, tag, 1)

cv2.imwrite(args["output"], tag)
#  cv2.imshow("ArUCo Tag", tag)
#  cv2.waitKey(0)
