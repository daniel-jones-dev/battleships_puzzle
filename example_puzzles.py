import puzzle


def get_example_puzzle(which: int):
    if which == 0:
        # The solution shall be:
        # <=>.
        # ....
        # O.O.
        p = puzzle.Puzzle(4, 3, [1, 1, 3], col_sums=[2, 1, 2, 0],
                          row_sums=[3, 0, 2])

    elif which == 1:
        # credit to: https://krazydad.com/tablet/battleships/?kind=6x6&volumeNumber=1&bookNumber=1&puzzleNumber=1
        knowns = puzzle.CellGrid(6, 6)
        knowns.set(3, 1, puzzle.CellState.OccupiedUnknown)
        p = puzzle.Puzzle(6, 6, [4, 3, 2, 2, 1, 1, 1], [4, 1, 3, 2, 0, 4],
                          [2, 3, 0, 5, 1, 3], known_grid=knowns)

    elif which == 2:
        # credit to: https://krazydad.com/tablet/battleships/?kind=12x12&volumeNumber=1&bookNumber=1&puzzleNumber=1
        knowns = puzzle.CellGrid(12, 12)
        knowns.set(3, 4, puzzle.CellState.OccupiedWhole)
        knowns.set(0, 5, puzzle.CellState.OccupiedEndDown)
        knowns.set(9, 10, puzzle.CellState.OccupiedEndRight)
        p = puzzle.Puzzle(12, 12, [5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1],
                          [3, 0, 1, 4, 0, 1, 2, 3, 4, 3, 4, 0],
                          [0, 5, 0, 0, 2, 6, 3, 0, 3, 1, 3, 2],
                          known_grid=knowns)
    elif which == 3:
        # credit to: https://krazydad.com/tablet/battleships/?kind=12x12&volumeNumber=5&bookNumber=5&puzzleNumber=4
        knowns = puzzle.CellGrid(12, 12)
        knowns.set(5, 0, puzzle.CellState.OccupiedUnknown)
        knowns.set(8, 0, puzzle.CellState.OccupiedEndUp)
        knowns.set(1, 2, puzzle.CellState.Water)
        knowns.set(5, 2, puzzle.CellState.OccupiedUnknown)
        knowns.set(11, 2, puzzle.CellState.Water)
        knowns.set(10, 5, puzzle.CellState.OccupiedUnknown)
        knowns.set(3, 7, puzzle.CellState.OccupiedEndRight)
        knowns.set(10, 8, puzzle.CellState.OccupiedEndDown)
        knowns.set(3, 11, puzzle.CellState.OccupiedEndDown)
        knowns.set(9, 11, puzzle.CellState.OccupiedEndRight)
        p = puzzle.Puzzle(12, 12, [5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1],
                          [0, 2, 1, 5, 1, 2, 1, 0, 6, 1, 5, 1],
                          [2, 2, 4, 0, 1, 1, 2, 5, 1, 3, 1, 3],
                          known_grid=knowns)
    else:
        raise ValueError("Unknown example puzzle")

    return p
