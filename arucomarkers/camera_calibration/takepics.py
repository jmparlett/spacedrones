import cv2
import numpy as np
import os


cap = cv2.VideoCapture(0)

i=0;
while(i < 50):
    img_name=f"opencv_frame{i}.jpg"
    ret, img = cap.read()
    cv2.imwrite("calib_images/"+img_name, img)
    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    i+=1


