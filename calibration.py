import cv2
import numpy as np

def mouse_click(event, x, y, flags, param):
    global points, frame

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            cv2.circle(frame, (x, y), 5, (0,0,255), -1)
            print("Point", len(points), ":", (x,y))

def calibrate_board(frame): # en sentido horario

    global points
    points = []

    display = frame.copy()

    cv2.namedWindow("Calibration")
    cv2.setMouseCallback("Calibration", mouse_click)

    while True:

        cv2.imshow("Calibration", frame)

        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break

        if len(points) == 4:
            break

    cv2.destroyWindow("Calibration")

    p1, p2, p3, p4 = points

    x = p1[0]
    y = p1[1]

    width  = p2[0] - p1[0]
    height = p4[1] - p1[1]

    return (x, y, width, height)

frame = cv2.imread("test_images\Screenshot 2026-03-10 093918.png")
board = calibrate_board(frame)
x, y, w, h = board
preview = frame.copy()

cell_w = w / 10
cell_h = h / 20

for row in range(20):
    for col in range(10):

        px = int(x + col*cell_w + cell_w/2)
        py = int(y + row*cell_h + cell_h/2)

        cv2.circle(preview,(px,py),2,(0,0,255),-1)

cv2.rectangle(preview,(x,y),(x+w,y+h),(0,255,0),2)
cv2.imshow("Sampling Grid", preview)
cv2.waitKey(0)
cv2.destroyAllWindows()