from puzzle import *

# Very simple example -- a 4x3 grid with a 3-ship and two 1-ships
# simple_ruleset = Ruleset(4, 3, [1, 1, 3])

# The solution shall be:
# <=>.
# ....
# O.O.
# column_sums = [2, 1, 2, 0]
# row_sums = [3, 0, 2]
# simple_puzzle = Puzzle(simple_ruleset, column_sums=column_sums,
#                        row_sums=row_sums)
# solved_puzzle = Puzzle(simple_ruleset, column_sums=column_sums,
#                        row_sums=row_sums)
# solved_puzzle.grid[0][0] = CellState.OccupiedEndLeft
# solved_puzzle.grid[0][1] = CellState.OccupiedMidLR
# solved_puzzle.grid[0][2] = CellState.OccupiedEndRight
# solved_puzzle.grid[0][3] = CellState.Water
# solved_puzzle.grid[1][0] = CellState.Water
# solved_puzzle.grid[1][1] = CellState.Water
# solved_puzzle.grid[1][2] = CellState.Water
# solved_puzzle.grid[1][3] = CellState.Water
# solved_puzzle.grid[2][0] = CellState.OccupiedWhole
# solved_puzzle.grid[2][1] = CellState.Water
# solved_puzzle.grid[2][2] = CellState.OccupiedWhole
# solved_puzzle.grid[2][3] = CellState.Water
#
# print(simple_puzzle)
# print(solved_puzzle)
# assert (simple_puzzle.is_valid())
# assert (solved_puzzle.is_valid())
# assert (not simple_puzzle.is_solved())
# assert (solved_puzzle.is_solved())
#

# Very simple example -- a 3x3 grid with a 3-ship and two 1-ships

count = 0

for solution in generate_solved_puzzles(3, 3, [1, 1, 3]):
    print(solution)
    count += 1

print("count: {}".format(count))
