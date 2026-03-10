import cv2
import numpy as np

board = np.zeros((20,10))
#print(board)

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
    print(points)
    return points

def draw_sample_points(frame, sample_points):

    for row in sample_points:
        for (px,py) in row:

            cv2.circle(frame,(px,py),2,(0,0,255),-1)

    return frame

def update_board_state(frame, sample_points, board):
    for row in range(20):
        for col in range(10):

            px, py = sample_points[row][col]

            region = frame[py-2:py+3, px-2:px+3]

            b, g, r = region.mean(axis=(0,1))
            brightness = (b + g + r) / 3

            if brightness < 40 and b < 50 and g < 50 and r < 50:
                board[row, col] = 0 
            else:
                board[row, col] = 1


frame = cv2.imread("test_images\Screenshot 2026-03-10 100228.png")

# en base a la prueba, se obtuvo estas dimensiones
x = 808
y = 218
w = 342
h = 679

samplePoints = compute_sample_points(x,y,w,h)
preview = draw_sample_points(frame.copy(), samplePoints)
update_board_state(frame, samplePoints, board)
print(board)
cv2.imshow("Sampling Grid", preview)
cv2.waitKey(0)
cv2.destroyAllWindows()

