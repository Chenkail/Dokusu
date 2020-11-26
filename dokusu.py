from pathlib import Path
import numpy as np


class Sudoku:

    def __init__(self, board):
        self.board = board

    @staticmethod
    def from_file(path):
        pass
    
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

        board_possibilities = np.ones(9, 9, 9)

        return Sudoku.recursive_solving(board, board_possibilities)

    @staticmethod
    def recursive_solving(board, possibilities):
        stuck = False
        while not stuck:
            pre_reduction = possibilities.copy()
            possibilities = Sudoku.possibilities_reduction(board, possibilities)

            # TODO:
            # find solvable cells (i.e. only cell in 3x3 that can have a "1")
            # update board/possibilities based on that

            if Sudoku.board_done(board):
                if Sudoku.board_valid(board):
                    return board
                else:
                    return None
            
            # possiblitities didn't change
            stuck = (pre_reduction == possibilities).all()

        # pick cell with least possible options
        cell_options_counts = possibilities.sum(axis=2)
        relevant_cells = np.argwhere(cell_options_counts > 1)
        min_index = cell_options_counts[(*relevant_cells.T, )].argmin()
        cell = relevant_cells[min_index]
        
        possible_values = np.argwhere(possibilities[cell]).flatten() + 1
        for value in possible_values:
            new_board = board.copy()
            new_possibilities = possibilities.copy()

            new_board[cell] = value

            result = Sudoku.recursive_solving(new_board, new_possibilities)
            if result is not None:
                return result
            
            # possibilities[(*cell, value-1)] = False
        
        return None

        """
        for cell in np.argwhere(board == 0):
            possible_values = np.argwhere(possibilities[cell]).flatten() + 1
            
            for value in possible_values:
                new_board = board.copy()
                new_possibilities = possibilities.copy()

                new_board[cell] = value

                result = Sudoku.recursive_solving(new_board, new_possibilities)
                if result is not None:
                    return result
                
                possibilities[(*cell, value-1)] = False
        """


    @staticmethod
    def board_done(board):
        

        
        return False

    @staticmethod
    def board_valid(board):
        # TODO:
        return False
    
    @staticmethod
    def possibilities_reduction(board, board_possibilities):
        # for all the non-zero cells,
        for y, x in np.argwhere(board != 0):
            value = board[y, x]

            # remove that cell's value from 3x3 block options
            g_x = x // 3 # group x [0 - 2]
            g_y = y // 3 # group y [0 - 2]
            board_possibilities[g_y:g_y+3, g_x:g_x+3, value-1] = False

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