"""
grid.py – Shared grid setup, colours, and drawing helpers.
"""
import math
import pygame

# Grid size
ROWS, COLS = 8, 8
CELL = 70          # px per cell
PANEL_W = 200      # right panel width

WIN_W = COLS * CELL + PANEL_W
WIN_H = ROWS * CELL

FPS = 30
STEP_DELAY = 120   # ms between animation steps

# Cell types
EMPTY, WALL, START, GOAL = 0, 1, 2, 3

# Colours
WHITE = (255, 255, 255)
BLACK = (20,  20,  20)
GRAY = (160, 160, 160)
START_C = (50,  200,  80)   # green
GOAL_C = (220,  50,  50)   # red
WALL_C = (40,   40,  40)
FRONT_C = (255, 220,   0)   # yellow  – frontier
VISIT_C = (100, 149, 237)   # blue    – visited
PATH_C = (50,  220, 130)   # bright green – final path
PANEL_C = (30,  30,  30)
BTN_C = (70,  70,  70)
BTN_HOV = (110, 110, 110)
TEXT_C = (220, 220, 220)

START_POS = (1, 1)
GOAL_POS = (6, 6)

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def build_grid():
    """Return fresh 8x8 grid matching Q7.ipynb layout."""
    grid = [[EMPTY] * COLS for _ in range(ROWS)]
    for i in range(2, 6):
        grid[i][3] = WALL
        grid[i][5] = WALL
    for j in range(1, 4):
        grid[4][j] = WALL
    for j in range(4, 7):
        grid[6][j] = WALL
    grid[START_POS[0]][START_POS[1]] = START
    grid[GOAL_POS[0]][GOAL_POS[1]] = GOAL
    return grid


def pixel_to_cell(mx, my):
    """Convert mouse pixel position to (row, col). Returns None if outside grid."""
    if mx < 0 or mx >= COLS * CELL or my < 0 or my >= ROWS * CELL:
        return None
    return (my // CELL, mx // CELL)


def toggle_wall(grid, mx, my, drag_mode=None):
    """
    Toggle a wall at the mouse position.

    drag_mode: None  = first click, auto-detect (place or erase)
               True  = dragging in place mode  (set WALL)
               False = dragging in erase mode  (set EMPTY)

    Returns:
        (new_drag_mode, changed)
        new_drag_mode – True/False to pass back on next drag call
        changed       – True if the grid was modified
    """
    cell = pixel_to_cell(mx, my)
    if cell is None:
        return drag_mode, False

    r, c = cell
    ct = grid[r][c]

    # Never overwrite Start or Goal
    if ct in (START, GOAL):
        return drag_mode, False

    if drag_mode is None:
        # First click: decide whether we're placing or erasing
        if ct == EMPTY:
            grid[r][c] = WALL
            return True, True
        elif ct == WALL:
            grid[r][c] = EMPTY
            return False, True
        return drag_mode, False
    else:
        # Dragging: apply consistent mode
        target = WALL if drag_mode else EMPTY
        if ct != target and ct not in (START, GOAL):
            grid[r][c] = target
            return drag_mode, True
        return drag_mode, False


def get_neighbors(pos, grid):
    r, c = pos
    result = []
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != WALL:
            result.append((nr, nc))
    return result


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


# ── Drawing ──────────────────────────────────────────────────────────────────

def draw_grid(surf, grid, visited, frontier, path_set, hover_cell=None, editable=False):
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c * CELL, r * CELL
            ct = grid[r][c]
            if ct == WALL:
                col = WALL_C
            elif ct == START:
                col = START_C
            elif ct == GOAL:
                col = GOAL_C
            elif (r, c) in path_set:
                col = PATH_C
            elif (r, c) in visited:
                col = VISIT_C
            elif (r, c) in frontier:
                col = FRONT_C
            else:
                col = WHITE
            pygame.draw.rect(surf, col, (x + 1, y + 1, CELL - 2, CELL - 2))

            # Hover highlight so user knows they can click
            if editable and hover_cell == (r, c) and ct not in (START, GOAL):
                hover_col = (80, 80, 80) if ct == WALL else (210, 210, 210)
                pygame.draw.rect(
                    surf, hover_col, (x + 1, y + 1, CELL - 2, CELL - 2))
                pygame.draw.rect(surf, (255, 200, 0),
                                 (x + 1, y + 1, CELL - 2, CELL - 2), 2)

    for i in range(ROWS + 1):
        pygame.draw.line(surf, GRAY, (0, i * CELL), (COLS * CELL, i * CELL))
    for j in range(COLS + 1):
        pygame.draw.line(surf, GRAY, (j * CELL, 0), (j * CELL, ROWS * CELL))


def draw_panel(surf, font, algo_name, heur_name,
               nodes, cost, elapsed, state, btn_run, btn_reset,
               btn_manh, btn_eucl, heur_idx, mx, my):
    px = COLS * CELL
    pygame.draw.rect(surf, PANEL_C, (px, 0, PANEL_W, WIN_H))

    def txt(text, x, y, colour=TEXT_C):
        surf.blit(font.render(text, True, colour), (x, y))

    def btn(rect, label, active=False):
        col = (80, 140, 80) if active else (
            BTN_HOV if rect.collidepoint(mx, my) else BTN_C)
        pygame.draw.rect(surf, col, rect)
        pygame.draw.rect(surf, GRAY, rect, 1)
        lbl = font.render(label, True, WHITE)
        surf.blit(lbl, lbl.get_rect(center=rect.center))

    y = 10
    txt(algo_name, px + 8, y, (180, 220, 255))
    y += 24

    # Heuristic buttons
    txt("Heuristic:", px + 8, y, GRAY)
    y += 20
    btn(btn_manh, "Manhattan", active=(heur_idx == 0))
    btn(btn_eucl, "Euclidean", active=(heur_idx == 1))
    y = btn_manh.bottom + 10

    # Run / Reset
    btn(btn_run,   "Run")
    btn(btn_reset, "Reset")
    y = btn_run.bottom + 14

    # Metrics
    txt("Nodes:  " + str(nodes),                     px + 8, y)
    y += 22
    txt("Cost:   " + (str(cost) if cost else "-"),   px + 8, y)
    y += 22
    txt("Time:   " + (f"{elapsed:.1f}ms" if elapsed else "-"), px + 8, y)
    y += 26

    # Status
    status_col = (100, 220, 100) if state == 'done' else (
        220, 100, 100) if state == 'no_path' else TEXT_C
    txt(state.upper(), px + 8, y, status_col)
    y += 24

    # Legend
    legend = [
        (START_C, "Start"),
        (GOAL_C,  "Goal"),
        (WALL_C,  "Wall"),
        (FRONT_C, "Frontier"),
        (VISIT_C, "Visited"),
        (PATH_C,  "Path"),
    ]
    for colour, label in legend:
        pygame.draw.rect(surf, colour, (px + 8, y + 2, 14, 14))
        txt(label, px + 26, y)
        y += 20
