from __future__ import print_function
import cv2 as cv
import cv2 as cv
import argparse
import numpy as np

def CannyThreshold(val):
    low_threshold = val # funciona con 10
    img_blur = cv.blur(frame_gray, (3,3))
    detected_edges = cv.Canny(img_blur, low_threshold, low_threshold*ratio, kernel_size)
    mask = detected_edges != 0
    dst = frame * (mask[:,:,None].astype(frame.dtype))
    cv.imshow(window_name, dst)
    return detected_edges

# codigo de deteccion de bordes

max_lowThreshold = 100
window_name = 'Edge Map'
title_trackbar = 'Min Threshold:'
ratio = 3 # ni idea
kernel_size = 3 # ni idea

frame = cv.imread(cv.samples.findFile("test_images/frame.png"))

frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
cv.namedWindow(window_name)
cv.createTrackbar(title_trackbar, window_name , 0, max_lowThreshold, CannyThreshold)
CannyThreshold(0)
cv.waitKey(0)
