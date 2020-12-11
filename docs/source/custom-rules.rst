************
Custom Rules
************

The library supports defining your own rules for more complicated sudoku puzzles. For example, in anti-knight sudoku, a number cannot occur a (chess) knight's move away from another instance of that number. The most basic viable ``Rule`` object must implement the two methods ``reduce_possibilities`` and ``verify``.
 - ``reduce_possibilities`` is used to trim the solution space based on the rule. It is meant to operate in-place on ``sudoku.possibilities``.
 - ``verify`` checks if the current board state violates the rule, returning ``True`` if the board is valid or ``False`` if it breaks the rule.

.. code:: python

    class MyCustomRule(Rule):
        def reduce_possibilities(self, sudoku, extended=False):
            # Code which reduces possibilities which do not meet the rule's conditions goes here
            pass
        
        def verify(self, sudoku):
            # Code to check if the board violates the rule goes here
            pass

For example, to define a rule saying that a certain cell must be greater than a certain other cell:

.. code:: python

    class GreaterRule(Rule):
        def __init__(self, cell_a, cell_b):
            self.cell_a = cell_a
            self.cell_b = cell_b

        def reduce_possibilities(self, sudoku, extended=False):
            # `cell_a` > `cell_b` implies `cell_b` can't be greater than the max value for `cell_a`
            max_a = sudoku.possibilities[self.cell_a].nonzero()[0].max()
            sudoku.possibilities[self.cell_b, max_a:] = False

            # and the reverse is also true
            min_b = sudoku.possibilities[self.cell_b].nonzero()[0].min()
            sudoku.possibilities[self.cell_a, :min_b+1] = False # :min_b+1 to include it
        
        def verify(self, sudoku):
            return sudoku.board[self.cell_a] > sudoku.board[self.cell_b]

After defining a rule, add it to the Sudoku object with ``Sudoku.rules.append()``.

.. code:: python

    from dokusu import Sudoku

    sudoku = Sudoku.from_file("my_puzzle.csv")
    sudoku.rules.append(GreaterRule((4,5), (5,4)))

    sudoku.solve() # solves with the rule included

This should be enough for many simple rules, but additional optional features can be used when needed.

 - ``find_solvable`` can be used to help optimize searching for solutions if there's a fast algorithm to find
   the right number for a cell directly, rather than just whittling down possibilities. For example, if a rule
   dictates that there's an exact clone of the bottom left 3x3 block somewhere in the board, once the location
   of the clone is found, any cells from one can simply be filled the other and vice versa.
 - Extended possibilities reduction: if there's a very slow but effective possibilities reduction approach,
   limit it to only be active when ``extended=True``. Sometimes, more intuitive pattern-finding approaches are
   often needed for sudokus with strange rules. For example, ``UniqueRule``'s extended reduction includes
   finding groups of N cells with N different options between them. This is prohibitively inefficient, but can
   be useful for some sudoku variants.
 - ``restriction_estimate`` only has an effect on guessing. With some rules, it's difficult to directly narrow
   down possibilities, but it's fairly easy to describe which possibilities are more 'restricted'. This method,
   based on the provided ``sudoku``, adds to ``restriction`` to estimate how restricted possibilities are in
   cells. ``restriction`` has the same shape as ``sudoku.possibilities``, with higher numbers being more
   restricted.

One subclass of ``Rule`` is ``UniqueRule``, which allows entering a numpy array slice or set of cells and
checks that no two cells in the group contain the same value. Standard sudoku rules are implemented as a list
of 27 instances of ``UniqueRule``, with 9 per row, column, and block, along with a single ``SingleRule``
which finds cells that only have one possibility. Suppose we wanted to implement a rule that each of the
two diagonals on the board had to also contain each number once. We could implement it like
this using ``UniqueRule``:

.. code:: python

    from dokusu import Sudoku, UniqueRule

    sudoku = Sudoku.from_file('diagonal.csv')
    size, _ = sudoku.board.shape
    
    # Top left to bottom right
    sudoku.rules.append(UniqueRule(indices=[(i,i) for i in range(size)]))
    # Bottom left to top right
    sudoku.rules.append(UniqueRule(indices=[(i,size-1-i) for i in range(size)]))

    solved = sudoku.solve()
    print(solved)

The library currently has two variant rules already built in:
 - ``AntiKnightRule``, where a number isn't allowed to be a knight's move away from another of itself
 - ``KillerCageRule``, where a cage is defined as a group of cells with a target sum. Within cages, digits
   may not repeat and must sum to the target sum.
