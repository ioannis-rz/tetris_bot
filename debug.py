import cv2
from pynput.keyboard import Controller, Key

MOVE_RIGHT = Key.right
MOVE_LEFT = Key.left
MOVE_DOWN = Key.down
SNAP_DOWN = Key.space
ROTATELEFT = "z"
SAVE = 'c'

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

def print_moves(moves):
    names = {
        MOVE_LEFT: "LEFT",
        MOVE_RIGHT: "RIGHT",
        MOVE_DOWN: "DOWN",
        SNAP_DOWN: "HARD DROP",
        ROTATELEFT: "ROTATE LEFT",
        SAVE: "HOLD"
    }
    readable = [names.get(move, str(move)) for move in moves]

    print("Moves:", " -> ".join(readable))

def print_move_info(piece, best_move, moves):
    print(f"Piece: {piece[0]}")
    print(f"Current rotation: {piece[1]}")
    print(f"Current column: {piece[2]}")
    print(f"Target rotation: {best_move[0]}")
    print(f"Target column: {best_move[1]}")
    print_moves(moves)
    print("-" * 40)