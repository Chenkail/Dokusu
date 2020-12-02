import math
from pathlib import Path

import numpy as np


class Sudoku:

    def __init__(self, board):
        self.board = board

    @staticmethod
    def from_file(path):
        # TODO: implement more comprehensive file loading
        board = np.genfromtxt(path, delimiter=',', dtype=int)
        return Sudoku(board)
    
    @staticmethod
    def sample():
        board = np.array([
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ], dtype=np.uint8)
        return Sudoku(board)

    def solve(self) -> np.ndarray:
        board = self.board.copy()
        board_size = board.shape[0]

        board_possibilities = np.ones((board_size, board_size, board_size), dtype=bool)

        return Sudoku.recursive_solving(board, board_possibilities)

    @staticmethod
    def recursive_solving(board, possibilities, indent=""):
        board_size = board.shape[0]
        
        stuck = False
        while not stuck:
            pre_reduction = possibilities.copy()
            possibilities = Sudoku.possibilities_reduction(board, possibilities)

            # TODO:
            # find solvable cells (i.e. only cell in 3x3 that can have a "1")
            # update board/possibilities based on that

            board = Sudoku.find_solvable(possibilities)

            if Sudoku.board_done(board):
                if Sudoku.board_valid(board):
                    return board
                else:
                    return None
            
            # possiblitities didn't change
            stuck = (pre_reduction == possibilities).all()

        possibilities = np.ones((board_size, board_size, board_size), dtype=bool)
        possibilities = Sudoku.possibilities_reduction(board, possibilities)
        # pick cell with least possible options
        cell_options_counts = possibilities.sum(axis=2)
        relevant_cells = np.argwhere(cell_options_counts > 1)

        # if there's no options for a cell, we broke the puzzle
        if cell_options_counts.min() == 0:
            return None

        try:
            min_index = cell_options_counts[(*relevant_cells.T, )].argmin()
        except:
            print('that one error')
            return None
        cell = tuple(relevant_cells[min_index])

        possible_values = np.argwhere(possibilities[cell]).flatten() + 1
        for value in possible_values:
            new_board = board.copy()
            new_possibilities = possibilities.copy()

            new_board[cell] = value

            result = Sudoku.recursive_solving(new_board, new_possibilities, indent+"")
            if result is not None:
                return result
            
            possibilities[(*cell, value-1)] = False
        
        return None

    @staticmethod
    def find_solvable(possibilities):
        """
        Given a set of the possible values for each cell, convert that to a board of definitely
        known cell values based on a set of rules.
        """

        board_size = possibilities.shape[0]
        block_size = int(math.sqrt(board_size))

        cell_options_counts = possibilities.sum(axis=2)

        # Cells with only one option
        board = np.where(cell_options_counts == 1, possibilities.argmax(axis=2), -1)

        # TODO: find a nice way to do this with numpy stuff

        # TODO: these 3 parts could be converted into one with a list [*rows, *columns, *boxes]
        for row_i in range(board_size):
            row = possibilities[row_i]
            # (count of X, )
            row_counts = row.sum(axis=0)
            for X in np.argwhere(row_counts == 1).flatten():
                location = np.nonzero(row[:, X])
                board[row_i][location] = X

        for col_i in range(board_size):
            col = possibilities[:, col_i]
            # (count of X, )
            col_counts = col.sum(axis=0)
            for X in np.argwhere(col_counts == 1).flatten():
                location = np.nonzero(col[:, X])
                board[:, col_i][location] = X

        # TODO: REFACTOR
        groups = []
        for i in range(block_size):
            groups.append(slice(i*block_size, (i+1)*block_size))
        # groups = [slice(0,3), slice(3,6), slice(6,9)]
        for group_i in groups:
            for group_j in groups:
                box = possibilities[(group_i, group_j)]
                # (count of X, )
                box_counts = box.sum(axis=(0,1))
                for X in np.argwhere(box_counts == 1).flatten():
                    location = np.nonzero(box[:, :, X])
                    board[(group_i, group_j)][location] = X

        return board + 1


    @staticmethod
    def board_done(board):
        return board.min() > 0

    @staticmethod
    def board_valid(board):
        board_size = board.shape[0]
        block_size = int(math.sqrt(board_size))

        if not Sudoku.board_done(board):
            return False

        numbers = np.arange(1, board_size+1)

        for row_i in range(board_size):
            row = board[row_i]
            values, counts = np.unique(row, return_counts=True)
            if (values.tolist() != numbers.tolist()) or (counts != 1).any():
                return False

        for col_i in range(board_size):
            col = board[row_i]
            values, counts = np.unique(col, return_counts=True)
            if (values.tolist() != numbers.tolist()) or (counts != 1).any():
                return False

        # TODO: REFACTOR
        groups = []
        for i in range(block_size):
            groups.append(slice(i*block_size, (i+1)*block_size))
        # groups = [slice(0,3), slice(3,6), slice(6,9)]


        for group_i in groups:
            for group_j in groups:
                box = board[group_i, group_j]
                values, counts = np.unique(box, return_counts=True)
                if (values.tolist() != numbers.tolist()) or (counts != 1).any():
                    return False

        return True
    
    @staticmethod
    def possibilities_reduction(board, board_possibilities):
        board_size = board.shape[0]
        block_size = int(math.sqrt(board_size)) 
        
        # for all the non-zero cells,
        for y, x in np.argwhere(board != 0):
            value = board[y, x]

            # remove that cell's value from NxN block options
            g_x = (x // block_size)*block_size # group x [0 - 2]
            g_y = (y // block_size)*block_size # group y [0 - 2]
            board_possibilities[g_y:g_y+block_size, g_x:g_x+block_size, value-1] = False

            # remove that cell's value from row options
            board_possibilities[y, :, value-1] = False

            # remove that cell's value from col options
            board_possibilities[:, x, value-1] = False

            # that cell's options are only that value
            board_possibilities[y, x] = False
            board_possibilities[y, x, value-1] = True

        return board_possibilities


def main():
    """
    docstring
    """
    
    sudoku = Sudoku.sample()
    # sudoku = Sudoku.from_numpy(<np array here>)

    solved = sudoku.solve()

    print(solved) # np array (9, 9)


if __name__ == "__main__":
    main()
