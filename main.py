"""
main.py – Entry point. Run this file.
    python main.py

Controls:
  GBFS / A*              – pick algorithm
  Manhattan / Euclidean  – pick heuristic
  Run                    – start animated search (keeps your walls!)
  Reset                  – clear board AND walls back to default
  Left-click grid        – place a wall
  Left-click wall        – remove the wall
  Click and drag         – draw / erase walls continuously
  ESC                    – quit
"""
import pygame
import sys

from grid import (build_grid, draw_grid, toggle_wall, pixel_to_cell,
                  ROWS, COLS, CELL, PANEL_W, WIN_W, WIN_H,
                  FPS, STEP_DELAY, START_POS, GOAL_POS,
                  WALL, EMPTY, manhattan, euclidean, BLACK,
                  WHITE, GRAY, TEXT_C, PANEL_C, BTN_C, BTN_HOV,
                  START_C, GOAL_C, WALL_C, FRONT_C, VISIT_C, PATH_C)
from rgbfs import gbfs
from astar import astar

px = COLS * CELL
bx = px + 8
BW = (PANEL_W - 20) // 2
BH = 26


def make_buttons():
    y = 30
    return {
        'gbfs':  pygame.Rect(bx,          y,      BW, BH),
        'astar': pygame.Rect(bx + BW + 4, y,      BW, BH),
        'manh':  pygame.Rect(bx,          y + 34, BW, BH),
        'eucl':  pygame.Rect(bx + BW + 4, y + 34, BW, BH),
        'run':   pygame.Rect(bx,          y + 68, BW, BH),
        'reset': pygame.Rect(bx + BW + 4, y + 68, BW, BH),
    }


def fresh_state():
    """Full reset – rebuilds the grid (wipes custom walls too)."""
    return dict(
        grid=build_grid(),
        visited=set(),
        frontier=set(),
        path=[],
        nodes_visited=0,
        path_cost=0,
        elapsed=0.0,
        state='idle',
        gen=None,
    )


def clear_search(s):
    """Clear only the search overlay – keeps the user's walls intact."""
    s['visited'] = set()
    s['frontier'] = set()
    s['path'] = []
    s['nodes_visited'] = 0
    s['path_cost'] = 0
    s['elapsed'] = 0.0
    s['state'] = 'idle'
    s['gen'] = None
    return s


def draw_panel(surf, font_lbl, font_val, btns, algo_idx, heur_idx, s, mx, my):
    pygame.draw.rect(surf, PANEL_C, (px, 0, PANEL_W, WIN_H))
    pygame.draw.line(surf, GRAY, (px, 0), (px, WIN_H), 1)

    def label(text, x, y, col=GRAY):
        surf.blit(font_lbl.render(text, True, col), (x, y))

    def value(text, x, y, col=TEXT_C):
        surf.blit(font_val.render(text, True, col), (x, y))

    def btn(rect, text, active=False):
        col = (60, 160, 80) if active else (
            BTN_HOV if rect.collidepoint(mx, my) else BTN_C)
        pygame.draw.rect(surf, col, rect)
        pygame.draw.rect(surf, GRAY, rect, 1)
        t = font_lbl.render(text, True, WHITE)
        surf.blit(t, t.get_rect(center=rect.center))

    y = 8
    label("Algorithm", bx, y)
    y = btns['gbfs'].top
    btn(btns['gbfs'],  "GBFS", active=(algo_idx == 0))
    btn(btns['astar'], "A*",   active=(algo_idx == 1))

    y = btns['gbfs'].bottom + 6
    label("Heuristic", bx, y)
    y = btns['manh'].top
    btn(btns['manh'], "Manhattan", active=(heur_idx == 0))
    btn(btns['eucl'], "Euclidean", active=(heur_idx == 1))

    y = btns['manh'].bottom + 6
    label("Controls", bx, y)
    y = btns['run'].top
    btn(btns['run'],   "Run")
    btn(btns['reset'], "Reset")

    # Metrics
    y = btns['run'].bottom + 12
    pygame.draw.line(surf, (60, 60, 60), (px + 4, y), (px + PANEL_W - 4, y))
    y += 6
    label("Nodes:",  bx, y)
    value(str(s['nodes_visited']),                           bx + 70, y)
    y += 20
    label("Cost:",   bx, y)
    value(str(s['path_cost']) if s['path_cost'] else "-",    bx + 70, y)
    y += 20
    label("Time:",   bx, y)
    value(f"{s['elapsed']:.1f}ms" if s['elapsed'] else "-",  bx + 70, y)
    y += 20

    # Status
    pygame.draw.line(surf, (60, 60, 60), (px + 4, y), (px + PANEL_W - 4, y))
    y += 6
    st = s['state']
    st_col = (80, 220, 80) if st == 'done' else \
        (220, 80, 80) if st == 'no_path' else TEXT_C
    st_text = {'idle': 'Idle', 'running': 'Running...',
               'done': 'Done!', 'no_path': 'No Path'}.get(st, st)
    value(st_text, bx, y, st_col)
    y += 22

    # Legend
    pygame.draw.line(surf, (60, 60, 60), (px + 4, y), (px + PANEL_W - 4, y))
    y += 6
    for col, lbl in [(START_C, "Start"), (GOAL_C, "Goal"), (WALL_C, "Wall"),
                     (FRONT_C, "Frontier"), (VISIT_C, "Visited"), (PATH_C, "Path")]:
        pygame.draw.rect(surf, col, (bx, y + 3, 13, 13))
        label(lbl, bx + 18, y)
        y += 18

    # Wall hint
    y += 4
    pygame.draw.line(surf, (60, 60, 60), (px + 4, y), (px + PANEL_W - 4, y))
    y += 6
    hint_col = (255, 200, 0) if s['state'] in (
        'idle', 'done', 'no_path') else (80, 80, 80)
    label("Click/drag grid", bx, y, hint_col)
    y += 16
    label("to add/remove walls", bx, y, hint_col)


