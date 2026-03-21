# tests/test_solver/test_hill_climbing.py
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
