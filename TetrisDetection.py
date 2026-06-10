import cv2
import debug
import dxcam
import numpy as np
from pynput.keyboard import Controller, Key
import time

TETROMINOS = {

    "I": [
        [[1,1,1,1]],
        [[1],
         [1],
         [1],
         [1]]
    ],

    "O": [
        [[1,1],
         [1,1]]
    ],

    "T": [
        [[0,1,0],
         [1,1,1]],

        [[1,0],
         [1,1],
         [1,0]],

        [[1,1,1],
         [0,1,0]],

        [[0,1],
         [1,1],
         [0,1]]
    ],

    "L": [
        [[1,0],
         [1,0],
         [1,1]],

        [[1,1,1],
         [1,0,0]],

        [[1,1],
         [0,1],
         [0,1]],

        [[0,0,1],
         [1,1,1]]
    ],

    "J": [
        [[0,1],
         [0,1],
         [1,1]],

        [[1,0,0],
         [1,1,1]],

        [[1,1],
         [1,0],
         [1,0]],

        [[1,1,1],
         [0,0,1]]
    ],

    "S": [
        [[0,1,1],
         [1,1,0]],

        [[1,0],
         [1,1],
         [0,1]]
    ],

    "Z": [
        [[1,1,0],
         [0,1,1]],

        [[0,1],
         [1,1],
         [1,0]]
    ]
}

MOVE_RIGHT = Key.right
MOVE_LEFT = Key.left
MOVE_DOWN = Key.down
SNAP_DOWN = Key.space
ROTATELEFT = "z"
SAVE = 'c'

def clear_lines(board):

    full_rows = [r for r in range(20) if all(board[r])]
    cleared = len(full_rows)

    if cleared > 0:
        board = np.delete(board, full_rows, axis=0)
        new_rows = np.zeros((len(full_rows), 10))
        board = np.vstack((new_rows, board))

    return board, cleared

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

def evaluate_board(board, cleared):

    heights = get_column_heights(board)
    aggregate_height = sum(heights)

    holes = count_holes(board)

    bumpiness = get_bumpiness(heights)

    score = (
        -0.8 * aggregate_height
        -0.7 * holes
        -0.3 * bumpiness
        +10.0 * cleared
    )

    return score

def collision(board, piece, row, col):

    for r in range(len(piece)):
        for c in range(len(piece[0])):

            if piece[r][c]:

                rr = row + r
                cc = col + c

                if rr >= 20 or cc < 0 or cc >= 10 or board[rr][cc]:
                    return True
    return False

def place_piece(board, piece, row, col ):

    new = board.copy()

    for r in range(len(piece)):
        for c in range(len(piece[0])):
            if piece[r][c]:
                new[row+r][col+c] = 1

    new, cleared = clear_lines(new)

    return new, cleared

class Enviroment:
    def __init__(self):
        self.camera = dxcam.create(output_color="BGR")
        self.camera.start(target_fps=60, video_mode=True)
        self.keyboard = Controller()

    def get_frame(self):
        return self.camera.get_latest_frame()

    def act(self, moves):
        for move in moves:
            self.keyboard.tap(move)
            time.sleep(0.1)    

class AgentPerception:

    def __init__(self, x, y, w, h):
        self.sample_points = self.compute_sample_points(x,y,w,h)   
        self.board = np.zeros((20,10))

    def get_falling_piece(self):
        visited = set()

        for r in range(4):
            for c in range(10):

                if self.board[r][c] == 1 and (r,c) not in visited:

                    stack = [(r,c)]
                    piece = []

                    while stack:

                        cr, cc = stack.pop()

                        if (cr,cc) in visited:
                            continue
                        if cr < 0 or cr >= 20 or cc < 0 or cc >= 10:
                            continue
                        if self.board[cr][cc] == 0:
                            continue

                        visited.add((cr,cc))
                        piece.append((cr,cc))

                        stack.extend([
                            (cr+1,cc),(cr-1,cc),
                            (cr,cc+1),(cr,cc-1)
                        ])

                    if len(piece) == 4:

                        # normalize coordinates
                        min_r = min(r for r,c in piece)
                        min_c = min(c for r,c in piece)

                        norm = [(r-min_r, c-min_c) for r,c in piece]

                        h = max(r for r,c in norm) + 1
                        w = max(c for r,c in norm) + 1

                        mat = [[0]*w for _ in range(h)]

                        for r,c in norm:
                            mat[r][c] = 1

                        # compare with tetromino dictionary
                        for name, rotations in TETROMINOS.items():
                            for i, rot in enumerate(rotations):
                                if mat == rot:
                                    return name, i, min_c
        return None

    def update_board_state(self, frame):
        for row in range(20):
            for col in range(10):

                px, py = self.sample_points[row][col]

                region = frame[py-2:py+3, px-2:px+3]

                b, g, r = region.mean(axis=(0,1))
                brightness = (b + g + r) / 3

                if brightness < 40 and b < 50 and g < 50 and r < 50:
                    self.board[row, col] = 0 
                else:
                    self.board[row, col] = 1

    def compute_sample_points(self, x, y, w, h):

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

