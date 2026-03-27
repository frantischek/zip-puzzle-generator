def solve_unique_path(grid: list, walls: list, step_cap: int = 300_000):
    """Returns (path, stats) or (None, stats).

    Uses iterative DFS to avoid Python function-call overhead.
    Counts solutions: returns the path only if exactly one exists.
    """
    h, w = len(grid), len(grid[0])
    total = h * w

    # Find start/end cells
    start = (0, 0)
    end = (h - 1, w - 1)
    max_val = -1
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v is not None:
                if v == 1:
                    start = (r, c)
                if v > max_val:
                    max_val = v
                    end = (r, c)

    # Build barrier set (flat tuples for O(1) lookup)
    barrier_set: set = set()
    for wall in walls:
        r1, c1 = wall["cell1"]
        r2, c2 = wall["cell2"]
        barrier_set.add((r1, c1, r2, c2))
        barrier_set.add((r2, c2, r1, c1))

    # Pre-compute adjacency lists
    adj = [[[] for _ in range(w)] for _ in range(h)]
    for r in range(h):
        for c in range(w):
            nbs = []
            for dr, dc in ((0, -1), (0, 1), (1, 0), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    nbs.append((nr, nc))
            adj[r][c] = nbs

    visited = [[False] * w for _ in range(h)]
    path = []  # current path as list of (r, c)
    solutions = 0
    result = None
    stats = {
        "solver_steps": 0,
        "branch_count": 0,
        "dead_end_count": 0,
        "forced_move_count": 0,
        "max_depth_reached": 0,
    }

    # Stack entries: (r, c, curr_num, neighbor_idx, is_entering)
    # is_entering=True means we're visiting this cell for the first time
    sr, sc = start
    stack = [(sr, sc, 1, 0, True)]

    while stack:
        if solutions > 1:
            break
        stats["solver_steps"] += 1
        if stats["solver_steps"] > step_cap:
            solutions = 2
            break

        r, c, curr_num, ni, entering = stack[-1]

        if entering:
            if visited[r][c]:
                stack.pop()
                continue
            visited[r][c] = True
            path.append((r, c))
            if len(path) > stats["max_depth_reached"]:
                stats["max_depth_reached"] = len(path)
            stack[-1] = (r, c, curr_num, 0, False)

            if r == end[0] and c == end[1] and len(path) == total:
                solutions += 1
                result = list(path)
                path.pop()
                visited[r][c] = False
                stack.pop()
                continue
            continue

        neighbors = adj[r][c]
        candidates = []
        for idx in range(ni, len(neighbors)):
            nr, nc = neighbors[idx]

            if visited[nr][nc]:
                continue
            if (r, c, nr, nc) in barrier_set:
                continue
            cell_val = grid[nr][nc]
            if cell_val is not None and cell_val != curr_num + 1:
                continue

            new_num = cell_val if cell_val is not None else curr_num
            candidates.append((idx + 1, nr, nc, new_num))

        if not candidates:
            stats["dead_end_count"] += 1
            path.pop()
            visited[r][c] = False
            stack.pop()
            continue

        if len(candidates) == 1:
            stats["forced_move_count"] += 1
        else:
            stats["branch_count"] += 1

        next_ni, nr, nc, new_num = candidates[0]
        stack[-1] = (r, c, curr_num, next_ni, False)
        stack.append((nr, nc, new_num, 0, True))

    found_path = result if solutions == 1 else None
    return found_path, stats
