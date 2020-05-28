from enum import Enum
import copy
import itertools
from typing import Iterable, Optional, Sequence, Tuple


class CellState(Enum):
    Unknown = "."
    Water = "w"
    OccupiedUnknown = "#"
    OccupiedWhole = "O"
    OccupiedMid = "="
    OccupiedEndLeft = "<"
    OccupiedEndUp = "^"
    OccupiedEndRight = ">"
    OccupiedEndDown = "v"

    def is_unknown(self):
        return self == CellState.Unknown

    def is_water(self):
        return self == CellState.Water

    def is_occupied(self):
        return self.is_mid() or self.is_whole() or self.is_end() \
               or self == CellState.OccupiedUnknown

    def is_mid(self):
        return self == CellState.OccupiedMid

    def is_whole(self):
        return self == CellState.OccupiedWhole

    def is_end(self):
        return self in [CellState.OccupiedEndDown,
                        CellState.OccupiedEndLeft,
                        CellState.OccupiedEndRight,
                        CellState.OccupiedEndUp]

    def describe(self):
        return self.name, self.value

    def symbol(self):
        """Outputs a character to represent the cell in a grid"""
        return self.value

    @staticmethod
    def from_symbol(symbol):
        for name, enum in CellState.__members__.items():
            if enum.value == symbol:
                return enum
        return None


class CellGrid:
    """
    CellGrid represents the state of all cells in a grid as a CellState.
    """

    def __init__(self, num_cols: int, num_rows: int):
        if num_cols < 1 or num_rows < 1:
            raise ValueError("number of columns and rows must be > 0")

        self.num_cols = num_cols
        self.num_rows = num_rows
        self._grid = {}
        for c in range(num_cols):
            for r in range(num_rows):
                self._grid[(c, r)] = CellState.Unknown

    def get(self, c: int, r: int):
        self._check_in_range(c, r)
        return self._grid[(c, r)]

    def set(self, c: int, r: int, state: CellState,
            expected_state: Optional[CellState] = None) -> bool:
        self._check_in_range(c, r)
        if expected_state is not None:
            if self.get(c, r) != expected_state:
                return False
        self._grid[(c, r)] = state
        return True

    def _check_in_range(self, c, r):
        if r < 0 or r >= self.num_rows:
            raise ValueError("r out of range")
        elif c < 0 or c >= self.num_cols:
            raise ValueError("c out of range")


