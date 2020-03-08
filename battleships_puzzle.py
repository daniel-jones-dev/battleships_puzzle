import puzzle
import solver
import example_puzzles


def solve_puzzle(puzzle_to_solve):
    simple_solver = solver.Solver(puzzle_to_solve)

    step_count = 1

    while True:
        print(puzzle_to_solve)
        if puzzle_to_solve.is_solved():
            print("Puzzle is solved")
            break

        step = simple_solver.solve_step()
        print("Step {}:".format(step_count))
        print(step)
        step_count += 1
        if len(step.solved_cells) == 0:
            print("Could not find any cells to solve")
            break
        else:
            simple_solver.do_step(step)


p = example_puzzles.get_example_puzzle(3)

solve_puzzle(p)
