from dokusu import Sudoku, Rule

def main():
    sudoku = Sudoku.sample()
    # sudoku.export("puzzle.txt")
    # sudoku = Sudoku.from_numpy(<np array here>)

    solved = sudoku.solve()
    # solved.export("solution.txt")

    print(solved) # np array (9, 9)
    
    key = Sudoku.from_file("sample_puzzles/sample_solution.csv")
    
    print(solved.compare(key))
    key.board[0][0] = 1
    print(solved.compare(key))

    pass


if __name__ == "__main__":
    main()
