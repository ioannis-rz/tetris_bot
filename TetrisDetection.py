import cv2
import numpy as np
import dxcam
import debug

def count_complete_lines(board):

    lines = 0

    for row in range(20):
        if all(board[row]):
            lines += 1

    return lines

def get_bumpiness(heights):

    bumpiness = 0

    for i in range(9):
        bumpiness += abs(heights[i] - heights[i+1])

    return bumpiness

def get_column_heights(board):

    heights = []

    for col in range(10):

        column = board[:, col]

        if np.any(column):
            first_block = np.argmax(column)
            heights.append(20 - first_block)
        else:
            heights.append(0)

    return heights

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

def count_holes(board):

    holes = 0

    for col in range(10):

        block_found = False

        for row in range(20):

            if board[row][col] != 0:
                block_found = True

            elif block_found and board[row][col] == 0:
                holes += 1

    return holes

def correct_board_state(board):
    logic_board = board.copy()
    logic_board[0:4, :] = 0
    return logic_board

def extract_falling_piece(board):

    visited = set()

    for r in range(20):
        for c in range(10):

            if board[r][c] == 1:

                # start flood fill
                stack = [(r,c)]
                piece = []

                while stack:

                    cr, cc = stack.pop()

                    if (cr,cc) in visited:
                        continue

                    if cr < 0 or cr >= 20 or cc < 0 or cc >= 10:
                        continue

                    if board[cr][cc] == 0:
                        continue

                    visited.add((cr,cc))
                    piece.append((cr,cc))

                    stack.append((cr+1,cc))
                    stack.append((cr-1,cc))
                    stack.append((cr,cc+1))
                    stack.append((cr,cc-1))

                if len(piece) == 4:
                    min_r = min(r for r,c in piece)
                    min_c = min(c for r,c in piece)
                    norm = [(r-min_r, c-min_c) for r,c in piece]
                    h = max(r for r,c in norm) + 1
                    w = max(c for r,c in norm) + 1

                    mat = np.zeros((h,w), dtype=int)

                    for r,c in norm:
                        mat[r,c] = 1
                    return mat

    return None

def evaluate_board(board):

    heights = get_column_heights(board)
    aggregate_height = sum(heights)

    holes = count_holes(board)

    bumpiness = get_bumpiness(heights)

    lines = count_complete_lines(board)

    score = (
        -0.5 * aggregate_height
        -0.7 * holes
        -0.3 * bumpiness
        +1.0 * lines
    )

    return score


# cosas que se ejecutan una sola vez
board = np.zeros((20,10))
logic_board = np.zeros((20,10))
#print(board)
# en base a la prueba, se obtuvo estas dimensiones en fullscreen
x = 808
y = 218
w = 342
h = 679
# para dimensiones a pantalla partida
x = 420
y = 404
w = 159
h = 315
camera = dxcam.create(output_color="BGR")
camera.start(target_fps=60, video_mode=True)
samplePoints = compute_sample_points(x,y,w,h)
#preview = debug.draw_sample_points(frame.copy(), samplePoints) # para debug
# crear el objeto para capturar la imagen


print("Press S to start the bot")

while True:
    frame = camera.get_latest_frame()
    frame = cv2.resize(frame, None, fx = 0.25, fy = 0.25, interpolation=cv2.INTER_AREA)
    cv2.imshow("preview", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        print("Starting...")
        cv2.destroyAllWindows()
        break

piece_active = False
piece = None
while True:

    frame = camera.get_latest_frame()

    update_board_state(frame, samplePoints, board) # calcular el estado del tablero de juego
    
    piece = extract_falling_piece(board) # capturtar la pieza nueva que cae, si easta incompleta, retorna None

    if piece is not None and not piece_active: # si la pieza se detecta y no hay pieza previamente detectada
        piece_active = True
        print("New piece detected")
        print(piece)
        logic_board = correct_board_state(board)
        #print(piece)

    if piece is None:
        piece_active = False

    preview = debug.draw_board_state(frame, samplePoints, board)
    preview = cv2.resize(preview, None, fx = 0.5, fy = 0.5, interpolation=cv2.INTER_AREA)
    cv2.imshow("debug screen", preview)
    #print(board)
    if cv2.waitKey(1) == 27: # esc key
        camera.stop()
        cv2.destroyAllWindows()
        break

