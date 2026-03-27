import random as _random_module
import time
from typing import List, Optional

from .config import DIFFICULTY_CONFIG
from .pathing import generate_hamiltonian_path, randomize_path, place_checkpoints
from .solver import solve_unique_path
from .validation import verify_solution_connectivity, covers_whole_board, quick_validity_check

def generate_walls(grid_size: int, solution_path: List[dict], checkpoints: List[dict],
                   config: dict, rng: _random_module.Random) -> list:
    if rng.random() > config["wall_probability"]:
        return []

    wall_count = rng.randint(config["min_wall_count"], config["max_wall_count"])
    if wall_count <= 0:
        return []

    # Build set of solution segments (normalised)
    sol_segs = set()
    for i in range(len(solution_path) - 1):
        p1 = (solution_path[i]["x"], solution_path[i]["y"])
        p2 = (solution_path[i + 1]["x"], solution_path[i + 1]["y"])
        seg = tuple(sorted([p1, p2]))
        sol_segs.add(seg)

    # All possible internal edges not on the solution path
    all_walls = []
    for y in range(grid_size):
        for x in range(grid_size):
            if x < grid_size - 1:
                seg = tuple(sorted([(x, y), (x + 1, y)]))
                if seg not in sol_segs:
                    all_walls.append(((x, y), (x + 1, y)))
            if y < grid_size - 1:
                seg = tuple(sorted([(x, y), (x, y + 1)]))
                if seg not in sol_segs:
                    all_walls.append(((x, y), (x, y + 1)))

    # Split: path-adjacent walls vs others
    path_cells = {(c["x"], c["y"]) for c in solution_path}

    path_adj = []
    other = []
    for w in all_walls:
        if w[0] in path_cells or w[1] in path_cells:
            path_adj.append(w)
        else:
            other.append(w)

    ratio = config.get("path_adjacent_wall_ratio", 0.7)
    adj_count = min(len(path_adj), int(wall_count * ratio + 0.5))
    other_count = min(len(other), wall_count - adj_count)

    rng.shuffle(path_adj)
    rng.shuffle(other)

    selected = path_adj[:adj_count] + other[:other_count]

    # Fill up if not enough
    if len(selected) < wall_count:
        remaining = path_adj[adj_count:]
        selected += remaining[: wall_count - len(selected)]

    # Convert to [row, col] format
    return [
        {"cell1": [w[0][1], w[0][0]], "cell2": [w[1][1], w[1][0]]}
        for w in selected
    ]

def try_generate(config: dict, rng: _random_module.Random):
    """Returns puzzle dict or None."""
    grid_size = config["grid_size"]
    n = grid_size

    # 1. Hamiltonian path
    path = generate_hamiltonian_path(n, rng)
    if path is None:
        return None

    # 2. Geometric randomisation
    path = randomize_path(path, n, rng)

    # 3. Determine checkpoint count
    path_len = len(path)
    max_possible = (path_len - 1) // config["min_spacing"] + 1
    if max_possible < config["min_dot_count"]:
        return None
    upper = min(config["max_dot_count"], max_possible)
    cp_count = rng.randint(config["min_dot_count"], upper)

    # 4. Place checkpoints
    checkpoints = place_checkpoints(
        path, cp_count, config["min_spacing"], rng,
        config.get("min_checkpoint_distance", 0),
    )
    if checkpoints is None:
        return None

    # 5-11. Try multiple wall configurations for the same path+checkpoints.
    # Many random wall sets fail the uniqueness check; retrying with different
    # walls (same rng, advancing state each call) raises the success rate
    # significantly without regenerating the full path each time.

    # Build grid once – it doesn't depend on walls
    grid = [[None] * n for _ in range(n)]
    for cp in checkpoints:
        grid[cp["y"]][cp["x"]] = cp["number"]

    min_steps = config.get("min_solver_steps", 0)
    wall_retries = config.get("wall_retry_attempts", 8)

    for _ in range(wall_retries):
        # 5. Generate walls (strategic placement)
        walls = generate_walls(grid_size, path, checkpoints, config, rng)

        # 6. Verify solution path isn't blocked by walls
        if not verify_solution_connectivity(path, walls):
            continue

        # 7. Board connectivity check
        if not covers_whole_board(checkpoints, walls, grid_size):
            continue

        # 8. Quick BFS reachability between consecutive checkpoints
        if not quick_validity_check(walls, checkpoints, grid_size):
            continue

        # 9. Verify unique solution via backtracking solver
        solver_path, solver_stats = solve_unique_path(
            grid, walls, step_cap=config["solver_step_cap"]
        )
        if isinstance(solver_stats, int):
            solver_stats = {
                "solver_steps": solver_stats,
                "branch_count": 0,
                "dead_end_count": 0,
                "forced_move_count": 0,
                "max_depth_reached": 0,
            }

        if solver_path is None:
            continue

        # 10. Difficulty filter: reject if too easy
        if min_steps > 0 and solver_stats["solver_steps"] < min_steps:
            continue

        # Convert solver path [row,col] -> {"x": col, "y": row}
        solution_path = [{"x": c, "y": r} for r, c in solver_path]

        return {
            "grid_size": grid_size,
            "checkpoints": checkpoints,
            "solution_path": solution_path,
            "checkpoint_count": cp_count,
            "walls": walls,
            "solver_steps": solver_stats["solver_steps"],
            "branch_count": solver_stats["branch_count"],
            "dead_end_count": solver_stats["dead_end_count"],
            "forced_move_count": solver_stats["forced_move_count"],
            "max_depth_reached": solver_stats["max_depth_reached"],
        }

    return None


