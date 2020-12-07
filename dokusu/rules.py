import numpy as np

class Rule:
    def reduce_possibilities(self, sudoku):
        raise NotImplementedError

    def find_solvable(self, sudoku):
        pass

    def verify(self, sudoku):
        raise NotImplementedError

class UniqueRule(Rule):
    def __init__(self, slice=None, indices=None, strong=True):
        self.slice = slice
        self.indices = np.array(indices)
        self.indicesT = None

        self.subset = self.slice
        if indices is not None:
            self.indicesT = tuple(np.array(indices).T)
            self.subset = self.indicesT

        self.strong = strong


    def reduce_possibilities(self, sudoku):
        board_subset = sudoku.board[self.subset]
        possibilities_subset = sudoku.possibilities[self.subset]

        # disable possibilities [at empty cells] [for existing values]
        board_indices = np.nonzero(board_subset == 0)

        # indices of possibilities (dim=1) to filter out
        to_remove = board_subset[board_subset != 0] - 1

        for remove_possibility in to_remove:
            if self.slice is not None:
                possibilities_subset[(*board_indices, remove_possibility)] = False
            else:
                sudoku.possibilities[(*self.indices[board_indices].T, remove_possibility)] = False


    def find_solvable(self, sudoku):
        if not self.strong:
            return
        #board = sudoku.board.copy()
        # (3=row, 3=col)
        b_subset = sudoku.board[self.subset]
        # (3=row, 3=col, N=possibilities)
        p_subset = sudoku.possibilities[self.subset]

        axes = tuple(range(len(b_subset.shape)))
        counts = p_subset.sum(axis=axes)

        slices = tuple(slice(None) for _ in axes)
        for X in np.argwhere(counts == 1).flatten():
            location = np.nonzero(p_subset[(*slices, X)])
            sudoku.board[self.subset][location] = X + 1

    def verify(self, sudoku):
        if self.strong:
            target = set(range(sudoku.board_size))
            actual = set(sudoku.board[self.subset].flatten() + 1)
            return target != actual
        else:
            flat = sudoku.board[self.subset].flatten()
            return len(set(flat)) == len(flat)

    def __repr__(self):
        return f'UniqueRule: {self.subset}'


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

    KNIGHT_MOVES = np.array([
        [1, 2], [1, -2], [-1, 2], [-1, -2],
        [2, 1], [2, -1], [-2, 1], [-2, -1],
    ])

    def reduce_possibilities(self, sudoku):
        for move in self.KNIGHT_MOVES:
            b_subset = AntiKnightRule.move_slice_subset(move, sudoku.board)
            p_subset = AntiKnightRule.move_slice_subset(-move, sudoku.possibilities)

            cells_i, cells_j = np.nonzero(b_subset)
            values = b_subset[cells_i, cells_j]
            p_subset[cells_i, cells_j, values-1] = False

    @staticmethod
    def move_slice_subset(move, array):
        di, dj = move
        slice_i = slice(di, None) if di > 0 else slice(None, di)
        slice_j = slice(dj, None) if dj > 0 else slice(None, dj)
        return array[slice_i, slice_j]

    def verify(self, sudoku):
        for move in self.KNIGHT_MOVES:
            subset_a = AntiKnightRule.move_slice_subset(move, sudoku.board)
            subset_b = AntiKnightRule.move_slice_subset(-move, sudoku.board)

            if ((subset_a != 0) & (subset_b != 0) & (subset_a == subset_b)).any():
                return False
        return True


