********************
Animating the Solver
********************

Dokusu does not come with any animations built in, nor does it provide an interface beyond just
text output. Instead, the idea is for a user-provided callback to do all the real work.

If an ``on_cell_update`` is provided to ``Sudoku.solve()``, the solver calls it anytime it updates
a cell (changing either the board or possibilities). At the moment, the signature for 
``on_cell_update`` should look like

.. code:: python

    def on_cell_update(sudoku:Sudoku, cell:tuple, guess:bool):
        # your code here

where ``sudoku`` is the sudoku to use the values of, while ``cell`` is a 2-tuple of the form
``(row, col)``, representing the location on the board that was updated, and ``guess`` is
whether or not this update is due to a guess.

In the sample ``interface.ipynb``, the notebook has a grid of instances of ``ipywidgets.Output``
with each ``Output`` corresponding to a particular cell. Whenever a cell is updated, it updates
the content of that output, resulting in an animated view of the solving.
