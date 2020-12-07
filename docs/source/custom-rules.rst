************
Custom Rules
************

The library supports defining your own rules for more complicated sudoku puzzles. For example, in anti-knight sudoku, a number cannot occur a (chess) knight's move away from another instance of that number. Each ``Rule`` object must implement two methods: ``reduce_possibilities`` and ``verify``. ``reduce_possibilities`` is used to trim the solution space based on the rule, while ``verify`` checks if the current board state violates the rule. There is a third method, ``find_solvable``, which is optional, but can be used to help optimize searching for solutions. Suppose we wanted to implement a rule that each of the two diagonals on the board had to also contain each number once. We could implement it like this:

.. code:: python

    from dokusu import Sudoku, Rule
    
    class DiagonalRule(Rule):
        def reduce_possibilities(self, sudoku):
            size, _ = sudoku.board.shape
            for i in range(size):
                # Diagonal from top left to bottom right
                value = sudoku.board[(i, i)]
                for j in range(i+1, size):
                    # Remove from set of possibilities -
                    # Remember that the array is indexed from zero!
                    sudoku.possibilities[j, j, value-1] = False

                # Diagonal from bottom left to top right
                value = sudoku.board[(i, rows-i-1)]
                for j in range(i+1, size):
                    sudoku.possibilities[j, rows-j-1, value-1] = False

        def verify(self, sudoku):
            size, _ = sudoku.board.shape
            for i in range(size):
                # Diagonal from top left to bottom right
                value = sudoku.board[(i, i)]
                for j in range(i+1, size):
                    if sudoku.board[j, j] == value:
                        return False
                    
                # Diagonal from bottom left to top right
                value = sudoku.board[(i, rows-i-1)]
                for j in range(i+1, size):
                    if sudoku.board[j, rows-j-1] == value:
                        return False

            return True
    
    sudoku = Sudoku.from_file('diagonal.csv')
    sudoku.rules.append(DiagonalRule())
    sudoku.solve()
