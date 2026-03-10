import cv2
import numpy as np

def compute_sample_points(x, y, w, h):

    points = []

    cell_w = w / 10
    cell_h = h / 20

    for row in range(20):

        row_points = []

        for col in range(10):

            px = int(x + col*cell_w + cell_w/2)
            py = int(y + row*cell_h + cell_h/2)

            row_points.append((px,py))

        points.append(row_points)

    return points

def draw_sample_points(frame, sample_points):

    for row in sample_points:
        for (px,py) in row:

            cv2.circle(frame,(px,py),2,(0,0,255),-1)

    return frame

frame = cv2.imread("test_images\Screenshot 2026-03-10 093918.png")

# en base a la prueba, se obtuvo estas dimensiones
x = 808
y = 218
w = 342
h = 679

print("Board:", x, y, w, h)

cell_w = w / 10
cell_h = h / 20

samplePoints = compute_sample_points(x,y,w,h)
preview = draw_sample_points(frame.copy(), samplePoints)

cv2.imshow("Sampling Grid", preview)
cv2.waitKey(0)
cv2.destroyAllWindows()

