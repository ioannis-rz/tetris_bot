import numpy as np
from TetrisDetection import env, vision, pieces  # adjust imports

# --- Heuristic functions ---

def simulate_drop(board, piece_shape, col):
    new_board = board.copy()
    r, c = piece_shape.shape
    
    landing_row = 0
    for row in range(board.shape[0] - r + 1):
        if np.any((new_board[row:row+r, col:col+c] + piece_shape) > 1):
            landing_row = row - 1
            break
    else:
        landing_row = board.shape[0] - r

    if landing_row < 0:
        return board, 0  # invalid placement

    new_board[landing_row:landing_row+r, col:col+c] |= piece_shape

    full_rows = np.all(new_board == 1, axis=1)
    cleared = full_rows.sum()
    new_board = new_board[~full_rows]
    empty_rows = np.zeros((cleared, board.shape[1]), dtype=board.dtype)
    new_board = np.vstack([empty_rows, new_board])

    return new_board, cleared

def aggregate_height(board):
    heights = []
    for c in range(board.shape[1]):
        col = board[:, c]
        heights.append(board.shape[0] - np.argmax(col) if col.any() else 0)
    return sum(heights)

def holes(board):
    total = 0
    for c in range(board.shape[1]):
        col = board[:, c]
        if col.any():
            top = np.argmax(col)
            total += (col[top:] == 0).sum()
    return total

def bumpiness(board):
    heights = [board.shape[0] - np.argmax(board[:, c]) if board[:, c].any() else 0
               for c in range(board.shape[1])]
    return sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))

def score_board(board, lines_cleared):
    return (
        +3.5  * lines_cleared
        -0.5  * aggregate_height(board)
        -0.36 * holes(board)
        -0.18 * bumpiness(board)
    )

def decide(board, piece, pieces_dict):
    best_score = -np.inf
    best_move = None

    for rot_idx, shape in enumerate(pieces_dict[piece['name']]):
        for col in range(board.shape[1] - shape.shape[1] + 1):
            new_board, lines = simulate_drop(board, shape, col)
            score = score_board(new_board, lines)
            if score > best_score:
                best_score = score
                best_move = {'rotation': rot_idx, 'col': col, 'score': score}

    return best_move

# --- Single frame test ---

frame = env.get_frame()
vision.update_board_state(frame)
piece = vision.get_falling_piece()

print("Board:")
print(vision.board)
print()
print("Piece:", piece)
print()

if piece is not None:
    move = decide(vision.board, piece, pieces)
    print("Best move:", move)
    print(f"  → rotate to rotation {move['rotation']}")
    col_diff = move['col'] - piece['col']
    direction = "right" if col_diff > 0 else "left"
    print(f"  → move {abs(col_diff)} steps {direction} (col {piece['col']} → {move['col']})")
else:
    print("No piece detected yet")