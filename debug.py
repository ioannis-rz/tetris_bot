def draw_sample_points(frame, sample_points):

    for row in sample_points:
        for (px,py) in row:

            cv2.circle(frame,(px,py),2,(0,0,255),-1)

    return frame

def draw_board_state(frame, sample_points, board):

    for r in range(20):
        for c in range(10):

            px, py = sample_points[r][c]

            if board[r][c] == 1:
                cv2.circle(frame, (px,py), 6, (0,255,0), -1)

    return frame