class Puzzle:
    """
    Puzzle represents a battleships puzzle, including:
        - the number of rows and columns in the grid
        - the number of ships and the length of each ship
        - the occupied sums of each row and column
        - the known cells i.e. the known state at the beginning of the puzzle
        - the current state, e.g. the state of each cell including guesses
        - optionally, the solution of the puzzle, i.e. the location of all ships
    The solution, if included, is not necessarily unique.
    The current state must agree with the known cell state (i.e. any known
    cells in the knowns must match in the current state), but the current state
    may be incorrect (i.e. disagree with the solution).
    """

    def __init__(self, num_cols: int, num_rows: int,
                 ship_lengths: Iterable[int],
                 col_sums: Optional[Iterable[int]] = None,
                 row_sums: Optional[Iterable[int]] = None,
                 known_grid: Optional[CellGrid] = None,
                 curr_grid: Optional[CellGrid] = None,
                 solution_ships: Optional[
                     Iterable[Tuple[int, int, bool]]] = None):
        """
        Creates a puzzle with a grid of the specified number of rows and
        columns.

        :param num_cols: Number of columns in the grid
        :param num_rows: Number of rows in the grid
        :param ship_lengths: List of the ship lengths, sorted shortest to
               longest.
        :param col_sums: List of the number of occupied cells for each column.
               If not given, solution_ships must be set.
        :param row_sums: List of the number of occupied cells for each row.
               If not given, solution_ships must be set.
        :param known_grid: CellGrid of the known cells.
               If not given, will default to all unknown.
        :param curr_grid: CellGrid of the current cells.
               If not given, will default to known_grid.
        :param solution_ships: List of starting column, row, and direction of
               each ship, as a tuple. Direction is True iff ship is row-aligned.
               If not given, puzzle solution is unknown, and both col_sums and
               row_sums must be given.

        Note the solution_grid will be calculated from solution_ships.
        """

        if num_cols < 1 or num_rows < 1:
            raise ValueError("number of columns and rows must be > 0")

        # Perform necessary copies and create lists from iterables
        if known_grid is None:
            known_grid = CellGrid(num_cols, num_rows)
        else:
            known_grid = copy.deepcopy(known_grid)

        if curr_grid is None:
            curr_grid = copy.deepcopy(known_grid)
        else:
            curr_grid = copy.deepcopy(curr_grid)

        ship_lengths = [s for s in ship_lengths]

        if solution_ships is not None:
            solution_ships = [s for s in solution_ships]

        if any(ship < 1 for ship in ship_lengths):
            raise ValueError("ships values must be > 0")
        if known_grid.num_rows != num_rows or known_grid.num_cols != num_cols:
            raise ValueError("known_grid has non matching size")
        if curr_grid.num_rows != num_rows or curr_grid.num_cols != num_cols:
            raise ValueError("curr_grid has non matching size")
        if (col_sums is None) == (solution_ships is None):
            raise ValueError("one of [col_sums, solution_ships] must be set")
        if (row_sums is None) == (solution_ships is None):
            raise ValueError("one of [row_sums, solution_ships] must be set")
        if solution_ships is not None:
            if len(solution_ships) != len(ship_lengths):
                raise ValueError("solution_ships has non matching size")
        if col_sums is not None:
            # Create a new list from the provided sequence
            col_sums = [s for s in col_sums]
            if len(col_sums) != num_cols:
                raise ValueError("col_sums has non matching size")
            if any(col_sum < 0 for col_sum in col_sums):
                raise ValueError("col_sums values must be non negative")
        if row_sums is not None:
            # Create a new list from the provided sequence
            row_sums = [s for s in row_sums]
            if len(row_sums) != num_rows:
                raise ValueError("row_sums has non matching size")
            if any(row_sum < 0 for row_sum in row_sums):
                raise ValueError("row_sums values must be non negative")

        # Standard function arguments validated, set self
        # Note: col_sums, row_sums, solution_ships and solution_grid still need to be checked
        self._num_cols = num_cols
        self._num_rows = num_rows
        self._ship_lengths = ship_lengths
        self._known_grid = known_grid
        self._curr_grid = curr_grid

        # Create solution_grid if ships are given
        if solution_ships is not None:
            solution_grid = CellGrid(num_cols, num_rows)

            for ship_length, solution_ship in zip(ship_lengths, solution_ships):
                start_c, start_r, direction = solution_ship
                ship_all_cells = self.get_ship_all_cells(ship_length,
                                                         start_c,
                                                         start_r,
                                                         direction)
                for c, r in ship_all_cells:
                    if solution_grid.get(c, r).is_occupied():
                        raise ValueError(
                            "solutions_ships invalid: cell at {}, {}".format(
                                c, r))

                if ship_length == 1:
                    solution_grid.set(start_c, start_r, CellState.OccupiedWhole)
                elif direction:
                    # ship is row-aligned, so the covered columns may increase
                    end_c = start_c + ship_length - 1
                    solution_grid.set(start_c, start_r,
                                      CellState.OccupiedEndLeft)
                    for c in range(start_c + 1, end_c - 1):
                        solution_grid.set(c, start_r, CellState.OccupiedMid)
                    solution_grid.set(end_c, start_r,
                                      CellState.OccupiedEndRight)
                else:
                    # ship is column-aligned
                    end_r = start_r + ship_length - 1
                    solution_grid.set(start_c, start_r, CellState.OccupiedEndUp)
                    for r in range(start_r + 1, end_r - 1):
                        solution_grid.set(start_c, r, CellState.OccupiedMid)
                    solution_grid.set(start_c, end_r, CellState.OccupiedEndDown)

            for c in range(num_cols):
                for r in range(num_rows):
                    solution_grid.set(c, r, CellState.Water,
                                      expected_state=CellState.Unknown)

            # Set col_sums and row_sums based on solution_ships
            col_sums = [
                sum([1 if solution_grid.get(c, r).is_occupied() else 0
                     for r in range(num_rows)])
                for c in range(num_cols)]
            row_sums = [
                sum([1 if solution_grid.get(c, r).is_occupied() else 0
                     for c in range(num_cols)])
                for r in range(num_rows)]
        else:
            solution_grid = None

        # Check known_grid agrees with solution_grid
        if solution_grid is not None:
            for c in range(num_cols):
                for r in range(num_rows):
                    if not known_grid.get(c, r).is_unknown():
                        if known_grid.get(c, r) != solution_grid.get(c, r):
                            raise ValueError(
                                "known_grid does not match solution_grid")

        self._solution_ships = solution_ships
        self._solution_grid = solution_grid
        self._col_sums = col_sums
        self._row_sums = row_sums

    @property
    def num_cols(self) -> int:
        return self._num_cols

    @property
    def num_rows(self) -> int:
        return self._num_rows

    @property
    def ship_lengths(self) -> Sequence[int]:
        return self._ship_lengths

    def get_col_sum(self, c: int) -> int:
        """Returns the current number of cells occupied in given column"""
        return self._col_sums[c]

    @property
    def col_sums(self) -> Sequence[int]:
        """Returns the current number of cells occupied in each column"""
        return self._col_sums

    def get_row_sum(self, r: int) -> int:
        """Returns the current number of cells occupied in each row"""
        return self._row_sums[r]

    @property
    def row_sums(self) -> Sequence[int]:
        """Returns the current number of cells occupied in each row"""
        return self._row_sums

    def has_solution(self) -> bool:
        return self._solution_grid is not None

    def get_cell(self, c: int, r: int) -> CellState:
        """
        Gets the visible state of the specified cell.
        :param c: Cell column number
        :param r: Cell row number
        :return: State of the cell
        """
        return self._curr_grid.get(c, r)

    def get_solution_cell(self, c: int, r: int) -> CellState:
        """
        Gets the solution state of the specified cell.
        :param c: Cell column number
        :param r: Cell row number
        :return: State of the cell
        """
        return self._solution_grid.get(c, r)

    def is_cell_known(self, c: int, r: int) -> bool:
        """
        :param c: Cell column number
        :param r: Cell row number
        :return: True iff the cell is known i.e. cannot be changed.
        """
        return not self._known_grid.get(c, r).is_unknown()

    def is_valid(self) -> bool:
        """
        :return: True iff no cells violate known constraints, i.e. without
                 knowing solution.
        """
        # Check row occupied count against sum constraints
        if any([self.get_row_occupied_sum(row) > self._row_sums[row] for row in
                range(self._num_rows)]):
            return False
        # Check column occupied count against sum constraints
        if any([self.get_col_occupied_sum(col) > self._col_sums[col] for
                col in
                range(self._num_cols)]):
            return False
        # Check row water count against sum constraints
        if any([self.get_row_water_sum(row) >
                self._num_cols - self._row_sums[row] for row in
                range(self._num_rows)]):
            return False
        # Check column water count against sum constraints
        if any([self.get_col_water_sum(col) >
                self._num_rows - self._col_sums[col] for col in
                range(self._num_cols)]):
            return False
        return True

    def is_incorrect(self) -> bool:
        """
        :return: True iff solution known and any cell disagrees with solution.
        """
        if self._solution_grid is None:
            return False

        for c in range(self._num_cols):
            for r in range(self._num_rows):
                curr_state = self._curr_grid.get(c, r)
                if curr_state.is_occupied():
                    if not self._solution_grid.get(c, r).is_occupied():
                        return True
                elif curr_state.is_water():
                    if not self._solution_grid.get(c, r).is_water():
                        return True
        return False

    def is_solved(self) -> bool:
        """
        :return: True iff valid, not incorrect and all cells are solved.
        """
        if not self.is_valid() or self.is_incorrect():
            return False

        for c in range(self._num_cols):
            for r in range(self._num_rows):
                if self._curr_grid.get(c, r).is_unknown() or \
                        self._curr_grid.get(c, r) == CellState.OccupiedUnknown:
                    return False
        return True

    def set_cell(self, c: int, r: int, state: CellState) -> None:
        """
        Sets the state of the specified cell.
        If the cell is known, a ValueError will be raised.
        :param c: Cell column number
        :param r: Cell row number
        :param state: Cell state
        """
        if self._known_grid.get(c, r) == CellState.OccupiedUnknown:
            if not state.is_occupied():
                raise ValueError("cannot set a known-to-be-occupied cell")
        elif self._known_grid.get(c, r) != CellState.Unknown:
            raise ValueError("cell is known")

        # TODO should the input be a more basic water|occupied|unknown? Then
        #  the actual state is set based on surroundings
        self._curr_grid.set(c, r, state)

    def __str__(self):
        ruleset_text = "{}x{}, ships: {}".format(self._num_cols, self._num_rows,
                                                 self._ship_lengths)
        row_text_list = [(" ".join([
            self._curr_grid.get(c, r).symbol() for c in range(
                self._num_cols)]) + " " + str(self._row_sums[r]))
                         for r in range(self._num_rows)]

        sum_text = " ".join([str(column_sum) for column_sum in
                             self._col_sums])

        return "\n".join([ruleset_text] + row_text_list + [sum_text])

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Puzzle):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def get_row_occupied_sum(self, r):
        """Returns the current number of cells occupied in this row"""
        return sum(
            [(1 if self._curr_grid.get(c, r).is_occupied() else 0) for c in
             range(self._num_cols)])

    def get_col_occupied_sum(self, c):
        """Returns the current number of cells occupied in this column"""
        return sum(
            [(1 if self._curr_grid.get(c, r).is_occupied() else 0) for r in
             range(self._num_rows)])

    def get_row_water_sum(self, r):
        """Returns the current number of cells water in this row"""
        return sum(
            [(1 if self._curr_grid.get(c, r).is_water() else 0) for c in
             range(self._num_cols)])

    def get_col_water_sum(self, c):
        """Returns the current number of cells water in this column"""
        return sum(
            [(1 if self._curr_grid.get(c, r).is_water() else 0) for r in
             range(self._num_rows)])

    def get_neighbour_cells(self, c: int, r: int) -> Sequence[Tuple[int, int]]:
        """Returns the (up to) 9 cells around and including the given cell as
        tuples of (c, r)"""
        minc = max(c - 1, 0)
        maxc = min(c + 1, self._num_cols - 1)
        minr = max(r - 1, 0)
        maxr = min(r + 1, self._num_rows - 1)

        return [(cd, rd) for cd, rd in itertools.product(
            range(minc, maxc + 1), range(minr, maxr + 1))]

    def get_nondiagonal_neighbour_cells(self, c: int, r: int) \
            -> Sequence[Tuple[int, int]]:
        """Returns the (up to) directly-adjacent 4 cells around the cell as
        tuples of (c, r)"""
        return [(c, r) for c, r
                in [(c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)]
                if 0 <= c < self._num_cols and 0 <= r < self._num_rows]

    def get_diagonal_neighbour_cells(self, c: int, r: int) \
            -> Sequence[Tuple[int, int]]:
        """Returns the (up to) diagonally-adjacents 4 cells around the cell as
        tuples of (c, r)"""
        return [(c, r) for c, r
                in itertools.product([c - 1, c + 1], [r - 1, r + 1])
                if 0 <= c < self._num_cols and 0 <= r < self._num_rows]

    def get_ship_cells(self, ship_length: int, start_c: int, start_r: int,
                       direction: bool) -> Sequence[Tuple[int, int]]:
        """Returns a list of the cells the current ship would occupy"""
        if direction:
            # ship is row-aligned, so the covered columns may increase
            if start_c + ship_length > self._num_cols:
                raise ValueError("Ship does not fit in grid")
            return [(start_c + d, start_r) for d in range(ship_length)]
        else:
            if start_r + ship_length > self._num_rows:
                raise ValueError("Ship does not fit in grid")
            return [(start_c, start_r + d) for d in range(ship_length)]

    def get_ship_neighbour_cells(self,
                                 ship_length: int, start_c: int, start_r: int,
                                 direction: bool) -> Sequence[Tuple[int, int]]:
        """Returns a list of the cells neighbouring the ship, excluding the
        ship."""
        min_c = max(start_c - 1, 0)
        min_r = max(start_r - 1, 0)
        max_c = min(start_c + 1, self._num_cols - 1)
        max_r = min(start_r + 1, self._num_rows - 1)

        if direction:
            # ship is row-aligned, so the covered columns may increase
            max_c = min(self._num_cols - 1, start_c + ship_length)
        else:
            # ship is col-aligned, so the covered rows may increase
            max_r = min(self._num_rows - 1, start_r + ship_length)

        if direction:
            # ship is row-aligned, so the covered columns may increase
            if start_r > 0:
                for c in range(min_c, max_c + 1):
                    yield c, start_r - 1
            if start_r + 1 < self._num_rows:
                for c in range(min_c, max_c + 1):
                    yield c, start_r + 1
            if start_c > 0:
                yield start_c - 1, start_r
            if start_c + ship_length < self._num_cols:
                yield start_c + ship_length, start_r
        else:
            # ship is column-aligned, so the covered rows may increase
            if start_c > 0:
                for r in range(min_r, max_r + 1):
                    yield start_c - 1, r
            if start_c + 1 < self._num_cols:
                for r in range(min_r, max_r + 1):
                    yield start_c + 1, r
            if start_r > 0:
                yield start_c, start_r - 1
            if start_r + ship_length < self._num_rows:
                yield start_c, start_r + ship_length

    def get_ship_all_cells(self,
                           ship_length: int, start_c: int, start_r: int,
                           direction: bool) -> Sequence[Tuple[int, int]]:
        """Returns a list of the cells neighbouring the ship, including the
        ship."""
        min_c = max(start_c - 1, 0)
        min_r = max(start_r - 1, 0)
        max_c = min(start_c + 1, self._num_cols - 1)
        max_r = min(start_r + 1, self._num_rows - 1)

        if direction:
            # ship is row-aligned, so the covered columns may increase
            max_c = min(self._num_cols - 1, start_c + ship_length)
        else:
            # ship is col-aligned, so the covered rows may increase
            max_r = min(self._num_rows - 1, start_r + ship_length)

        return [(c, r) for c, r in itertools.product(range(min_c, max_c + 1),
                                                     range(min_r, max_r + 1))]

    def strip_out_of_bound_cells(self, cells: Iterable[Tuple[int, int]]) -> \
            Iterable[Tuple[int, int]]:
        for c, r in cells:
            if 0 <= c < self._num_cols and 0 <= r < self._num_rows:
                yield c, r

    def can_place_ship(self, ship_length: int, start_c: int, start_r: int,
                       direction: bool) -> bool:
        """Checks if ship could fit in specified location"""
        if 0 > start_r or start_r >= self.num_rows():
            return False
        if 0 > start_c or start_c >= self.num_cols:
            return False
        if direction:
            # ship is row-aligned, so the covered columns may increase
            if start_c + ship_length > self.num_cols:
                return False
            if self.get_row_sum(start_r) < ship_length:
                return False
        else:
            # ship is col-aligned
            if start_r + ship_length > self.num_rows():
                return False
            if self.get_col_sum(start_c) < ship_length:
                return False

        if any(self.get_cell(c, r).is_water() for c, r in self.get_ship_cells(
                ship_length, start_c, start_r, direction)):
            return False

        neighbour_cells = list(
            self.get_ship_neighbour_cells(ship_length, start_c,
                                          start_r,
                                          direction))

        if any(self.get_cell(c, r).is_occupied() for c, r in neighbour_cells):
            return False

        return True


