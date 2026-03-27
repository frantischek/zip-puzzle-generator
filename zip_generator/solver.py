def solve_unique_path(grid: list, walls: list, step_cap: int = 300_000):
    """Returns (path, steps) or (None, steps).

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
    steps = 0

    # Stack entries: (r, c, curr_num, neighbor_idx, is_entering)
    # is_entering=True means we're visiting this cell for the first time
    sr, sc = start
    stack = [(sr, sc, 1, 0, True)]

    while stack:
        if solutions > 1:
            break
        steps += 1
        if steps > step_cap:
            solutions = 2
            break

        r, c, curr_num, ni, entering = stack[-1]

        if entering:
            # First visit: mark visited, add to path
            if visited[r][c]:
                stack.pop()
                continue
            visited[r][c] = True
            path.append((r, c))
            stack[-1] = (r, c, curr_num, 0, False)

            # Check if we reached the goal
            if r == end[0] and c == end[1] and len(path) == total:
                solutions += 1
                result = list(path)
                # Backtrack to continue searching for more solutions
                path.pop()
                visited[r][c] = False
                stack.pop()
                continue
            continue

        # Explore neighbors from index ni onward
        neighbors = adj[r][c]
        found_next = False
        while ni < len(neighbors):
            nr, nc = neighbors[ni]
            ni += 1

            if visited[nr][nc]:
                continue
            if (r, c, nr, nc) in barrier_set:
                continue
            cell_val = grid[nr][nc]
            if cell_val is not None and cell_val != curr_num + 1:
                continue

            new_num = cell_val if cell_val is not None else curr_num
            # Save our progress and push the new cell
            stack[-1] = (r, c, curr_num, ni, False)
            stack.append((nr, nc, new_num, 0, True))
            found_next = True
            break

        if not found_next:
            # All neighbors exhausted — backtrack
            path.pop()
            visited[r][c] = False
            stack.pop()

    found_path = result if solutions == 1 else None
    return found_path, steps
