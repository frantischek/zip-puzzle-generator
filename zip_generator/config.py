from typing import Tuple

Coord = Tuple[int, int]

DIFFICULTY_CONFIG = {
    "easy": {
        "grid_size": 6,
        "min_dot_count": 5,
        "max_dot_count": 7,
        "min_spacing": 2,
        "min_checkpoint_distance": 2,
        "retry_attempts": 10_000,
        "min_wall_count": 4,
        "max_wall_count": 7,
        "wall_probability": 0.8,
        "path_adjacent_wall_ratio": 0.5,
        "min_solver_steps": 500,
        "solver_step_cap": 300_000,
    },
    "medium": {
        "grid_size": 7,
        "min_dot_count": 4,
        "max_dot_count": 8,
        "min_spacing": 3,
        "min_checkpoint_distance": 3,
        "retry_attempts": 30_000,
        "min_wall_count": 10,
        "max_wall_count": 16,
        "wall_probability": 1.0,
        "path_adjacent_wall_ratio": 0.6,
        "min_solver_steps": 800,
        "solver_step_cap": 600_000,
    },
    "hard": {
        "grid_size": 8,
        "min_dot_count": 6,
        "max_dot_count": 10,
        "min_spacing": 3,
        "min_checkpoint_distance": 4,
        "retry_attempts": 50_000,
        "min_wall_count": 16,
        "max_wall_count": 24,
        "wall_probability": 1.0,
        "path_adjacent_wall_ratio": 0.7,
        "min_solver_steps": 1_000,
        "solver_step_cap": 2_000_000,
    },
}
