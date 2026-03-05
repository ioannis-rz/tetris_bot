import cv2 as cv
from PIL import Image, ImageGrab
import cv2 as cv
import numpy as np

def detect_sprite(frame, template, threshold=0.7):

    result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)
    cv.imshow("Heatmap", result)
    locations = np.where(result >= threshold)

    detections = []
    for pt in zip(*locations[::-1]):
        detections.append(pt)

    return detections

frame = cv.imread("test_images/frame.png")
 # cv.imread(cv.samples.findFile("test_images/frame.png")
templateMi = cv.imread("test_images/misionero.png", cv.IMREAD_COLOR)
templateCa = cv.imread("test_images/canibal2.png", cv.IMREAD_COLOR)

detections1 = detect_sprite(frame, templateMi)
# detections2 = detect_sprite(frame, templateCa)
for x, y in detections1:
    cv.rectangle(
        frame,
        (x, y),
        (x + templateMi.shape[1], y + templateMi.shape[0]),
        (255,0,0),
        2
    )

cv.imshow("result", frame)
cv.waitKey(0)
