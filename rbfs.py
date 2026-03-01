"""
gbfs.py – Greedy Best-First Search  f(n) = h(n)
"""
import heapq
import time
from grid import get_neighbors


def gbfs(grid, start, goal, heuristic):
    """
    Generator that yields one step at a time for animation.
    Each yield: (kind, visited_set, frontier_set, path_list, nodes_visited, cost, elapsed_ms)
    kind = 'step' | 'done' | 'no_path'
    """
    h = heuristic
    open_set = [(h(start, goal), 0, start)]
    counter = 1
    came_from = {start: None}
    visited = set()
    nodes_visited = 0
    start_time = time.time()

    while open_set:
        _, _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)
        nodes_visited += 1

        frontier = {n for _, _, n in open_set}
        yield ('step', visited.copy(), frontier, [], nodes_visited, 0, 0)

        if current == goal:
            # Reconstruct path
            path, node = [], goal
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            elapsed = (time.time() - start_time) * 1000
            yield ('done', visited, set(), path, nodes_visited, len(path) - 1, elapsed)
            return

        for nb in get_neighbors(current, grid):
            if nb not in visited and nb not in came_from:
                came_from[nb] = current
                heapq.heappush(open_set, (h(nb, goal), counter, nb))
                counter += 1

    elapsed = (time.time() - start_time) * 1000
    yield ('no_path', visited, set(), [], nodes_visited, 0, elapsed)
