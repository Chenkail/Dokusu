# Design Decisions and Notes

## Library, not an Application

This project is meant to serve as a library to facilitate sudoku solving behavior.

Some examples of possible usage are as follows:

- program to animate solving a sudoku (`interface.ipynp`)
- program to help set sudoku variants puzzles (no sample implemented)
- program to provide hints in solving a variant (no sample implemented)

The main reason for this decision is that each of those use cases either needs to implement sudoku (variant) solving, or use a library such as this to handle that. As such, it makes sense to dedicate this project to primarily the task of solving, and leaving the specific purpose to any client code. Essentially, we focused on doing one thing, and doing it well (mostly).

## Algorithm for Solving

Our algorithm for solving begins with creating a 3-dimensional array, with the first two dimensions being the rows and columns, and the last dimension representing the space of possibilities for each particular cell. We then methodically trim the possibilities for each cell using the defined rulesets. After that, we start guessing, beginning with the cell with the fewest remaining possible values, and backtracking if we reach an unsolvable puzzle state. We continue until the puzzle is solved or we have exhausted all possibilities, in which case the puzzle is unsolvable.

## Rule Structure

The rules are structured as they are to ensure maximum extensibility and performance. For this, we went with a fairly encapsulated approach, where the solver doesn't actually know how to reduce possibilities or find solvable cells. Instead, the rules themselves are tasted with doing this. Base sudoku rules are simply composed of 27 `UniqueRule`s, 9 per each row, column, and box, along with a single `SingleRule` to represent how each cell has one value. This also enables a high degree of code reuse. e.g. `KillerCageRule` can just use a UniqueRule on its cells. With this structure, it's also possible to do things like show which specific rule a sudoku fails or iterate over indiidual rules to provide hints.

## Vectorized Operations/Numpy Usage

Within the rules, we make extensive use of highly vectorized `numpy` to have the solver be as fast as possible. With normal code, to limit the possibilities such that a set of cells can't have a 5 in them, you'd have to go cell by cell, setting values as you go. With `numpy`, you can do something like `sudoku.possibilities[row_slice, 4] = False`, which uses C and C++ internally with highly optimized code on contiguous arrays to effectively do it all at once. This is just a simple example, but it gets a lot more complicated when doing operations like "disable possibilities values of cells with a known value in cells without a known value" like in `UniqueRule`s non-extended possibilities reduction.
