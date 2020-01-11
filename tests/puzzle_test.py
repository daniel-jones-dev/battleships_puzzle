import unittest

from puzzle import *


# class RulesetTestCase(unittest.TestCase):
#     def test_standard(self):
#         ruleset = Ruleset()
#         self.assertEqual(ruleset.width, 10)
#         self.assertEqual(ruleset.height, 10)
#         self.assertEqual(ruleset.fleet, [1, 1, 1, 1, 2, 2, 2, 3, 3, 4])
#
#     def test_minimum(self):
#         ruleset = Ruleset(1, 1, fleet=[])
#         self.assertEqual(ruleset.width, 1)
#         self.assertEqual(ruleset.height, 1)
#         self.assertEqual(ruleset.fleet, [])
#
#     def test_fleet_too_large(self):
#         self.assertRaises(ValueError, Ruleset, 1, 1, fleet=[1, 1])
#
#     def test_fleet_sorting(self):
#         ruleset = Ruleset(10, 10, fleet=[2, 1, 3, 1])
#         self.assertEqual([1, 1, 2, 3], ruleset.fleet)


class CellStateTestCase(unittest.TestCase):
    def test_unknown(self):
        cell_state = CellState.Unknown
        self.assertTrue(cell_state.is_unknown())
        self.assertFalse(cell_state.is_water())
        self.assertFalse(cell_state.is_occupied())

    def test_water(self):
        cell_state = CellState.Water
        self.assertFalse(cell_state.is_unknown())
        self.assertTrue(cell_state.is_water())
        self.assertFalse(cell_state.is_occupied())

    def test_occupied(self):
        cell_state = CellState.OccupiedUnknown
        self.assertFalse(cell_state.is_unknown())
        self.assertFalse(cell_state.is_water())
        self.assertTrue(cell_state.is_occupied())
        self.assertFalse(cell_state.is_whole())
        self.assertFalse(cell_state.is_mid())
        self.assertFalse(cell_state.is_end())

    def test_occupied_whole(self):
        cell_state = CellState.OccupiedWhole
        self.assertFalse(cell_state.is_unknown())
        self.assertFalse(cell_state.is_water())
        self.assertTrue(cell_state.is_occupied())
        self.assertTrue(cell_state.is_whole())
        self.assertFalse(cell_state.is_mid())
        self.assertFalse(cell_state.is_end())

    def test_occupied_mid(self):
        cell_state = CellState.OccupiedMid
        self.assertFalse(cell_state.is_unknown())
        self.assertFalse(cell_state.is_water())
        self.assertTrue(cell_state.is_occupied())
        self.assertFalse(cell_state.is_whole())
        self.assertTrue(cell_state.is_mid())
        self.assertFalse(cell_state.is_end())

    def test_occupied_end(self):
        for cell_state in [CellState.OccupiedEndLeft,
                           CellState.OccupiedEndUp,
                           CellState.OccupiedEndDown,
                           CellState.OccupiedEndRight]:
            self.assertFalse(cell_state.is_unknown())
            self.assertFalse(cell_state.is_water())
            self.assertTrue(cell_state.is_occupied())
            self.assertFalse(cell_state.is_whole())
            self.assertFalse(cell_state.is_mid())
            self.assertTrue(cell_state.is_end())

    def test_symbols(self):
        for name, enum in CellState.__members__.items():
            self.assertEqual(enum, CellState.from_symbol(enum.symbol()))

    def test_invalid_symbol(self):
        self.assertEqual(None, CellState.from_symbol("?"))