def select_candidate(candidates: List[dict], difficulty: str) -> dict:
    """Select a candidate based on the computed difficulty score.

    easy   -> easiest valid candidate
    medium -> middle candidate after sorting by score
    hard   -> hardest valid candidate
    """
    if not candidates:
        raise ValueError("No candidates available")

    ranked = sorted(candidates, key=lambda c: c["difficulty_score_raw"])

    if difficulty == "easy":
        return ranked[0]
    if difficulty == "hard":
        return ranked[-1]

    # medium: prefer the middle instead of the absolute easiest/hardest
    return ranked[len(ranked) // 2]

def generate_puzzle(difficulty: str = "medium", seed: Optional[int] = None) -> dict:
    config = DIFFICULTY_CONFIG.get(difficulty)
    if config is None:
        raise ValueError(f"Unknown difficulty: {difficulty}")

    base_seed = seed if seed is not None else int(time.time() * 1000) % (2**31)
    max_attempts = config["retry_attempts"]
    started = time.time()

    pool_size = config.get(
        "candidate_pool_size",
        1 if difficulty == "easy" else 3 if difficulty == "medium" else 5,
    )
    scan_limit = min(
        max_attempts,
        config.get(
            "candidate_scan_attempts",
            20 if difficulty == "easy" else 80 if difficulty == "medium" else 160,
        ),
    )
    min_attempts_before_selection = config.get(
        "min_attempts_before_selection",
        1 if difficulty == "easy" else 12 if difficulty == "medium" else 40,
    )
    max_no_new_candidate_streak = config.get(
        "max_no_new_candidate_streak",
        8 if difficulty == "easy" else 10 if difficulty == "medium" else 40,
    )

    candidates: List[dict] = []
    scanned_attempts = 0
    no_new_candidate_streak = 0

    for attempt in range(scan_limit):
        scanned_attempts = attempt + 1
        attempt_seed = base_seed + attempt
        rng = _random_module.Random(attempt_seed)
        result = try_generate(config, rng)
        if result is None:
            no_new_candidate_streak += 1
            if (
                len(candidates) >= pool_size
                and scanned_attempts >= min_attempts_before_selection
            ):
                break
            if (
                candidates
                and scanned_attempts >= min_attempts_before_selection
                and no_new_candidate_streak >= max_no_new_candidate_streak
            ):
                break
            continue
        no_new_candidate_streak = 0
        result["seed"] = attempt_seed
        result["attempts"] = attempt + 1
        result["difficulty_score_raw"] = (
            result["solver_steps"]
            + result["branch_count"] * 50
            + result["dead_end_count"] * 20
            - result["forced_move_count"] * 5
        )
        result["difficulty_score"] = round(result["difficulty_score_raw"] / 1000, 1)
        candidates.append(result)

        if (
            len(candidates) >= pool_size
            and scanned_attempts >= min_attempts_before_selection
        ):
            break

    elapsed = time.time() - started

    if not candidates:
        return {
            "error": True,
            "message": f"Failed after {scanned_attempts} scanned attempts ({elapsed:.1f}s) for difficulty '{difficulty}'",
        }

    best = select_candidate(candidates, difficulty)
    best["elapsed_seconds"] = round(elapsed, 2)
    best["collected_candidates"] = len(candidates)
    best["target_candidate_pool_size"] = pool_size
    best["scanned_attempts"] = scanned_attempts
    best["error"] = False
    return best