def main():
    pygame.init()
    surf = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Search Visualizer")
    clock = pygame.time.Clock()

    font_lbl = pygame.font.SysFont("arial", 13, bold=True)
    font_val = pygame.font.SysFont("arial", 13)

    btns = make_buttons()
    algo_idx = 0
    heur_idx = 0
    last_step = 0
    s = fresh_state()

    dragging = False
    drag_mode = None

    while True:
        now = pygame.time.get_ticks()
        mx, my = pygame.mouse.get_pos()

        on_grid = (mx < COLS * CELL) and (my < ROWS * CELL)
        editable = s['state'] in ('idle', 'done', 'no_path')
        hover_cell = pixel_to_cell(mx, my) if on_grid and editable else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if on_grid and editable:
                    # Wall toggle – grid stays, just modify the cell
                    drag_mode, _ = toggle_wall(
                        s['grid'], mx, my, drag_mode=None)
                    dragging = True

                elif btns['gbfs'].collidepoint(mx, my):
                    algo_idx = 0
                    clear_search(s)          # keep walls, just reset search

                elif btns['astar'].collidepoint(mx, my):
                    algo_idx = 1
                    clear_search(s)          # keep walls, just reset search

                elif btns['manh'].collidepoint(mx, my):
                    heur_idx = 0
                    clear_search(s)          # keep walls, just reset search

                elif btns['eucl'].collidepoint(mx, my):
                    heur_idx = 1
                    clear_search(s)          # keep walls, just reset search

                elif btns['run'].collidepoint(mx, my) and editable:
                    # keep walls, clear previous result
                    clear_search(s)
                    h_fn = manhattan if heur_idx == 0 else euclidean
                    s['gen'] = gbfs(s['grid'], START_POS, GOAL_POS, h_fn) if algo_idx == 0 \
                        else astar(s['grid'], START_POS, GOAL_POS, h_fn)
                    s['state'] = 'running'

                elif btns['reset'].collidepoint(mx, my):
                    s = fresh_state()        # full reset – grid goes back to default

            if event.type == pygame.MOUSEMOTION:
                if dragging and on_grid and editable:
                    drag_mode, _ = toggle_wall(
                        s['grid'], mx, my, drag_mode=drag_mode)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
                drag_mode = None

        # Advance animation
        if s['state'] == 'running' and s['gen'] and (now - last_step) >= STEP_DELAY:
            last_step = now
            try:
                kind, vis, fron, pth, nv, pc, el = next(s['gen'])
                s['visited'] = vis
                s['frontier'] = fron
                s['nodes_visited'] = nv
                if kind in ('done', 'no_path'):
                    s['elapsed'] = el
                    s['path'] = pth
                    s['path_cost'] = pc
                    s['state'] = kind
                    s['gen'] = None
            except StopIteration:
                s['state'] = 'done'
                s['gen'] = None

        # Draw
        surf.fill(BLACK)
        draw_grid(surf, s['grid'], s['visited'], s['frontier'], set(s['path']),
                  hover_cell=hover_cell, editable=editable)
        draw_panel(surf, font_lbl, font_val, btns,
                   algo_idx, heur_idx, s, mx, my)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
