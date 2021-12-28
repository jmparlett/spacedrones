#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Jonathan Parlett
#Program Name: camCalib
#Created: 2021-December-28

import numpy as np
import cv2 as cv
import glob


# beware the absolute path, you must change this if running elsewhere
imgpath = "/home/jp/Documents/gitRepos/spacedrones/opencv/camCalib/imgs"

# Termination Criteria for the findCornerSubpix() algorithm
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points (we use an 8x8 grid)
objp = np.zeros((8*8,3), np.float32)
objp[:,:2] = np.mgrid[0:8,0:8].T.reshape(-1,2)
print(objp)

# Object point and Image point arrays taken from all images
objpoints = [] #3d points in real space
imgpoints = [] #2d points in image space


images = glob.glob(imgpath+"/*.jpg")
print(images)

# now we loop over all images and grab the 2d and 3d points we find
for file in images:
    img = cv.imread(file)
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

    # debug stuff
    #  cv.imshow(file,img)
    #  cv.waitKey(0)

    # find chess board corners
    ret, corners = cv.findChessboardCorners(gray, (8,8), None) #remember were using an 8x8 board

    # if found add object and image points after we refine them
    if ret == True:
        objpoints.append(objp)

        cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria) # this function seems pretty complex https://theailearner.com/tag/cv2-cornersubpix/
        imgpoints.append(corners)

        # draw and display corners
        cv.drawChessboardCorners(img, (8,8), corners, ret)
        cv.imshow("board",img)
        cv.waitKey(0)

# now that we have all our points we can finally get what we came for, our camera matrix, and rotation and translation vectors
ret, cmatrix, dist, rotationVecs, translationVecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# first lets optimize our new camera matrix
img = cv.imread(imgpath+"/2021-12-28-154431.jpg")
# slice the dimensions out
h, w = img.shape[:2]
newCMatrix, roi = cv.getOptimalNewCameraMatrix(cmatrix, dist, (w,h),1,(w,h))

# with all our constants found we can undistort an image using cv.undistort()
dst = cv.undistort(img,cmatrix, dist, None, newCMatrix)

# crop it 
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite("calibOrig.png", img)
cv.imwrite("calibResult.png", dst)

 #--------- Save result
filename = "cameraMatrix.txt"
np.savetxt(filename, cmatrix, delimiter=',')
filename = "cameraDistortion.txt"
np.savetxt(filename, dist, delimiter=',')

# lets find error
meanError = 0
totError = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(objpoints[i], rotationVecs[i], translationVecs[i], cmatrix, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
    meanError += error
print("total Error:", meanError/len(objpoints))


if __name__ == "__main__":
    print("template for camCalib created!!")
