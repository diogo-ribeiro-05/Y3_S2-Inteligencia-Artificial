# tests/test_solver/test_hill_climbing.py
import random
from src.models.photo import Photo
from src.solver.hill_climbing import HillClimbingSolver


def test_generate_initial_solution_horizontal_only():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
        Photo(2, 'H', {'c'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    assert len(solution) == 3
    # All photos should be used
    used_ids = set()
    for slide in solution.slides:
        used_ids.update(slide.photo_ids)
    assert used_ids == {0, 1, 2}


def test_generate_initial_solution_vertical_pairing():
    photos = [
        Photo(0, 'V', {'a'}),
        Photo(1, 'V', {'b'}),
        Photo(2, 'V', {'c'}),
        Photo(3, 'V', {'d'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    # 4 vertical photos = 2 slides
    assert len(solution) == 2
    for slide in solution.slides:
        assert slide.is_vertical_slide
        assert len(slide.photo_ids) == 2


def test_generate_initial_solution_mixed():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'V', {'b'}),
        Photo(2, 'V', {'c'}),
        Photo(3, 'H', {'d'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    # 2 horizontal + 2 vertical (paired) = 3 slides
    assert len(solution) == 3


def test_swap_slides():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
        Photo(2, 'H', {'c'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    neighbor = solver._swap_slides(solution)

    # Should have same number of slides
    assert len(neighbor) == len(solution)
    # Should contain same photo IDs
    original_ids = set()
    neighbor_ids = set()
    for s in solution.slides:
        original_ids.update(s.photo_ids)
    for s in neighbor.slides:
        neighbor_ids.update(s.photo_ids)
    assert original_ids == neighbor_ids


def test_get_neighbor_preserves_validity():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'V', {'b'}),
        Photo(2, 'V', {'c'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    neighbor = solver.get_neighbor(solution)
    # Verify all slides are still valid
    for slide in neighbor.slides:
        assert slide.is_horizontal_slide or slide.is_vertical_slide


def test_solve_improves_or_maintains_score():
    random.seed(42)  # For reproducibility
    photos = [
        Photo(0, 'H', {'a', 'b', 'c'}),
        Photo(1, 'H', {'a', 'b', 'd'}),
        Photo(2, 'H', {'a', 'c', 'd'}),
        Photo(3, 'H', {'b', 'c', 'd'}),
    ]
    solver = HillClimbingSolver(photos)
    initial = solver.generate_initial_solution()
    initial_score = initial.calculate_score()

    final = solver.solve(max_iterations=100)
    final_score = final.calculate_score()

    # Score should improve or stay same
    assert final_score >= initial_score


def test_solve_populates_history():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]
    solver = HillClimbingSolver(photos)
    solver.solve(max_iterations=10)

    assert len(solver.history) == 10


def test_solve_callback():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]
    solver = HillClimbingSolver(photos)
    callback_calls = []

    def callback(iteration, score):
        callback_calls.append((iteration, score))

    solver.solve(max_iterations=5, callback=callback)

    assert len(callback_calls) == 5


def test_solve_can_be_stopped():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]
    solver = HillClimbingSolver(photos)

    def stop_early(iteration, score):
        if iteration >= 3:
            solver.request_stop()

    result = solver.solve(max_iterations=100, callback=stop_early)

    # Should have stopped early
    assert len(solver.history) < 100
