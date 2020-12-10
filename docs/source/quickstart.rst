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

Exporting Puzzles
=================

You can export the current board state to a file by calling the ``export()`` function. This exports to the ``exports`` folder in the ``dokusu`` root directory. It takes an optional filename argument, but defaults to ``export.txt`` otherwise.

.. code:: python

    from dokusu import Sudoku

    sudoku = Sudoku.sample()
    sudoku.export("sample.txt")

Comparing Puzzles
=================

The ``compare()`` method checks two boards to see if they contain the same values in the same cells. For example, to check the solution to a puzzle against an answer key, you might write something like the following:

.. code:: python

    from dokusu import Sudoku

    sudoku = Sudoku.from_file("puzzle.csv")
    sudoku.solve()

    key = Sudoku.from_file("answers.csv")
    print(sudoku.compare(key))
