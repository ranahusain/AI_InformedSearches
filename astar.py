"""
astar.py – A* Search  f(n) = g(n) + h(n)
"""
import heapq
import time
from grid import get_neighbors


def astar(grid, start, goal, heuristic):
    """
    Generator that yields one step at a time for animation.
    Each yield: (kind, visited_set, frontier_set, path_list, nodes_visited, cost, elapsed_ms)
    kind = 'step' | 'done' | 'no_path'
    """
    h = heuristic
    open_set = [(h(start, goal), 0, start)]
    counter = 1
    came_from = {start: None}
    g_score = {start: 0}
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
            path, node = [], goal
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            elapsed = (time.time() - start_time) * 1000
            yield ('done', visited, set(), path, nodes_visited, round(g_score[goal], 2), elapsed)
            return

        for nb in get_neighbors(current, grid):
            tentative_g = g_score[current] + 1
            if nb not in g_score or tentative_g < g_score[nb]:
                g_score[nb] = tentative_g
                came_from[nb] = current
                f = tentative_g + h(nb, goal)
                heapq.heappush(open_set, (f, counter, nb))
                counter += 1

    elapsed = (time.time() - start_time) * 1000
    yield ('no_path', visited, set(), [], nodes_visited, 0, elapsed)
