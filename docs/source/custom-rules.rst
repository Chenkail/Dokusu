************
Custom Rules
************

The library supports defining your own rules for more complicated sudoku puzzles. For example, in anti-knight sudoku, a number cannot occur a (chess) knight's move away from another instance of that number. Each ``Rule`` object must implement three methods: ``reduce_possibilities``, ``find_solvable``, and ``verify``. The anti-knight sudoku rule can then be implemented as follows:

.. code:: python

    from dokusu.dokusu import *

    sudoku = Sudoku.from_file('anti-knight.csv')
    sudoku.rules.append(AntiKnightRule())
    sudoku.solve()
