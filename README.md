# Battleships Puzzle #

This project started out of interest in the Battleships puzzle. The puzzle is a
variant of the two-player game, but instead intended for one-player, and
involving more logic than chance. 

General interests/directions of this project are:
- do some puzzles have multiple solutions?
- are all puzzles with unique solutions solvable with logical reasoning
  (excluding brute-force-search)?
- what are some examples of puzzles requiring very complicated logic, and can
  these rules be explained?
- how does varying the puzzle affect the above? For example, the grid size
  and shape, the number and size of ships in the fleet.

## Rules of the puzzle ##
A fleet of ships of various sizes is hidden in a square grid of 10x10 squares.
The fleet includes one battleship four squares long, two cruises three
squares long, three destroyers two squares long, and four submarines one
square  in size. Each ship occupies a number of contiguous squares on the
grid, arranged horizontally or vertically. The ships are placed so that no
ship touches any other ship, not even diagonally. 

![Example of a solved Battleships puzzle](
    300px-Solved_Solitaire_Battleships.svg.png
    "Example of a solved Battleships puzzle")

Example of a solved Battleships puzzle
(Note: image sourced from Wikipedia, reproduced under CC BY_SA 3.0 license)

The goal of the puzzle is to discover where the ships are located. A grid may
start with clues in the form of squares that have already been solved,
showing a submarine, an end piece of a ship, a middle piece of a ship, or water.
Each row and column also has a number beside it, indicating the number of
squares occupied by ship parts in that row or column, respectively.

## Terminology ##
Some terms used by this project:
- fleet - all ships in a puzzle
- N-ship - a ship of length N, e.g. "the 4-ship"
- cell states:
    * water - a cell with no ship segment in it
    * occupied - a cell with a ship segment in it.
      The cell state occupied may be further divided into:
       - whole - a cell that contains a 1-ship (ie. submarine). 
       - end - a cell that contains the end of a 2+-ship.
       - mid - a cell that contains a mid-section of a 3+ ship.
      The end and mid states also specify a direction (4 options for an end
       cell, 2 for a mid cell)
    * unknown - a cell which could be either water or occupied
- line sum - the total number of cells in a row or column that contain ship
 segments 
- ruleset - the grid-dimensions and fleet composition. The standard ruleset
 is 10x10 with one 4-ship, two 3-ships, three 2-ships and four 1-ships.
- solution - a fully-solved grid, with locations of all ships known
- puzzle - a partially-solved grid, with ruleset and line sums known, but
 some (or all) cells unknown.
- solvable puzzle - a puzzle with a unique solution.
 
 