class Agent:
    
    def __init__(self):
        self.logic_board = np.zeros((20,10))
        self.piece_active = False

    def update(self, board, piece):
        
        if piece is not None and not self.piece_active:
            self.piece_active = True
            self.correct_board_state(board)
            best_move = self.find_best_move(self.logic_board, piece[0])
            
            # Phase 1: only rotate
            rotation_moves = self.calculate_rotation(piece, best_move)
            self.pending_move = best_move  # remember target for phase 2
            self.rotating = True
            return rotation_moves

        if piece is not None and self.rotating:
            # Phase 2: piece has been re-detected after rotation, now move horizontally
            self.rotating = False
            return self.calculate_horizontal(piece, self.pending_move)

        if piece is None:
            self.piece_active = False
            self.rotating = False

        return None

    def correct_board_state(self, board):
        self.logic_board = board.copy()
        self.logic_board[0:4, :] = 0
        return self.logic_board

    def find_best_move(self, board, piece_name):

        best_score = -1e9
        best_move = None

        for i, rotation in enumerate(TETROMINOS[piece_name]):

            h = len(rotation)
            w = len(rotation[0])

            for col in range(10 - w + 1):

                row = 0

                # drop piece
                while not collision(board, rotation, row+1, col):
                    row += 1

                new_board, cleared = place_piece(board, rotation, row, col)

                score = evaluate_board(new_board, cleared)

                if score > best_score:
                    best_score = score
                    best_move = (i, col)

        return best_move

    def calculate_rotation(self, piece, best_move):
        piece_name, current_rot, current_col = piece
        target_rot, _ = best_move

        moves = []
        rotations_needed = (current_rot - target_rot) % len(TETROMINOS[piece_name])
        for _ in range(rotations_needed):
            moves.append(ROTATELEFT)

        return moves

    def calculate_horizontal(self, piece, best_move):
        piece_name, current_rot, current_col = piece  # current_col is now post-rotation
        _, target_col = best_move

        moves = []
        diff = target_col - current_col

        if diff > 0:
            for _ in range(diff):
                moves.append(MOVE_RIGHT)
        elif diff < 0:
            for _ in range(-diff):
                moves.append(MOVE_LEFT)

        moves.append(SNAP_DOWN)
        return moves

# para dimensiones a pantalla partida, prioducto de calibration
x = 697
y = 549
w = 172
h = 343
#preview = debug.draw_sample_points(frame.copy(), samplePoints) # para debug


print("Press S to start the bot")

env = Enviroment()
vision = AgentPerception(x,y,w,h)
agent = Agent()

while True:
    frame = env.get_frame()
    frame = cv2.resize(frame, None, fx = 0.25, fy = 0.25, interpolation=cv2.INTER_AREA)
    cv2.imshow("preview", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        print("Starting...")
        cv2.destroyAllWindows()
        break

#print(TETROMINOS["I"])
last_board = None

while True:

    # capturar frame
    frame = env.get_frame()

    # calcular el estado del tablero de juego
    vision.update_board_state(frame) 
    # print(vision.board)

    if last_board is None or not np.array_equal(vision.board, last_board):
        # print()
        last_board = vision.board.copy()

    # capturtar la pieza nueva que cae, si easta incompleta, retorna None
    piece = vision.get_falling_piece() 
    # print(piece)
    
    moves = agent.update(vision.board.copy(), piece)
    if moves:
        print("rotation phase")
        print(vision.board)
        debug.print_move_info(piece, agent.find_best_move(vision.board,piece[0]), moves)
        env.act(moves)

    frame=env.get_frame()
    vision.update_board_state(frame)
    piece = vision.get_falling_piece()
    moves = agent.update(vision.board.copy(), piece)
    if moves:
        print("Horizontal move phase")
        print(vision.board)
        debug.print_move_info(piece, agent.find_best_move(vision.board,piece[0]), moves)
        env.act(moves)

    preview = debug.draw_board_state(frame, vision.sample_points, vision.board)
    preview = cv2.resize(preview, None, fx = 0.25, fy = 0.25, interpolation=cv2.INTER_AREA)
    cv2.imshow("debug screen", preview)
    #print(board)
    if cv2.waitKey(1) == 27: # esc key
        env.camera.stop()
        cv2.destroyAllWindows()
        break

