import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from TetrisDetection import (
    Agent,
    TETROMINOS,
    MOVE_RIGHT,
    MOVE_LEFT,
    SNAP_DOWN,
    ROTATELEFT,
    collision,
    place_piece,
    evaluate_board,
    count_holes,
    get_column_heights,
    get_bumpiness,
    clear_lines,
)

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def empty_board():
    return np.zeros((20, 10))

def board_with_rows(filled_rows):
    """Return a board with specific rows completely filled."""
    b = empty_board()
    for r in filled_rows:
        b[r, :] = 1
    return b

def board_with_cols(col_heights):
    """Return a board filled from the bottom up per column."""
    b = empty_board()
    for col, h in enumerate(col_heights):
        for row in range(20 - h, 20):
            b[row, col] = 1
    return b

agent = Agent()

# ──────────────────────────────────────────────
# calculate_moves
# ──────────────────────────────────────────────

class TestCalculateMoves:

    def test_no_rotation_no_movement(self):
        """Piece already in target rotation and column — only SNAP_DOWN expected."""
        piece = ("O", 0, 4)
        best_move = (0, 4)
        moves = agent.calculate_moves(piece, best_move)
        assert moves == [SNAP_DOWN]

    def test_move_right(self):
        piece = ("O", 0, 3)
        best_move = (0, 6)
        moves = agent.calculate_moves(piece, best_move)
        assert moves.count(MOVE_RIGHT) == 3
        assert MOVE_LEFT not in moves
        assert moves[-1] == SNAP_DOWN

    def test_move_left(self):
        piece = ("O", 0, 7)
        best_move = (0, 4)
        moves = agent.calculate_moves(piece, best_move)
        assert moves.count(MOVE_LEFT) == 3
        assert MOVE_RIGHT not in moves
        assert moves[-1] == SNAP_DOWN

    def test_rotation_only(self):
        """T piece at rot 0, target rot 2 → 2 left rotations, no horizontal."""
        piece = ("T", 0, 4)
        best_move = (2, 4)
        moves = agent.calculate_moves(piece, best_move)
        assert moves.count(ROTATELEFT) == 2
        assert MOVE_RIGHT not in moves
        assert MOVE_LEFT not in moves
        assert moves[-1] == SNAP_DOWN

    def test_rotation_wraps_correctly(self):
        """T has 4 rotations. Going from rot 3 to rot 0 needs 1 left rotation."""
        piece = ("T", 3, 4)
        best_move = (0, 4)
        moves = agent.calculate_moves(piece, best_move)
        assert moves.count(ROTATELEFT) == 1

    def test_rotation_and_movement_combined(self):
        piece = ("L", 0, 2)
        best_move = (2, 7)
        moves = agent.calculate_moves(piece, best_move)
        assert ROTATELEFT in moves
        assert moves.count(MOVE_RIGHT) == 5
        assert moves[-1] == SNAP_DOWN

    def test_snap_down_always_last(self):
        for piece_name in TETROMINOS:
            piece = (piece_name, 0, 0)
            best_move = (0, 0)
            moves = agent.calculate_moves(piece, best_move)
            assert moves[-1] == SNAP_DOWN, f"SNAP_DOWN not last for {piece_name}"

    def test_i_piece_no_extra_rotation(self):
        """I has only 2 rotations; going 0→0 needs 0 rotations."""
        piece = ("I", 0, 4)
        best_move = (0, 4)
        moves = agent.calculate_moves(piece, best_move)
        assert ROTATELEFT not in moves

    def test_s_piece_rotation(self):
        """S has 2 rotations; going from 0 to 1 needs 1 left rotation."""
        piece = ("S", 0, 4)
        best_move = (1, 4)
        moves = agent.calculate_moves(piece, best_move)
        assert moves.count(ROTATELEFT) == 1


# ──────────────────────────────────────────────
# find_best_move
# ──────────────────────────────────────────────

