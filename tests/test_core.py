from zip_generator.config import DIFFICULTY_CONFIG
from zip_generator.generator import generate_puzzle, try_generate
from zip_generator.pathing import generate_hamiltonian_path, place_checkpoints
from zip_generator.validation import verify_solution_connectivity


def test_generate_hamiltonian_path_covers_board():
    import random
    rng = random.Random(1234)
    path = generate_hamiltonian_path(6, rng)
    assert path is not None
    assert len(path) == 36


def test_place_checkpoints_are_numbered():
    path = [{"x": i, "y": 0} for i in range(10)]
    import random
    rng = random.Random(1)
    checkpoints = place_checkpoints(path, count=4, min_spacing=2, rng=rng)
    assert checkpoints is not None
    assert [c["number"] for c in checkpoints] == [1, 2, 3, 4]


def test_verify_solution_connectivity_detects_blocking_wall():
    solution_path = [{"x": 0, "y": 0}, {"x": 1, "y": 0}]
    walls = [{"cell1": [0, 0], "cell2": [0, 1]}]
    assert verify_solution_connectivity(solution_path, walls) is False


def test_try_generate_medium_returns_valid_shape():
    import random
    rng = random.Random(1234)
    result = try_generate(DIFFICULTY_CONFIG["medium"], rng)
    assert result is None or {
        "grid_size",
        "checkpoints",
        "solution_path",
        "checkpoint_count",
        "walls",
        "solver_steps",
    }.issubset(result.keys())


def test_generate_puzzle_invalid_difficulty_raises():
    import pytest
    with pytest.raises(ValueError):
        generate_puzzle("invalid", seed=1)
