# Design Decisions and Notes

## Main Decisions

### Representing Board State

We chose to use numpy for handling the state of board possibilities because the tools provided by numpy allow for easy and efficient manipulation of large multidimensional arrays. This allowed us to use shortcuts such as quickly finding which cell has the fewest remaining possibilities, or filtering to only find the cells containing a specific value.

### Algorithm for Solving

Our algorithm for solving begins with creating a 3-dimensional array, with the first two dimensions being the rows and columns, and the last dimension representing the space of possibilities for each particular cell. We then methodically trim the possibilities for each cell using the defined rulesets. After that, we start guessing, beginning with the cell with the fewest remaining possible values, and backtracking if we reach an unsolvable puzzle state. We continue until the puzzle is solved or we have exhausted all possibilities, in which case the puzzle is unsolvable.
