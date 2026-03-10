# code extracted from https://github.com/fjpereny/image_capture_performance_testing

import mss
from PIL import Image, ImageGrab
import pyautogui
import cv2 as cv
import numpy as np
import time
import dxcam

w, h = pyautogui.size()
print("PIL Screen Capture Speed Test")
print("Screen Resolution: " + str(w) + 'x' + str(h))

img = None
t0 = time.perf_counter()
n_frames = 1

while True:
    img = ImageGrab.grab()
    img = np.array(img)                         # Convert to NumPy array
    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)    # Convert RGB to BGR color
    
    small = cv.resize(img, (0, 0), fx=0.5, fy=0.5)
    cv.imshow("Computer Vision", small)

    # Break loop and end test
    key = cv.waitKey(1)
    if key == ord('q'):
        break
    
    elapsed_time = time.perf_counter() - t0
    avg_fps = (n_frames / elapsed_time)
    print("Average FPS PIL: " + str(avg_fps))
    n_frames += 1

    
w, h = pyautogui.size()
print("MSS Screen Capture Speed Test")
print("Screen Resolution: " + str(w) + 'x' + str(h))
img = None
t0 = time.perf_counter()
n_frames = 1

monitor = {"top": 0, "left": 0, "width": w, "height": h}
with mss.mss() as sct:
    while True:
        img = sct.grab(monitor)
        img = np.array(img)                         # Convert to NumPy array
        # img = cv.cvtColor(img, cv.COLOR_RGB2BGR)  # Convert RGB to BGR color
        
        small = cv.resize(img, (0, 0), fx=0.5, fy=0.5)
        cv.imshow("Computer Vision", small)

        # Break loop and end test
        key = cv.waitKey(1)
        if key == ord('q'):
            break
        
        elapsed_time = time.perf_counter() - t0
        avg_fps = (n_frames / elapsed_time)
        print("Average FPS in MSS: " + str(avg_fps))
        n_frames += 1


# my own code
camera = dxcam.create(output_color="BGR")
camera.start(target_fps=120)

print("dxcam Screen Capture Speed Test")
print("Screen Resolution: " + str(w) + 'x' + str(h))
frame = None
t0 = time.perf_counter()
n_frames = 1

while True:
    frame = camera.get_latest_frame()
    #img = np.array(img)                         #  
    small = cv.resize(frame, (0, 0), fx=0.5, fy=0.5)
    cv.imshow("Computer Vision", small)

    # Break loop and end test
    key = cv.waitKey(1)
    if key == ord('q'):
        break

    elapsed_time = time.perf_counter() - t0
    avg_fps = (n_frames / elapsed_time)
    print("Average FPS DXCAM: " + str(avg_fps))
    n_frames += 1
camera.stop()
