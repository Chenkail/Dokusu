****************
Quickstart Guide
****************

Solving a Sample Puzzle
=======================

The following code solves the built-in sample puzzle and prints the solution:

.. code:: python

    from dokusu import Sudoku

    sudoku = Sudoku.sample()
    solved = sudoku.solve()
    print(solved)

Importing Puzzles
=================

To import a puzzle, call the ``from_file()`` method. For example, to import from a file called "puzzle.csv", we would write the following:

.. code:: python

    from dokusu import Sudoku

    sudoku = Sudoku.from_file("puzzle.csv")
