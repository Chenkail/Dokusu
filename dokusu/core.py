import numpy as np

from rules import *


class Sudoku:

    def __init__(self, board, possibilities=None, rules=None):
        self.board_size = board.shape[0]
        self.block_size = int(np.sqrt(self.board_size)) 
        self.start_board = board.copy()
        self.board = board.copy()
        if possibilities is None:
            self.possibilities = np.ones(
                    (self.board_size, self.board_size, self.board_size), dtype=bool)
        else:
            self.possibilities = possibilities

        if rules is None:
            self.rules = Sudoku.base_rules(self.board_size, self.block_size)
        else:
            self.rules = rules

    @staticmethod
    def base_rules(board_size, block_size):
        def select_box(block):
            x, y = block%block_size, block//block_size
            return slice(block_size*y, block_size*(y+1)), slice(block_size*x, block_size*(x+1))
        return [
            SingleRule()
        ] + [
            UniqueRule(row) for row in range(board_size)
        ] + [
            UniqueRule((slice(None), col)) for col in range(board_size)
        ] + [
            UniqueRule(select_box(box)) for box in range(board_size)
        ]

    @staticmethod
    def from_file(path):
        """
        Read a sudoku puzzle from a file
        """

        # TODO: (possibly) implement more comprehensive file loading (multiple filetypes?)
        f = open(path)
        lines = f.readlines()
        f.close()

        lines = filter(lambda line: line.strip() != '#' and len(line.strip()) > 0, lines)

        def remap(s):
            s = s.strip().lower()
            if s.isnumeric():
                return int(s)
            elif len(s) == 1 and 'a' <= s <= 'z':
                return ord(s) - ord('a') + 10
            else:
                raise Exception(f"couldn't figure out what '{s}' is")

        rows = [list(map(remap, line.split(','))) for line in lines]
        return Sudoku(np.array(rows, dtype=np.uint8))
    
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

    @staticmethod
    def sample16():
        return Sudoku.from_file('./sample_puzzles/sample16.csv')

    def copy(self):
        return Sudoku(
            self.board.copy(),
            self.possibilities.copy(),
            self.rules,
        )

    def solve(self, log_guessing=False, log_indent=""):
        """
        Solve the current sudoku puzzle.

        Returns:
            np.ndarray of shape (N, N) representing the solution or None if no solution found
        """
        
        stuck = False
        while not stuck:
            pre_reduction = self.possibilities.copy()
            self.possibilities = self.possibilities_reduction()

            self.board = self.find_solvable()

            if self.board_done():
                if self.board_valid():
                    return self.board
                else:
                    return None
            
            # stuck when possibilities didn't change
            stuck = (pre_reduction == self.possibilities).all()

        cell, possible_values = self.pick_guess()

        # try all the possible values for the guess cell
        for value in possible_values:
            if log_guessing:
                print(f'{log_indent}guessing {value} for {cell}')

            guess_sudoku = self.copy()
            guess_sudoku.board[cell] = value

            result = guess_sudoku.solve(log_guessing, log_indent+" ")
            if result is not None:
                self.board = guess_sudoku.board
                self.possibilities = guess_sudoku.possibilities
                return result
            
            self.possibilities[(*cell, value-1)] = False
        
        return None

    def pick_guess(self):
        """
        Pick a cell to guess for when we run out of steam with the base algorithm.

        Returns:
            (cell, possible_values)
            where `cell` is an (i, j) tuple and `possible_values` is a list of values that cell
            could potentially have.
        """
        # pick cell with least possible options
        cell_options_counts = self.possibilities.sum(axis=2)
        relevant_cells = np.argwhere(cell_options_counts > 1)

        # if there's no options for a cell, we broke the puzzle
        if cell_options_counts.min() == 0:
            return None, []

        min_index = cell_options_counts[(*relevant_cells.T, )].argmin()
        cell = tuple(relevant_cells[min_index])
        possible_values = np.argwhere(self.possibilities[cell]).flatten() + 1

        return cell, possible_values
    

    def find_solvable(self):
        """
        Given a set of the possible values for each cell, convert that to a board of definitely
        known cell values based on a set of rules.

        Returns:
            np.ndarray of shape (N, N)
        """

        for rule in self.rules:
            rule.find_solvable(self)

        return self.board


    def board_done(self):
        """
        Check if every square in the board is filled
        """
        return self.board.min() > 0

    def board_valid(self):
        """
        Check whether or not the current board state is a valid solution.

        Theoretically, it could be done with a simple check on `self.possibilities`, but
        then this method wouldn't be able to catch any issues with it.
        """
        if not self.board_done():
            return False

        for rule in self.rules:
            if not rule.verify(sudoku):
                print(f'failed rule {rule}')
                return False

        return True

        numbers = np.arange(1, self.board_size+1)

        # TODO: Same as in `find_solvable`, these three sections can definitely be combined
        for row_i in range(self.board_size):
            row = self.board[row_i]
            values, counts = np.unique(row, return_counts=True)
            if (values.tolist() != numbers.tolist()) or (counts != 1).any():
                return False

        for col_i in range(self.board_size):
            col = self.board[row_i]
            values, counts = np.unique(col, return_counts=True)
            if (values.tolist() != numbers.tolist()) or (counts != 1).any():
                return False

        groups = []
        for i in range(self.block_size):
            groups.append(slice(i*self.block_size, (i+1)*self.block_size))

        for group_i in groups:
            for group_j in groups:
                box = self.board[group_i, group_j]
                values, counts = np.unique(box, return_counts=True)
                if (values.tolist() != numbers.tolist()) or (counts != 1).any():
                    return False

        return True
    
    def possibilities_reduction(self):
        """
        Filter down all the possibilities for each cell based on sudoku rules.

        Returns:
            reduced copy of self.possibilities
        """

        for rule in self.rules:
            rule.reduce_possibilities(self)

        return self.possibilities


sudoku = Sudoku.sample()

def main():
    
    sudoku = Sudoku.sample()
    # sudoku = Sudoku.from_numpy(<np array here>)

    solved = sudoku.solve()

    print(solved) # np array (9, 9)
    pass


if __name__ == "__main__":
    main()
