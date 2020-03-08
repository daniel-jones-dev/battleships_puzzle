import puzzle
import textwrap
from typing import Optional, Sequence, Tuple


class PuzzleSolveStep:
    """
    A description of an applied logical rule, and the solved cells.
    This is the result of a solver step.
    """

    def __init__(self,
                 desc: str,
                 solved_cells: Sequence[Tuple[int, int, puzzle.CellState]] =
                 None):
        if solved_cells is None:
            solved_cells = []
        self.desc = desc
        self.solved_cells = solved_cells

    def __str__(self):
        return "\n".join(
            [self.desc] +
            ["-> Set cell {},{} to {}".format(c, r, cell_state.name)
             for c, r, cell_state in self.solved_cells])


class Solver:
    """
    A solver is given a puzzle to solve, and will solve it step-by-step using
    various rules.
    """

    def __init__(self, puz: puzzle.Puzzle):
        """

        """
        self.puzzle = puz

        # ship_length_modes is a sorted list of the different ship lengths
        self.ship_length_modes = list(
            set(self.puzzle.get_ship_lengths()))
        self.ship_length_modes.sort()

        # ship_length_dict is a dictionary of each ship length to the ship count
        self.ship_lengths_dict = {}
        for ship_length in self.puzzle.get_ship_lengths():
            if ship_length not in self.ship_lengths_dict:
                self.ship_lengths_dict[ship_length] = 0
            self.ship_lengths_dict[ship_length] += 1

        # ship_possibles is a dictionary of each ship length to a list of tuples
        # each tuple holds the c,r,dir of a possible location of the ship
        self.ship_possibles = {}

    def do_step(self, solve_step: PuzzleSolveStep):
        for c, r, cell_state in solve_step.solved_cells:
            self.puzzle.set_cell(c, r, cell_state)

    def solve_step(self) -> PuzzleSolveStep:
        """
        Applies all known logical rules until a rule is found to solve a cell
        Returns a PuzzleSolveStep
        """
        if not self.puzzle.is_valid():
            return PuzzleSolveStep("puzzle is invalid")
        if self.puzzle.is_solved():
            return PuzzleSolveStep("puzzle is solved")

        puzzle_solve_step = self.solve_line_occupied_total_reached()
        if len(puzzle_solve_step.solved_cells) > 0:
            return puzzle_solve_step

        puzzle_solve_step = self.solve_line_unknowns_total_reached()
        if len(puzzle_solve_step.solved_cells) > 0:
            return puzzle_solve_step

        puzzle_solve_step = self.solve_ship_state_updates()
        if len(puzzle_solve_step.solved_cells) > 0:
            return puzzle_solve_step

        puzzle_solve_step = self.solve_ship_diagonals()
        if len(puzzle_solve_step.solved_cells) > 0:
            return puzzle_solve_step

        puzzle_solve_step = self.solve_ship_1_around()
        if len(puzzle_solve_step.solved_cells) > 0:
            return puzzle_solve_step

        puzzle_solve_step = self.solve_ship_end_around()
        if len(puzzle_solve_step.solved_cells) > 0:
            return puzzle_solve_step

        self.calculate_ship_possibles()

        puzzle_solve_step = self.solve_place_large_ship()
        if len(puzzle_solve_step.solved_cells) > 0:
            return puzzle_solve_step

        return PuzzleSolveStep("none found")

    def solve_line_occupied_total_reached(self) -> PuzzleSolveStep:
        """
        Checks for a row or column with at least one unknown cell, where the
        number of occupied cells matches the known sum for the row or column.
        This implies all unknown cells must be water.
        Returns a PuzzleSolveStep
        """
        col_text = textwrap.dedent("""\
                In column {}, {} cells are occupied, matching the total. Therefore
                all unknown cells are water.
                """)
        row_text = textwrap.dedent("""\
                In row {}, {} cells are occupied, matching the total. Therefore
                all unknown cells are water.
                """)

        for c in range(self.puzzle.get_num_cols()):
            unknown_cells = [r for r in range(self.puzzle.get_num_rows())
                             if self.puzzle.get_cell(c, r).is_unknown()]
            if len(unknown_cells) > 0:
                occupied_total = self.puzzle.get_col_occupied_sum(c)
                if occupied_total == self.puzzle.get_col_sum(c):
                    return PuzzleSolveStep(col_text.format(c, occupied_total),
                                           [(c, r, puzzle.CellState.Water)
                                            for r in unknown_cells])

        for r in range(self.puzzle.get_num_rows()):
            unknown_cells = [c for c in range(self.puzzle.get_num_cols())
                             if self.puzzle.get_cell(c, r).is_unknown()]
            if len(unknown_cells) > 0:
                occupied_total = self.puzzle.get_row_occupied_sum(r)
                if occupied_total == self.puzzle.get_row_sum(r):
                    return PuzzleSolveStep(
                        row_text.format(r, occupied_total),
                        [(c, r, puzzle.CellState.Water)
                         for c in unknown_cells])

        return PuzzleSolveStep("none found")

    def solve_line_unknowns_total_reached(self) -> PuzzleSolveStep:
        """
        Checks for a row or column with at least one unknown cell, where the
        number of unknown and occupied cells matches the known sum for the row
        or column. This implies all unknown cells must be occupied.
        Returns a PuzzleSolveStep
        """
        col_text = textwrap.dedent("""\
                In column {}, {} cells are occupied and {} are unknown, matching 
                the total occupied of {}. Therefore all unknown cells are occupied.
                """)
        row_text = textwrap.dedent("""\
                In row {}, {} cells are occupied and {} are unknown, matching 
                the total occupied of {}. Therefore all unknown cells are occupied.
                """)

        for c in range(self.puzzle.get_num_cols()):
            unknown_cells = [r for r in range(self.puzzle.get_num_rows())
                             if self.puzzle.get_cell(c, r).is_unknown()]
            unknown_total = len(unknown_cells)
            if unknown_total > 0:
                occupied_total = self.puzzle.get_col_occupied_sum(c)
                col_sum = self.puzzle.get_col_sum(c)
                if unknown_total + occupied_total == col_sum:
                    desc = col_text.format(c, occupied_total, unknown_total,
                                           col_sum)
                    return PuzzleSolveStep(desc,
                                           [(c, r,
                                             puzzle.CellState.OccupiedUnknown)
                                            for r in
                                            unknown_cells])

        for r in range(self.puzzle.get_num_rows()):
            unknown_cells = [c for c in range(self.puzzle.get_num_cols())
                             if self.puzzle.get_cell(c, r).is_unknown()]
            unknown_total = len(unknown_cells)
            if unknown_total > 0:
                occupied_total = self.puzzle.get_row_occupied_sum(r)
                row_sum = self.puzzle.get_row_sum(r)
                if unknown_total + occupied_total == row_sum:
                    desc = row_text.format(r, occupied_total, unknown_total,
                                           row_sum)
                    return PuzzleSolveStep(desc, [
                        (c, r, puzzle.CellState.OccupiedUnknown) for c in
                        unknown_cells])

        return PuzzleSolveStep("none found")

    def solve_ship_diagonals(self) -> PuzzleSolveStep:
        """
        Checks for unknown cells lying diagonal from an occupied cell. These
        cells must be water.
        Returns a PuzzleSolveStep
        """
        text = textwrap.dedent("""\
                Ships cannot lie adjacent, and cell {}, {} is occupied, so all 
                diagonal cells are water.
                """)

        for c in range(self.puzzle.get_num_cols()):
            for r in range(self.puzzle.get_num_rows()):
                if self.puzzle.get_cell(c, r).is_occupied():
                    neighbour_cells = \
                        self.puzzle.get_diagonal_neighbour_cells(c, r)
                    unknown_cells = [(cn, rn) for cn, rn in neighbour_cells if
                                     self.puzzle.get_cell(cn, rn).is_unknown()]

                    if len(unknown_cells) > 0:
                        return PuzzleSolveStep(text.format(c, r),
                                               [(cn, rn,
                                                 puzzle.CellState.Water) for
                                                cn, rn in
                                                unknown_cells])

        return PuzzleSolveStep("none found")

    def solve_ship_state_updates(self) -> PuzzleSolveStep:
        """
        Checks for OccupiedUnknown cells that can be made more accurate.
        Returns a PuzzleSolveStep
        """
        text = textwrap.dedent("""\
                        Occupied cell at {},{} must be a specific ship part.
                        """)
        for c in range(self.puzzle.get_num_cols()):
            for r in range(self.puzzle.get_num_rows()):
                if self.puzzle.get_cell(c, r) == \
                        puzzle.CellState.OccupiedUnknown:

                    nondiagonal_neighbours = \
                        self.puzzle.get_nondiagonal_neighbour_cells(c, r)

                    if all(self.puzzle.get_cell(c, r).is_water() for
                           c, r in nondiagonal_neighbours):
                        return PuzzleSolveStep(
                            text.format(c, r),
                            [(c, r, puzzle.CellState.OccupiedWhole)])

                    if sum(self.puzzle.get_cell(c, r).is_occupied() for
                           c, r in nondiagonal_neighbours) == 2:
                        return PuzzleSolveStep(
                            text.format(c, r),
                            [(c, r, puzzle.CellState.OccupiedMid)])

                    if sum(self.puzzle.get_cell(c, r).is_occupied() for
                           c, r in nondiagonal_neighbours) == 1 and \
                            all(not self.puzzle.get_cell(c, r).is_unknown() for
                                c, r in nondiagonal_neighbours):

                        if c > 0 and self.puzzle.get_cell(c - 1,
                                                          r).is_occupied():
                            return PuzzleSolveStep(
                                text.format(c, r),
                                [(c, r, puzzle.CellState.OccupiedEndRight)])
                        elif r > 0 and \
                                self.puzzle.get_cell(c, r - 1).is_occupied():
                            return PuzzleSolveStep(
                                text.format(c, r),
                                [(c, r, puzzle.CellState.OccupiedEndDown)])
                        elif c + 1 < self.puzzle.get_num_cols() and \
                                self.puzzle.get_cell(c + 1, r).is_occupied():
                            return PuzzleSolveStep(
                                text.format(c, r),
                                [(c, r, puzzle.CellState.OccupiedEndLeft)])
                        elif r + 1 < self.puzzle.get_num_rows() and \
                                self.puzzle.get_cell(c, r + 1).is_occupied():
                            return PuzzleSolveStep(
                                text.format(c, r),
                                [(c, r, puzzle.CellState.OccupiedEndUp)])

        return PuzzleSolveStep("none found")

    def solve_ship_1_around(self) -> PuzzleSolveStep:
        """
        Checks for unknown cells lying next to a 1-ship. These cells must be
        water.
        Returns a PuzzleSolveStep
        """
        text = textwrap.dedent("""\
                    Ships cannot lie next to a 1-length ship in cell {},{}, so all 
                    adjacent cells are water.
                    """)
        for c in range(self.puzzle.get_num_cols()):
            for r in range(self.puzzle.get_num_rows()):
                if self.puzzle.get_cell(c, r).is_whole():
                    neighbour_cells = self.puzzle.get_neighbour_cells(c, r)
                    unknown_cells = [(cn, rn) for cn, rn in neighbour_cells if
                                     self.puzzle.get_cell(cn, rn).is_unknown()]

                    if len(unknown_cells) > 0:
                        return PuzzleSolveStep(text.format(c, r),
                                               [(cn, rn,
                                                 puzzle.CellState.Water) for
                                                cn, rn in
                                                unknown_cells])

        return PuzzleSolveStep("none found")

    def solve_ship_end_around(self) -> PuzzleSolveStep:
        """
        Checks for unknown cells lying next to an end-ship. One cell must be
        occupied, and the other three nearby cells must be water.
        Returns a PuzzleSolveStep
        """
        text = textwrap.dedent("""\
                    Cell {},{} has a ship-end, so the next cell is occupied and 
                    other cells are water.""")

        for end_c in range(self.puzzle.get_num_cols()):
            for end_r in range(self.puzzle.get_num_rows()):
                state = self.puzzle.get_cell(end_c, end_r)
                if state.is_end():
                    if state == puzzle.CellState.OccupiedEndDown:
                        expected_water_cells = [(end_c, end_r + 1),
                                                (end_c + 1, end_r),
                                                (end_c - 1, end_r)]
                        expected_occupied_cell = end_c, end_r - 1
                    elif state == puzzle.CellState.OccupiedEndUp:
                        expected_water_cells = [(end_c, end_r - 1),
                                                (end_c + 1, end_r),
                                                (end_c - 1, end_r)]
                        expected_occupied_cell = end_c, end_r + 1
                    elif state == puzzle.CellState.OccupiedEndLeft:
                        expected_water_cells = [(end_c - 1, end_r),
                                                (end_c, end_r + 1),
                                                (end_c, end_r - 1)]
                        expected_occupied_cell = end_c + 1, end_r
                    else:  # OccupiedEndRight
                        expected_water_cells = [(end_c + 1, end_r),
                                                (end_c, end_r + 1),
                                                (end_c, end_r - 1)]
                        expected_occupied_cell = end_c - 1, end_r

                    # Strip cells out of bounds
                    expected_water_cells = self.puzzle.strip_out_of_bound_cells(
                        expected_water_cells)

                    solved_cells = []

                    for expected_water_cell in expected_water_cells:
                        exp_water_c, exp_water_r = expected_water_cell
                        actual_state = self.puzzle.get_cell(exp_water_c,
                                                            exp_water_r)
                        if actual_state.is_unknown():
                            solved_cells.append((exp_water_c, exp_water_r,
                                                 puzzle.CellState.Water))

                    exp_occ_c, exp_occ_r = expected_occupied_cell
                    if 0 <= exp_occ_c < self.puzzle.get_num_cols() \
                            and 0 <= exp_occ_r < self.puzzle.get_num_rows():
                        actual_state = self.puzzle.get_cell(exp_occ_c,
                                                            exp_occ_r)
                        if actual_state.is_unknown():
                            solved_cells.append((exp_occ_c, exp_occ_r,
                                                 puzzle.CellState.OccupiedUnknown))

                    if len(solved_cells) > 0:
                        return PuzzleSolveStep(
                            text.format(end_c, end_r), solved_cells)

        return PuzzleSolveStep("none found")

    def calculate_ship_possibles(self):
        """
        Calculates the possible positions of large ships.
        """
        self.ship_possibles = {}

        # Go through each ship length
        for length in self.ship_length_modes:
            self.ship_possibles[length] = []
            for c in range(self.puzzle.get_num_cols()):
                for r in range(self.puzzle.get_num_rows()):
                    for direction in [True, False]:
                        if self.puzzle.can_place_ship(length, c, r, direction):
                            self.ship_possibles[length].append(
                                (c, r, direction))

    def solve_place_large_ship(self) -> PuzzleSolveStep:
        """
        Checks for unknown cells that are the only possibility to hold the
        largest ship.
        Returns a PuzzleSolveStep
        """
        text = textwrap.dedent("""\
                    Ship of length {} must go from cells {},{} to {},{}.""")
        # For each length of ship, check if the list of possible ship locations
        #  matches the number of ships to place
        for length, possibles in self.ship_possibles.items():
            if len(possibles) == self.ship_lengths_dict[length]:
                # These positions must be the ship positions

                # If any of the ships cells are unknown, we can fill them
                for start_c, start_r, direction in possibles:
                    ship_cells = self.puzzle.get_ship_cells(length, start_c,
                                                            start_r,
                                                            direction)
                    if any(self.puzzle.get_cell(c, r).is_unknown()
                           for c, r in ship_cells):
                        end_c = start_c
                        end_r = start_r
                        if direction:
                            end_c += length - 1
                        else:
                            end_r += length - 1
                        return PuzzleSolveStep(
                            text.format(length, start_c, start_r, end_c, end_r),
                            [(c, r, puzzle.CellState.OccupiedUnknown) for
                             c, r in ship_cells])

        return PuzzleSolveStep("none found")

    def solve_partial_fill_ship(self) -> PuzzleSolveStep:
        """
        Checks for unknown cells that must be filled, though the ship placement
        is unknown.
        Returns a PuzzleSolveStep
        """
        # TODO This rule needs to be implemented
        return PuzzleSolveStep("none found")
