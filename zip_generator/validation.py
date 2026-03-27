from typing import List

def verify_solution_connectivity(solution_path: List[dict], walls: list) -> bool:
    if not walls:
        return True

    wall_set = set()
    for w in walls:
        r1, c1 = w["cell1"]
        r2, c2 = w["cell2"]
        wall_set.add((r1, c1, r2, c2))
        wall_set.add((r2, c2, r1, c1))

    for i in range(len(solution_path) - 1):
        p1 = solution_path[i]
        p2 = solution_path[i + 1]
        dx = abs(p1["x"] - p2["x"])
        dy = abs(p1["y"] - p2["y"])
        if dx + dy != 1:
            return False
        # Check wall (in row,col format)
        r1, c1 = p1["y"], p1["x"]
        r2, c2 = p2["y"], p2["x"]
        if (r1, c1, r2, c2) in wall_set:
            return False

    return True

def covers_whole_board(checkpoints: list, walls: list, grid_size: int) -> bool:
    cps = sorted(checkpoints, key=lambda c: c["number"])
    sr, sc = cps[0]["y"], cps[0]["x"]

    wall_set = set()
    for w in walls:
        r1, c1 = w["cell1"]
        r2, c2 = w["cell2"]
        wall_set.add((r1, c1, r2, c2))
        wall_set.add((r2, c2, r1, c1))

    stack = [(sr, sc)]
    seen = {(sr, sc)}
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < grid_size and 0 <= nc < grid_size and (nr, nc) not in seen:
                if (r, c, nr, nc) not in wall_set:
                    seen.add((nr, nc))
                    stack.append((nr, nc))

    return len(seen) == grid_size * grid_size

def quick_validity_check(walls: list, checkpoints: list, grid_size: int) -> bool:
    if len(checkpoints) < 2:
        return False

    wall_set = set()
    for w in walls:
        r1, c1 = w["cell1"]
        r2, c2 = w["cell2"]
        wall_set.add((r1, c1, r2, c2))
        wall_set.add((r2, c2, r1, c1))

    cps = sorted(checkpoints, key=lambda c: c["number"])

    for i in range(len(cps) - 1):
        sr, sc = cps[i]["y"], cps[i]["x"]
        tr, tc = cps[i + 1]["y"], cps[i + 1]["x"]

        queue = [(sr, sc)]
        seen = {(sr, sc)}
        found = False

        while queue:
            r, c = queue.pop(0)
            if r == tr and c == tc:
                found = True
                break
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < grid_size and 0 <= nc < grid_size and (nr, nc) not in seen:
                    if (r, c, nr, nc) not in wall_set:
                        seen.add((nr, nc))
                        queue.append((nr, nc))

        if not found:
            return False

    return True