class TestFindBestMove:

    def test_returns_tuple(self):
        board = empty_board()
        result = agent.find_best_move(board, "O")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_target_col_in_valid_range(self):
        """Target column must be reachable for each piece width."""
        board = empty_board()
        for piece_name in TETROMINOS:
            rot, col = agent.find_best_move(board, piece_name)
            w = len(TETROMINOS[piece_name][rot][0])
            assert 0 <= col <= 10 - w, (
                f"{piece_name} rot {rot}: col {col} out of range for width {w}"
            )

    def test_target_rotation_valid(self):
        board = empty_board()
        for piece_name in TETROMINOS:
            rot, _ = agent.find_best_move(board, piece_name)
            assert 0 <= rot < len(TETROMINOS[piece_name])

    def test_prefers_line_clear(self):
        """
        Fill rows 17-19, columns 0-8 (leaving col 9 empty).
        An I piece dropped vertically in col 9 should clear 4 lines — 
        the agent should prefer that move.
        """
        board = empty_board()
        for row in range(17, 20):
            board[row, 0:9] = 1

        rot, col = agent.find_best_move(board, "I")
        assert col == 9, f"Expected col 9 for line clear, got {col}"
        assert rot == 1, f"Expected vertical rotation (1) for I piece, got {rot}"

    def test_avoids_creating_holes(self):
        """
        On an empty board the agent should not stack pieces in a way that
        obviously creates holes; aggregate hole count after best placement
        should be 0.
        """
        board = empty_board()
        rot, col = agent.find_best_move(board, "O")
        # simulate drop
        piece = TETROMINOS["O"][rot]
        row = 0
        while not collision(board, piece, row + 1, col):
            row += 1
        new_board, _ = place_piece(board, piece, row, col)
        from main import count_holes
        assert count_holes(new_board) == 0

    def test_score_improves_with_line_clear(self):
        """evaluate_board should give a higher score when lines are cleared."""
        board = empty_board()
        score_no_clear = evaluate_board(board, cleared=0)
        score_with_clear = evaluate_board(board, cleared=2)
        assert score_with_clear > score_no_clear

    def test_all_pieces_return_a_move(self):
        board = empty_board()
        for piece_name in TETROMINOS:
            result = agent.find_best_move(board, piece_name)
            assert result is not None, f"find_best_move returned None for {piece_name}"


# ──────────────────────────────────────────────
# Supporting logic sanity checks
# ──────────────────────────────────────────────

class TestBoardHelpers:

    def test_clear_full_row(self):
        board = board_with_rows([19])
        board, cleared = clear_lines(board)
        assert cleared == 1
        assert not board[19].all()

    def test_no_clear_partial_row(self):
        board = empty_board()
        board[19, 0:9] = 1
        _, cleared = clear_lines(board)
        assert cleared == 0

    def test_count_holes_simple(self):
        board = empty_board()
        board[0, 0] = 1   # block at top of col 0
        board[2, 0] = 1   # gap at row 1 = 1 hole
        assert count_holes(board) == 1

    def test_get_column_heights(self):
        board = empty_board()
        board[18, 0] = 1
        board[19, 0] = 1
        heights = get_column_heights(board)
        assert heights[0] == 2

    def test_bumpiness_flat(self):
        heights = [5] * 10
        assert get_bumpiness(heights) == 0

    def test_collision_out_of_bounds(self):
        board = empty_board()
        piece = TETROMINOS["O"][0]
        assert collision(board, piece, 19, 0)   # bottom overflow
        assert collision(board, piece, 0, 9)    # right overflow
        assert collision(board, piece, 0, -1)   # left overflow

    def test_place_piece_marks_cells(self):
        board = empty_board()
        piece = TETROMINOS["O"][0]
        new_board, _ = place_piece(board, piece, 18, 4)
        assert new_board[18, 4] == 1
        assert new_board[18, 5] == 1
        assert new_board[19, 4] == 1
        assert new_board[19, 5] == 1
