import numpy as np
from itertools import permutations

class Rule:
    def reduce_possibilities(self, sudoku, extended=False):
        raise NotImplementedError

    def find_solvable(self, sudoku):
        """
        Find the values of any cells that can easily be found with this rule
        """
        pass

    def verify(self, sudoku):
        """
        Check to verify that the board isn't broken
        """
        raise NotImplementedError

    def restriction_estimate(self, sudoku, restriction):
        """
        Estimate how 'restricted' each possibility in the sudoku is.

        `restriction` has the same shape as `sudoku.possibilities`
        """
        pass

class UniqueRule(Rule):

    index_sets = {}

    def __init__(self, slice=None, indices=None, strong=True):
        self.slice = slice
        self.indices = np.array(indices)
        self.indicesT = None

        self.subset = self.slice
        if indices is not None:
            self.indicesT = tuple(np.array(indices).T)
            self.subset = self.indicesT

        self.strong = strong

    def reduce_possibilities(self, sudoku, extended=False):
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

        if extended:
            # TODO: make this work with indices lists too, rather than just slices
            # if a N-subset of a unique set has N or less options, it contains all those options.
            row_b = sudoku.board[self.subset]
            row_p = sudoku.possibilities[self.subset]
            size = np.prod(row_b.shape)
            for index_set in UniqueRule.get_index_sets(size):
                index_set.resize(row_b.shape)
                possible_digits = row_p[index_set].sum(0, dtype=bool)
                if possible_digits.sum() == index_set.sum():
                    if self.slice is not None:
                        mask = np.zeros_like(row_p)
                        possible_digits_slice = (*[slice(None) for _ in row_b.shape], possible_digits)
                        mask[possible_digits_slice] = True
                        mask[index_set, :] = False
                        row_p[mask] = False
                    else:
                        mask = np.zeros_like(sudoku.possibilities)
                        subset = tuple(self.indices[~index_set].T)
                        mask[subset] = True
                        mask[:, :, ~possible_digits] = False
                        sudoku.possibilities[mask] = False
        
    @staticmethod
    def get_index_sets(size):
        if size in UniqueRule.index_sets:
            return UniqueRule.index_sets[size]

        def func(n, a=0, acc=[]):
            if n == 0:
                arr = np.zeros(size, bool)
                arr[acc] = True
                return [arr]
            out = []
            for X in range(a, size):
                out += func(n-1, X+1, [*acc, X])
            return out

        index_sets = np.array(sum((func(n) for n in range(2, size)), []))
        UniqueRule.index_sets[size] = index_sets
        return index_sets


    def find_solvable(self, sudoku):
        if not self.strong:
            return

        b_subset = sudoku.board[self.subset]
        if self.subset is self.slice and len(b_subset.shape) == 1:
            p_subset = sudoku.possibilities[self.subset]

            counts = p_subset.sum(axis=0)

            locations = p_subset.argmax(0)[counts == 1]
            values = np.nonzero(counts == 1)[0] + 1

            b_subset[locations] = values

    def verify(self, sudoku):
        #if self.strong:
            #target = set(range(sudoku.board_size))
            #actual = set(sudoku.board[self.subset].flatten() + 1)
            #return target != actual
        #else:
        #    flat = sudoku.board[self.subset].flatten()
        #    return len(set(flat)) == len(flat)

        flat = sudoku.board[self.subset].flatten()
        nonzero = flat[flat != 0]
        #unique = len(set(flat)) == len(flat)
        unique = len(set(nonzero)) == len(nonzero)
        return unique
        #has_all = 

        #target = set(range(sudoku.board_size))
        #actual = set(flat + 1)
        #return target != actual

    def __repr__(self):
        name = type(self).__name__
        strong = '' if self.strong else ', strong=False'
        if self.slice is not None:
            return f'{name}({self.slice}{strong})'
        else:
            return f'{name}(indices={self.indices}{strong})'


class SingleRule(Rule):
    def reduce_possibilities(self, sudoku, extended=False):
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
        return (sudoku.possibilities.sum(-1) > 0).all()

    def restriction_estimate(self, sudoku, restriction):
        restriction += 1 / sudoku.possibilities.sum(-1).reshape((9,9,1))
        #restriction -= 1000 * (sudoku.board > 0).reshape(9, 9, 1)
        
class AntiKnightRule(Rule):

    KNIGHT_MOVES = np.array([
        [1, 2], [1, -2], [-1, 2], [-1, -2],
        [2, 1], [2, -1], [-2, 1], [-2, -1],
    ])

    def reduce_possibilities(self, sudoku, extended=False):
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

