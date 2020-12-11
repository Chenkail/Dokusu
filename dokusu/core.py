import os
from pathlib import Path

import numpy as np

from . import rules
from .rules import *

DOKUSU_DIR = Path(__file__).parent.parent
CURRENT_DIR = Path().absolute()
EXPORT_DIR = CURRENT_DIR / "exports"
if not os.path.isdir(EXPORT_DIR):
    os.mkdir(EXPORT_DIR)

class Sudoku:
    """
    A sudoku puzzle, with any (N^2, N^2) shape or any rule sets.
    """

    def __init__(self, board:np.ndarray, possibilities:np.ndarray=None, rules:list=None):
        """
        Initialize a new Sudoku puzzle given an numpy array as the board.

        Args:
            board:np.ndarray         -- The (N^2, N^2) shape board to initialize with
            possibilities:np.ndarray -- (optional) possibilities to set at the start
                                        (default: (N^2, N^2, N^2) shape ndarray of all True)
            rules:list               -- (optional) rules to use for solving this sudoku
                                        (default: standard sudoku rules)
        """

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
            # TODO: create a `BaseSudokuRule` Rule that contains all the base rules
            self.rules = Sudoku.base_rules(self.board_size, self.block_size)
        else:
            self.rules = rules


    @staticmethod
    def base_rules(board_size:int, block_size:int):
        """
        Returns valid rules for a basic N^2xN^2 game of Sudoku

        Args:
            board_size:int -- The size of the board. For normal sudoku, this is 9
            block_size:int -- The size of a sudoku block. For normal sudoku, this is 3
        """

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
    def from_file(path:str):
        """
        Load a sudoku puzzle from a file

        Args:
            path:str -- The path to the file to load from
        
        Returns:
            A sudoku instance created from that file
        """

        # TODO: Add import for exported files
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
        """
        Built-in sample sudoku

        Returns:
            A sample sudoku instance
        """

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
        """
        load a sample 16x16 puzzle
        """
        return Sudoku.from_file('./sample_puzzles/sample16.csv')

    def copy(self):
        """
        Creates a copy of a Sudoku object by duplicating the board, 
        possibilities, and rules
        """

        return Sudoku(
            self.board.copy(),
            self.possibilities.copy(),
            self.rules,
        )

    def reset(self):
        """
        Reset the board and possibilities to be like they were when this sudoku was created
        """

        self.possibilities = np.ones(
                (self.board_size, self.board_size, self.board_size), dtype=bool)
        self.board = self.start_board


    def solve(self, log_guessing:bool=False, log_indent:str="",
              extended_depth:int=0, on_cell_update=None):
        """
        Solve the current sudoku puzzle.

        Args:
            log_guessing:bool  -- Should all guesses be logged? (default: False)
            log_indent:str     -- Current indentation level for guess logging. Only used
                                  internally, can be safely ignored.
            extended_depth:int -- Guess depth to use extended reduction for. 0 is best for
                                  standard sudoku, while 1 or 2 works well for difficult
                                  variants. (default: 0)
            on_cell_update:    -- Method to call whenever a cell is updated. See
                                  'Animating the Solver' in docs for usage details

        Returns:
            self if a solution was found or None if no solution found
        """
        
        solved = self.solve_until_stuck(on_cell_update, extended=False)
        if solved:
            return self

        if not self.board_valid():
            return None
        if self.board_done():
            self.full_redraw(on_cell_update)
            return self

        while True:
            solved = self.solve_until_stuck(on_cell_update, extended=(extended_depth>0))
            if solved:
                return self

            if not self.board_valid():
                return None
            if self.board_done():
                self.full_redraw(on_cell_update)
                return self

            # at this point, we're stuck and need a guess

            restriction = self.calculate_restriction()

            guess = self.pick_guess()
            result = self.take_guess(guess, log_guessing, log_indent+' ', extended_depth-1,
                                     on_cell_update)

            if result is not None:
                self.board = result.board
                self.possibilities = result.possibilities
                self.full_redraw(on_cell_update)
                return result
            
            self.possibilities[guess] = False
            if self.possibilities[guess[:2]].max() == False:
                return None

            self.full_redraw(on_cell_update)
        
        return None

    def solve_until_stuck(self, on_cell_update, extended=False):
        """
        Tries to solve the sudoku puzzle until it gets stuck

        Args:
            on_cell_update -- Method to call whenever a cell is updated. See
                              'Animating the Solver' in docs for usage details
            extended:bool  -- Flag controlling extended reduction usage.

        Returns:
            False if it got stuck/failed, True if it found a solution
        """
        
        stuck = False
        while not stuck:
            stuck = self.solve_step(on_cell_update, extended=extended)

            if not self.board_valid():
                return False
            if self.board_done():
                self.full_redraw(on_cell_update)
                return True

        return False


    def solve_step(self, on_cell_update=None, extended=False):
        """
        Tries to solve the sudoku puzzle until it gets stuck

        Args:
            on_cell_update -- Method to call whenever a cell is updated. See
                              'Animating the Solver' in docs for usage details
            extended:bool  -- Flag controlling extended reduction usage.

        Returns:
            Is it stuck?

            True if stuck, False if it isn't stuck
        """

        pre_possibilities = self.possibilities.copy()
        self.possibilities_reduction(extended=extended)
        if on_cell_update is not None:
            for pos in np.argwhere((self.board == 0) & 
                    (self.possibilities != pre_possibilities).max(-1)):
                on_cell_update(self, pos)

        pre_board = self.board.copy()
        self.board = self.find_solvable()
        if on_cell_update is not None:
            for pos in np.argwhere(self.board != pre_board):
                on_cell_update(self, pos)

        return (pre_possibilities == self.possibilities).all()


    def full_redraw(self, on_cell_update=None):
        """
        'Update' every cell in the board to reset it to the current state of the board.
        """
        if on_cell_update is not None:
            for pos in np.argwhere(self.board > -1):
                on_cell_update(self, pos)

    
    def calculate_restriction(self):
        """
        Calculate how restricted each possibility is.

        Returns:
            (N, N, N) np.ndarray of per-possibility restriction estimates
        """
        restriction = np.zeros_like(self.possibilities, dtype=float)
        for rule in self.rules:
            rule.restriction_estimate(self, restriction)

        restriction += np.random.rand(*restriction.shape) * 0.01 # slight randomness
        restriction *= self.possibilities * (self.board == 0).reshape(9, 9, 1)
        return restriction


    def pick_guess(self):
        """
        Pick a cell to guess for when we run out of steam with the base algorithm.

        Returns:
            3-tuple representing the possibility to guess.
        """

        restriction = self.calculate_restriction()
        return np.unravel_index(restriction.ravel().argmax(), restriction.shape)

    def take_guess(self, guess, log_guessing=False, log_indent="",
                   extended_depth=0, on_cell_update=None):
        """
        Solve the sudoku with an assumed square.
        """

        i, j, p_index = guess
        if log_guessing:
            print(f'{log_indent}guess: {p_index+1} at {(i, j)}')
    
        guess_sudoku = self.copy()
        guess_sudoku.board[i, j] = p_index + 1

        if on_cell_update is not None:
            on_cell_update(guess_sudoku, (i, j), guess=True)

        result = guess_sudoku.solve(log_guessing, log_indent+" ", extended_depth, 
                                    on_cell_update)

        return result
    

    def find_solvable(self):
        """
        Given a set of the possible values for each cell, convert that to a 
        board of definitely known cell values based on a set of rules.

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

    def board_valid(self, verbose=False):
        """
        Check whether or not the current board state is a valid solution.

        Theoretically, it could be done with a simple check on `self.possibilities`, but
        then this method wouldn't be able to catch any issues with it.
        """

        for rule in self.rules:
            if not rule.verify(self):
                if verbose:
                    print(f'failed rule {rule}')
                return False

        return True
    
    def possibilities_reduction(self, extended=False):
        """
        Filter down all the possibilities for each cell based on sudoku rules.

        Returns:
            reduced copy of self.possibilities
        """

        for rule in self.rules:
            rule.reduce_possibilities(self, extended=extended)

        return self.possibilities

    def __repr__(self):
        split_parts = self.board_size // self.block_size

        def cell_repr(value):
            if value == 0:
                return '□'
            if value > 9:
                return chr(ord('A') - 10 + value)
            return str(value)

        def cell_block_repr(cell_block):
            return ' '.join(cell_repr(value) for value in cell_block)

        def row_repr(row):
            return '  '.join(cell_block_repr(cell_block)
                    for cell_block in np.split(row, split_parts))

        def row_block_repr(row_block):
            return '\n'.join(row_repr(row) for row in row_block)

        return '\n\n'.join(row_block_repr(row_block)
                for row_block in np.split(self.board, split_parts))


    def compare(self, other):
        """
        Compares two Sudoku objects and returns True if they have the same board state
        """

        return np.array_equal(self.board, other.board)

    def export(self, filename="export.txt"):
        """
        Exports game board to a text file
        """
        
        with open(EXPORT_DIR / filename, "w+") as out:
            out.write(str(self.board))
