def solve_unique_path(grid: list, walls: list, step_cap: int = 300_000):
    """Returns (path, stats) or (None, stats).

    Uses iterative DFS to avoid Python function-call overhead.
    Counts solutions: returns the path only if exactly one exists.

    Pruning: tracks the number of unvisited accessible neighbours for each
    cell (free_count).  When visiting a cell reduces a neighbour's free_count
    to zero, that neighbour becomes a dead-end.  Unless it is the very last
    cell to be visited (the endpoint when only one cell remains), the current
    branch cannot complete a Hamiltonian path and is abandoned immediately.
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

    # Pre-compute two adjacency structures:
    #   adj          – all in-bounds neighbours (walls checked during search)
    #   adj_walkable – neighbours not blocked by a wall (used for free_count)
    adj = [[[] for _ in range(w)] for _ in range(h)]
    adj_walkable = [[[] for _ in range(w)] for _ in range(h)]
    for r in range(h):
        for c in range(w):
            nbs_all = []
            nbs_walk = []
            for dr, dc in ((0, -1), (0, 1), (1, 0), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    nbs_all.append((nr, nc))
                    if (r, c, nr, nc) not in barrier_set:
                        nbs_walk.append((nr, nc))
            adj[r][c] = nbs_all
            adj_walkable[r][c] = nbs_walk

    # free_count[r][c] = number of unvisited walkable neighbours of (r,c)
    free_count = [[len(adj_walkable[r][c]) for c in range(w)] for r in range(h)]

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

    er, ec = end

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

            if r == er and c == ec and len(path) == total:
                solutions += 1
                result = list(path)
                # Backtrack: restore free_count for neighbours
                for nr, nc in adj_walkable[r][c]:
                    free_count[nr][nc] += 1
                path.pop()
                visited[r][c] = False
                stack.pop()
                continue

            # Isolated-cell pruning: update free_count for walkable neighbours.
            # If any unvisited neighbour loses its last free connection it
            # becomes unreachable – prune this branch unless it is the end
            # cell and only one unvisited cell remains.
            remaining = total - len(path)
            isolated = False
            for nr, nc in adj_walkable[r][c]:
                free_count[nr][nc] -= 1
                if not visited[nr][nc] and free_count[nr][nc] == 0:
                    if not (nr == er and nc == ec and remaining == 1):
                        isolated = True

            if isolated:
                # Restore free_count and immediately backtrack
                for nr, nc in adj_walkable[r][c]:
                    free_count[nr][nc] += 1
                path.pop()
                visited[r][c] = False
                stats["dead_end_count"] += 1
                stack.pop()
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
            # Restore free_count before backtracking
            for nr, nc in adj_walkable[r][c]:
                free_count[nr][nc] += 1
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