class KillerCageRule(UniqueRule):
    digits_cache = {}

    def __init__(self, indices, sum):
        super().__init__(indices=indices, strong=False)
        self.sum = sum

    def reduce_possibilities(self, sudoku, extended=False):
        super(KillerCageRule, self).reduce_possibilities(sudoku, extended)

        num_left = (sudoku.board[self.subset] == 0).sum()
        sum_left = self.sum - sudoku.board[self.subset].sum()

        if sum_left == 0 and num_left == 0:
            return

        remaining_cells = tuple(dim[sudoku.board[self.subset] == 0] for dim in self.subset)
        #if sum_left < num_left or sum_left > num_left * 9:
        min_sum = self.min_sum(sudoku, extended=extended)
        max_sum = self.max_sum(sudoku, extended=extended)
        if self.sum < min_sum or self.sum > max_sum:
            sudoku.possibilities[remaining_cells] = False
        else:
            digits = KillerCageRule.possible_digits(num_left, sum_left)
            sudoku.possibilities[remaining_cells] = sudoku.possibilities[remaining_cells] & digits

    def min_sum(self, sudoku, extended=False):
            #return min_max_sum_helper(self.indices, sudoku, 0)
        if not extended:
            sub_p = sudoku.possibilities[self.subset]
            return (sub_p.argmax(1) + 1).sum()

        relevant_possibilities = [
            tuple(sudoku.possibilities[i, j].nonzero()[0] + 1)
            for i, j in self.indices
        ]
        best = 99*len(self.indices) # arbitrarily high number
        for perm in set(permutations(relevant_possibilities)):
            used = set()
            min_sum = 0
            failed = False
            for values in perm:
                remaining = set(values) - used
                if len(remaining) == 0:
                    failed = True
                    break
                next_value = min(remaining)
                min_sum += next_value
                used.add(next_value)

            if not failed:
                best = min(min_sum, best)

        return best


    def max_sum(self, sudoku, extended=False):
        if not extended:
            sub_p = sudoku.possibilities[self.subset]
            return (9 - sub_p[:, ::-1].argmax(1)).sum()

        relevant_possibilities = [
            tuple(sudoku.possibilities[i, j].nonzero()[0] + 1)
            for i, j in self.indices
        ]
        best = 0
        for perm in set(permutations(relevant_possibilities)):
            used = set()
            max_sum = 0
            failed = False
            for values in perm:
                remaining = set(values) - used
                if len(remaining) == 0:
                    failed = True
                    break
                next_value = max(remaining)
                max_sum += next_value
                used.add(next_value)

            if not failed:
                best = max(max_sum, best)

        return best

    def verify(self, sudoku):
        if not super(KillerCageRule, self).verify(sudoku):
            return False

        num_left = (sudoku.board[self.subset] == 0).sum()
        sum_left = self.sum - sudoku.board[self.subset].sum()

        if num_left == 0 and sum_left == 0: # cage full with right sum
            return True

        if self.sum < self.min_sum(sudoku) or self.sum > self.max_sum(sudoku):
            return False

        possible = KillerCageRule.possible_digits(num_left, sum_left).any()

        return possible
        
        #match_sum = sudoku.board[self.subset].sum() == self.sum
        #match_unique = super(KillerCageRule, self).verify(sudoku)
        #return match_sum and match_unique

    def restriction_estimate(self, sudoku, restriction):
        # number of unsolved cells left
        num_left = (sudoku.board[self.subset] == 0).sum()
        # remaining sum (for unsolved cells)
        sum_left = self.sum - sudoku.board[self.subset].sum()

        # minimum sum of the unsolved cells
        min_remaining = self.min_sum(sudoku) - sudoku.board[self.subset].sum() 
        # minimum sum of the unsolved cells
        max_remaining = self.max_sum(sudoku) - sudoku.board[self.subset].sum()

        high_slope = 1 / (sum_left - min_remaining + 1)
        low_slope = 1 / (sum_left - max_remaining - 1)

        for i, j in self.indices:
            if sudoku.board[i, j] > 0:
                continue
            cell_min = sudoku.possibilities[i, j].argmax() + 1
            cell_max = 9 - sudoku.possibilities[i, j, ::-1].argmax()

            k = np.arange(0, 9)

            # if max_remaining is low, penalize high values
            # if min_remaining is high, penalize low values
            high_penalty = ((k+1) - cell_min) * high_slope
            low_penalty = ((k+1) - cell_max) * low_slope

            restriction[i, j] += high_penalty + low_penalty


    # TODO: I'm 100% sure there's a better way to do this stuff
    @staticmethod
    def possible_cages(count, target, min=1, digits=[]):
        if count == 0:
            if target == 0:
                return [digits]
            else:
                return None

        cages = []

        for X in range(min, 10):
            new_digits = digits + [X]
            out = KillerCageRule.possible_cages(count-1, target-X, min=X+1, digits=new_digits)
            if out is not None:
                cages += out

        return cages

    @staticmethod
    def possible_digits(count, target):
        if (count, target) in KillerCageRule.digits_cache:
            return KillerCageRule.digits_cache[(count, target)]
        
        digits = set()
        cages = KillerCageRule.possible_cages(count, target)
        if cages is not None:
            for cage in cages:
                digits.update(cage)
        digits = np.array(list(digits))
        possibilities = np.zeros(9, dtype=bool)
        if len(digits) > 0:
            possibilities[digits - 1] = True
            
        KillerCageRule.digits_cache[(count, target)] = possibilities
        return possibilities



