import random as _random_module
from typing import List, Optional

def _count_free(x: int, y: int, visited: list, n: int) -> int:
    count = 0
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < n and 0 <= ny < n and not visited[ny][nx]:
            count += 1
    return count

def generate_hamiltonian_path(n: int, rng: _random_module.Random) -> Optional[List[dict]]:
    total = n * n
    start_x = rng.randint(0, n - 1)
    start_y = rng.randint(0, n - 1)

    stack = [{"x": start_x, "y": start_y}]
    visited = [[False] * n for _ in range(n)]
    visited[start_y][start_x] = True

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    max_iterations = total * 1000
    iteration = 0

    while stack and iteration < max_iterations:
        iteration += 1

        if len(stack) == total:
            return stack

        curr = stack[-1]
        cx, cy = curr["x"], curr["y"]
        rng.shuffle(dirs)

        candidates = []
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < n and 0 <= ny < n and not visited[ny][nx]:
                free = _count_free(nx, ny, visited, n)
                candidates.append({"x": nx, "y": ny, "free": free})

        if not candidates:
            last = stack.pop()
            visited[last["y"]][last["x"]] = False
            continue

        # 30% chance to pick a degree-1 neighbour (bottleneck bias)
        deg1 = [c for c in candidates if c["free"] == 1]
        if deg1 and rng.randint(1, 10) <= 3:
            nxt = rng.choice(deg1)
        else:
            # Warnsdorff: fewest onward moves first
            candidates.sort(key=lambda c: c["free"])
            nxt = candidates[0]

        visited[nxt["y"]][nxt["x"]] = True
        stack.append({"x": nxt["x"], "y": nxt["y"]})

    return None

def randomize_path(path: List[dict], grid_size: int, rng: _random_module.Random) -> List[dict]:
    rotation = rng.randint(0, 3)
    mirror_h = rng.choice([True, False])
    mirror_v = rng.choice([True, False])
    reverse = rng.choice([True, False])
    n = grid_size - 1

    def transform(cell):
        x, y = cell["x"], cell["y"]
        for _ in range(rotation):
            x, y = y, n - x
        if mirror_h:
            x = n - x
        if mirror_v:
            y = n - y
        return {"x": x, "y": y}

    result = [transform(c) for c in path]
    if reverse:
        result.reverse()
    return result

def place_checkpoints(path: List[dict], count: int, min_spacing: int,
                      rng: _random_module.Random,
                      min_checkpoint_distance: int = 0) -> Optional[List[dict]]:
    path_len = len(path)
    if count < 2 or path_len < (count - 1) * min_spacing + 1:
        return None

    indices = [0]
    last_idx = 0

    for i in range(1, count - 1):
        remaining_after = count - 1 - i
        min_idx = last_idx + min_spacing
        max_idx = path_len - 1 - remaining_after * min_spacing
        if min_idx > max_idx:
            return None

        if min_checkpoint_distance > 0:
            prev = path[last_idx]
            far = [
                idx for idx in range(min_idx, max_idx + 1)
                if (abs(path[idx]["x"] - prev["x"]) +
                    abs(path[idx]["y"] - prev["y"])) >= min_checkpoint_distance
            ]
            next_idx = rng.choice(far) if far else rng.randint(min_idx, max_idx)
        else:
            next_idx = rng.randint(min_idx, max_idx)

        indices.append(next_idx)
        last_idx = next_idx

    indices.append(path_len - 1)

    # Reject if the final segment doesn't meet the distance requirement
    if min_checkpoint_distance > 0:
        p1, p2 = path[indices[-2]], path[indices[-1]]
        if abs(p1["x"] - p2["x"]) + abs(p1["y"] - p2["y"]) < min_checkpoint_distance:
            return None

    return [
        {"x": path[idx]["x"], "y": path[idx]["y"], "number": num + 1}
        for num, idx in enumerate(indices)
    ]
