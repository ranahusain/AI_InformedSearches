"""
main.py – Entry point. Run this file.
    python main.py

Controls:
  Manhattan / Euclidean  – pick heuristic
  Run                    – start animated search
  Reset                  – clear the board
  ESC                    – quit
"""
import pygame
import sys

from grid import (build_grid, draw_grid, draw_panel,
                  ROWS, COLS, CELL, PANEL_W, WIN_W, WIN_H,
                  FPS, STEP_DELAY, START_POS, GOAL_POS,
                  WALL, EMPTY, manhattan, euclidean, BLACK)
from rgbfs import gbfs
from astar import astar

# Layout constants
px = COLS * CELL          # left edge of panel
bx = px + 8               # button x
BW = (PANEL_W - 20) // 2  # button width (half panel)
BH = 28                   # button height


def make_buttons():
    return {
        'manh':  pygame.Rect(bx,          54, BW,        BH),
        'eucl':  pygame.Rect(bx + BW + 4, 54, BW,        BH),
        'run':   pygame.Rect(bx,          90, BW,        BH),
        'reset': pygame.Rect(bx + BW + 4, 90, BW,        BH),
    }


def reset_state():
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


def main():
    pygame.init()
    surf = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 13)

    btns = make_buttons()
    heur_idx = 0          # 0 = Manhattan, 1 = Euclidean
    algo_idx = 0          # 0 = GBFS,      1 = A*
    algo_names = ["GBFS", "A*"]
    last_step = 0

    s = reset_state()      # all mutable state in one dict

    running = True
    while running:
        now = pygame.time.get_ticks()
        mx, my = pygame.mouse.get_pos()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 'G' = GBFS,  'A' = A*
                if event.key == pygame.K_g:
                    algo_idx = 0
                    s = reset_state()
                if event.key == pygame.K_a:
                    algo_idx = 1
                    s = reset_state()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Heuristic toggle
                if btns['manh'].collidepoint(mx, my):
                    heur_idx = 0
                    s = reset_state()
                if btns['eucl'].collidepoint(mx, my):
                    heur_idx = 1
                    s = reset_state()

                # Run
                if btns['run'].collidepoint(mx, my) and s['state'] in ('idle', 'done', 'no_path'):
                    s = reset_state()
                    h_fn = manhattan if heur_idx == 0 else euclidean
                    if algo_idx == 0:
                        s['gen'] = gbfs(s['grid'], START_POS, GOAL_POS, h_fn)
                    else:
                        s['gen'] = astar(s['grid'], START_POS, GOAL_POS, h_fn)
                    s['state'] = 'running'

                # Reset
                if btns['reset'].collidepoint(mx, my):
                    s = reset_state()

                # Toggle walls
                if mx < COLS * CELL and s['state'] == 'idle':
                    r, c = my // CELL, mx // CELL
                    if s['grid'][r][c] == EMPTY:
                        s['grid'][r][c] = WALL
                    elif s['grid'][r][c] == WALL:
                        s['grid'][r][c] = EMPTY

                # Click anywhere outside panel to cycle algo when idle
                if mx < COLS * CELL and s['state'] == 'idle':
                    pass  # wall toggling handled above

            # Right-click to switch algorithm
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if mx < COLS * CELL and s['state'] == 'idle':
                    algo_idx = 1 - algo_idx   # toggle GBFS <-> A*

        # one animation step
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
        draw_grid(surf, s['grid'], s['visited'], s['frontier'], set(s['path']))

        algo_label = algo_names[algo_idx] + \
            (" [Manhattan]" if heur_idx == 0 else " [Euclidean]")
        draw_panel(surf, font, algo_label, "",
                   s['nodes_visited'], s['path_cost'], s['elapsed'],
                   s['state'],
                   btns['run'], btns['reset'],
                   btns['manh'], btns['eucl'],
                   heur_idx, mx, my)

        #  algo switch hint at bottom of panel
        hint = font.render("Right-click grid: switch algo",
                           True, (100, 100, 100))
        surf.blit(hint, (px + 4, WIN_H - 18))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
