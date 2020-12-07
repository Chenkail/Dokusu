import numpy as np

class Rule:
    def reduce_possibilities(self, sudoku):
        raise NotImplementedError

    def find_solvable(self, sudoku):
        pass

    def verify(self, sudoku):
        raise NotImplementedError

class UniqueRule(Rule):
    def __init__(self, indices):
        self.indices = indices

    def reduce_possibilities(self, sudoku):
        board_subset = sudoku.board[self.indices]
        possibilities_subset = sudoku.possibilities[self.indices]

        # disable possibilities [at empty cells] [for existing values]
        board_indices = np.nonzero(board_subset == 0)

        # indices of possibilities (dim=1) to filter out
        to_remove = board_subset[board_subset != 0] - 1

        for remove_possibility in to_remove:
            possibilities_subset[(*board_indices, remove_possibility)] = False

    def find_solvable(self, sudoku):
        #board = sudoku.board.copy()
        # (3=row, 3=col)
        b_subset = sudoku.board[self.indices]
        # (3=row, 3=col, N=possibilities)
        p_subset = sudoku.possibilities[self.indices]

        axes = tuple(range(len(b_subset.shape)))
        counts = p_subset.sum(axis=axes)

        slices = tuple(slice(None) for _ in axes)
        for X in np.argwhere(counts == 1).flatten():
            location = np.nonzero(p_subset[(*slices, X)])
            sudoku.board[self.indices][location] = X + 1

    def verify(self, sudoku):
        target = set(range(sudoku.board_size))
        actual = set(sudoku.board[self.indices].flatten() + 1)
        return target != actual

    def __repr__(self):
        return f'UniqueRule: {self.indices}'


class SingleRule(Rule):
    def reduce_possibilities(self, sudoku):
        nonzero_cells = sudoku.board != 0
        nonzero_cell_values = sudoku.board[nonzero_cells]
        indices = nonzero_cell_values - 1
        before = sudoku.possibilities[nonzero_cells, indices]
        sudoku.possibilities[nonzero_cells] = False
        sudoku.possibilities[nonzero_cells, indices] = before

    def find_solvable(self, sudoku):
        counts = sudoku.possibilities.sum(axis=-1)
        sudoku.board = np.where(counts == 1, sudoku.possibilities.argmax(axis=-1)+1, sudoku.board)

    def verify(self, sudoku):
        return True
        
class AntiKnightRule(Rule):
    # TODO: anti-knight can probably be done by offsetting the entire board at once or something

    KNIGHT_MOVES = np.array([
        [1, 2],
        [1, -2],
        [-1, 2],
        [-1, -2],
        [2, 1],
        [2, -1],
        [-2, 1],
        [-2, -1],
    ])

    def reduce_possibilities(self, sudoku):
        rows, cols = sudoku.board.shape
        for cell in np.argwhere(sudoku.board != 0):
            value = sudoku.board[tuple(cell)]
            for move in self.KNIGHT_MOVES:
                i, j = cell + move
                if 0 <= i < rows and 0 <= j < cols:
                    sudoku.possibilities[i, j, value-1] = False

    def find_solvable(self, sudoku):
        pass

    def verify(self, sudoku):
        rows, cols = sudoku.board.shape
        for cell in np.argwhere(sudoku.board != 0):
            value = sudoku.board[tuple(cell)]
            for move in self.KNIGHT_MOVES:
                i, j = cell + move
                if 0 <= i < rows and 0 <= j < cols and sudoku.board[i, j] == value:
                    return False
        return True