class PuzzleTestCase(unittest.TestCase):
    def test_invalid_puzzle_size(self):
        # num_cols and num_rows must be > 0
        with self.assertRaises(ValueError):
            Puzzle(0, 1, ship_lengths=[])
        with self.assertRaises(ValueError):
            Puzzle(1, 0, ship_lengths=[])

    def test_invalid_puzzle_ship_length(self):
        # ship values must be > 0
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[0, 1])

    def test_invalid_puzzle_col_row_sums(self):
        # col_sums and row_sums must be specified if solution is not
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], col_sums=[0])
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], row_sums=[0])

        # col_sums, row_sums must not be specified if solution is
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], col_sums=[0], solution_ships=[])
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], row_sums=[0], solution_ships=[])

        # col_sums and row_sums must be non negative
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], col_sums=[0], row_sums=[-1])
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], col_sums=[-1], row_sums=[0])

        # col_sums and row_sums must be correct size
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], col_sums=[0, 0], row_sums=[0])
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], col_sums=[0], row_sums=[0, 0])

    def test_invalid_puzzle_grids(self):
        # known and curr grid size must match
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], col_sums=[0], row_sums=[0],
                   known_grid=CellGrid(2, 2))
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[], col_sums=[0], row_sums=[0],
                   known_grid=CellGrid(1, 1), curr_grid=CellGrid(2, 2))

    def test_invalid_puzzle_solutions(self):
        # solution_ships size must match
        with self.assertRaises(ValueError):
            Puzzle(1, 1, ship_lengths=[1], solution_ships=[])
        # solution_ships must not have collisions
        with self.assertRaises(ValueError):
            Puzzle(2, 2, ship_lengths=[2, 2],
                   solution_ships=[(0, 0, True), (0, 0, False)])
        # solution_ships must fit in grid
        with self.assertRaises(ValueError):
            Puzzle(2, 2, ship_lengths=[2], solution_ships=[(1, 1, True)])
        # solution_ships must not have neighbours
        with self.assertRaises(ValueError):
            Puzzle(2, 2, ship_lengths=[1, 1],
                   solution_ships=[(0, 0, True), (1, 1, True)])
        # solution_ships must agree with known_grid
        with self.assertRaises(ValueError):
            invalid_known_grid = CellGrid(3, 3)
            invalid_known_grid.set(0, 0, CellState.Water)
            Puzzle(3, 3, ship_lengths=[1, 1, 3], known_grid=invalid_known_grid,
                   solution_ships=[(0, 2, True), (2, 2, True), (0, 0, True)])

        valid_known_grid = CellGrid(3, 3)
        valid_known_grid.set(0, 0, CellState.OccupiedEndLeft)
        valid_known_grid.set(0, 1, CellState.Water)
        Puzzle(3, 3, ship_lengths=[1, 1, 3], known_grid=valid_known_grid,
               solution_ships=[(0, 2, True), (2, 2, True), (0, 0, True)])

    def test_puzzle_without_solution(self):
        # Puzzle solution
        # ^ w o 2
        # v w w 1
        # 2 0 1
        puzzle = Puzzle(3, 2, ship_lengths=[1, 2], col_sums=[2, 0, 1],
                        row_sums=[2, 1])
        self.assertEqual(puzzle.get_num_cols(), 3)
        self.assertEqual(puzzle.get_num_rows(), 2)
        self.assertEqual(puzzle.get_ship_lengths(), [1, 2])
        self.assertEqual(puzzle.get_col_sums(), [2, 0, 1])
        self.assertFalse(puzzle.has_solution())
        self.assertFalse(puzzle.is_solved())
        self.assertFalse(puzzle.is_incorrect())
        self.assertTrue(puzzle.is_valid())
        for c in range(3):
            for r in range(2):
                self.assertTrue(puzzle.get_cell(c, r).is_unknown())

    def test_puzzle_with_solution(self):
        # Puzzle solution
        # ^ w o 2
        # v w w 1
        # 2 0 1
        puzzle = Puzzle(3, 2, ship_lengths=[1, 2],
                        solution_ships=[(2, 0, True), (0, 0, False)])
        self.assertEqual(puzzle.get_num_cols(), 3)
        self.assertEqual(puzzle.get_num_rows(), 2)
        self.assertEqual(puzzle.get_ship_lengths(), [1, 2])
        self.assertEqual(puzzle.get_col_sums(), [2, 0, 1])
        self.assertTrue(puzzle.has_solution())
        self.assertFalse(puzzle.is_solved())
        self.assertFalse(puzzle.is_incorrect())
        self.assertTrue(puzzle.is_valid())
        for c in range(3):
            for r in range(2):
                self.assertTrue(puzzle.get_cell(c, r).is_unknown())

        # Check the solved state
        self.assertEqual(puzzle.get_solution_cell(0, 0),
                         CellState.OccupiedEndUp)
        self.assertEqual(puzzle.get_solution_cell(0, 1),
                         CellState.OccupiedEndDown)
        self.assertEqual(puzzle.get_solution_cell(1, 0),
                         CellState.Water)
        self.assertEqual(puzzle.get_solution_cell(1, 1),
                         CellState.Water)
        self.assertEqual(puzzle.get_solution_cell(2, 0),
                         CellState.OccupiedWhole)
        self.assertEqual(puzzle.get_solution_cell(2, 1),
                         CellState.Water)

    def test_puzzle_solving(self):
        # Create a puzzle with two cells in central column known
        # Puzzle solution
        # ^ w o 2
        # v w w 1
        # 2 0 1
        known_grid = CellGrid(3, 2)
        known_grid.set(1, 0, CellState.Water)
        known_grid.set(1, 1, CellState.Water)

        puzzle = Puzzle(3, 2, ship_lengths=[1, 2], known_grid=known_grid,
                        solution_ships=[(2, 0, True), (0, 0, False)])
        self.assertFalse(puzzle.is_incorrect())
        self.assertFalse(puzzle.is_solved())
        self.assertTrue(puzzle.is_valid())

        # Check that setting an unknown cell correctly is valid
        puzzle.set_cell(0, 0, CellState.OccupiedEndUp)
        self.assertFalse(puzzle.is_incorrect())
        # Check that setting an unknown cell incorrectly is valid
        puzzle.set_cell(0, 1, CellState.Water)
        self.assertTrue(puzzle.is_incorrect())
        self.assertFalse(puzzle.is_valid())
        puzzle.set_cell(0, 1, CellState.OccupiedEndDown)
        self.assertFalse(puzzle.is_incorrect())
        self.assertTrue(puzzle.is_valid())
        # TODO Should check for more types of invalidity, for example:
        #  Check that occupied cells do not touch diagonally
        #  Check ship sizes? Might be too complex

        # Check setting a known cell is invalid
        with self.assertRaises(ValueError):
            puzzle.set_cell(1, 0, CellState.OccupiedUnknown)

        puzzle.set_cell(2, 0, CellState.OccupiedWhole)
        puzzle.set_cell(2, 1, CellState.Water)
        self.assertTrue(puzzle.is_solved())

    pass


class GetAllSolutionsTestCase(unittest.TestCase):
    def test_empty_fleet(self):
        pass
        # ruleset = Ruleset(10, 10, [])
        # solutions = get_all_solutions(ruleset)
        # expected_solution = Puzzle(ruleset, grid=[[CellState.Water for x in
        #                                            range(10)] for y in
        #                                           range(10)])
        # self.assertEqual([expected_solution], [s for s in solutions])

    def test_small(self):
        pass
        # ruleset = Ruleset(3, 3, [1, 1, 3])
        # solutions = get_all_solutions(ruleset)
        # print("\n".join(str(s) for s in solutions))

    pass


if __name__ == '__main__':
    unittest.main()