def generate_solved_puzzles(num_cols: int, num_rows: int,
                            ship_lengths: Sequence[int]) -> Iterable[Puzzle]:
    """
    Iterates across all possible solved puzzles for the given puzzle size.
    Uses recursion to place each ship.
    """

    # We recurse through every ship:
    # - try to place it horizontally
    #   - try place it beginning from position 0,0
    #   - continue through every other cell
    # - if it is not a 1-ship, try vertically
    # - once successfully placed, recurse into the next ship
    # - if last ship, output a solution
    # - if not possible to place ship, go back to the previous ship

    solution_ships = [(0, 0, True)] * len(ship_lengths)
    bounding_boxes = [(0, 0, 0, 0)] * len(ship_lengths)

    def get_ship_bounding_box(length: int, start_c: int, start_r: int,
                              row_aligned: bool) -> Tuple[int, int, int, int]:
        min_c = start_c - 1
        max_c = start_c + (length if row_aligned else 1)
        min_r = start_r - 1
        max_r = start_r + (1 if row_aligned else length)
        return min_c, max_c, min_r, max_r

    def bounding_boxes_overlap(bbox1: Tuple[int, int, int, int],
                               bbox2: Tuple[int, int, int, int]) -> bool:
        min_c_1, max_c_1, min_r_1, max_r_1 = bbox1
        min_c_2, max_c_2, min_r_2, max_r_2 = bbox2

        if min_c_1 > max_c_2 or max_c_1 < min_c_2 or \
                min_r_1 > max_r_2 or max_r_1 < min_r_2:
            return False
        else:
            return True

    def can_place_ship(ship_index: int, start_c: int, start_r: int,
                       row_aligned: bool):
        length = ship_lengths[ship_index]
        if not (0 <= start_c < num_cols and 0 <= start_r < num_rows):
            return False
        if row_aligned and start_c + length > num_cols:
            return False
        if not row_aligned and start_r + length > num_rows:
            return False
        bbox = get_ship_bounding_box(length, start_c, start_r, row_aligned)

        for other_bbox in bounding_boxes[0:ship_index - 1]:
            if bounding_boxes_overlap(bbox, other_bbox):
                return False

        return True

    def can_place(x, y):
        """Checks if a ship can be placed to occupy specified cell"""

        if x >= num_cols or y >= num_rows or x < 0 or y < 0:
            return False

        cell_list = self.get_neighbour_cells(x, y)
        return all([cell not in occupied_cells for cell in cell_list])

    def can_place_ship(cells):
        return all([can_place(x, y) for x, y in cells])

    def place_ship(cells):
        for cell in cells:
            occupied_cells.add(cell)

    def remove_ship(cells):
        for cell in cells:
            occupied_cells.remove(cell)

    def make_puzzle():
        """Creates a puzzle from the current state"""

        def cell_state(cell):
            return CellState.OccupiedUnknown if cell in occupied_cells else \
                CellState.Water

        grid = CellGrid(num_cols, num_rows)
        for c in range(num_cols):
            for r in range(num_rows):
                grid.set(c, r, cell_state((c, r)))

        puzzle = Puzzle(num_cols, num_rows, ship_lengths, known_grid=grid)

        return puzzle

    def try_place_ship_and_continue(ship_index):
        # If the last ship was allocated, we're done
        if ship_index >= len(ship_lengths):
            yield make_puzzle()
        else:
            # If the ship is longer than 1, we try place it both ways
            direction_list = [0, 1] if ship_lengths[ship_index] > 1 else [1]

            for x in range(num_cols):
                for y in range(num_rows):
                    for direction in direction_list:
                        ship_cells = get_ship_cells(ship_lengths[ship_index],
                                                    x, y, direction)
                        if can_place_ship(ship_cells):
                            place_ship(ship_cells)
                            yield from try_place_ship_and_continue(
                                ship_index + 1)
                            remove_ship(ship_cells)

    yield from try_place_ship_and_continue(0)
