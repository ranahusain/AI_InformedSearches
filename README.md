# Search Algorithm Visualizer

An interactive grid-based visualizer built with **Python** and **PyGame** that demonstrates two informed search algorithms — **Greedy Best-First Search (GBFS)** and **A\* Search** — with two heuristic options: **Manhattan Distance** and **Euclidean Distance**.

---

## Project Structure

```
search-visualizer/
├── main.py       # Entry point — runs the PyGame window
├── grid.py       # Grid setup, colours, wall logic, drawing helpers
├── gbfs.py       # Greedy Best-First Search algorithm
├── astar.py      # A* Search algorithm
└── README.md     # This file
```

---

## Dependencies

| Dependency | Version | Purpose                       |
| ---------- | ------- | ----------------------------- |
| Python     | 3.8+    | Programming language          |
| PyGame     | 2.0+    | Window, rendering, user input |

Python's built-in modules used (no install needed):

- `heapq` — priority queue for the open set
- `math` — Euclidean distance calculation
- `time` — execution time measurement
- `sys` — clean program exit

---

## Installation & Setup

### Step 1 — Make sure Python is installed

```bash
python --version
```

If not installed, download from [python.org](https://www.python.org/downloads/).

### Step 2 — Install PyGame

```bash
pip install pygame
```

If you are using **Anaconda / Jupyter**, open **Anaconda Prompt** and run:

```bash
pip install pygame
```

### Step 3 — Download all four files

Place these files in the **same folder**:

```
main.py
grid.py
gbfs.py
astar.py
```

### Step 4 — Run the program

```bash
python main.py
```

> **Important:** Do NOT run from inside Jupyter Notebook. PyGame requires its own desktop window. Run from a terminal, command prompt, or Anaconda Prompt.

---

## How to Use

### Interface Layout

```
┌─────────────────────────┬───────────────┐
│                         │  Algorithm    │
│                         │ [GBFS] [A*]   │
│                         │               │
│       8 × 8 Grid        │  Heuristic    │
│                         │ [Manh][Eucl]  │
│                         │               │
│   S = Start  (green)    │ [Run] [Reset] │
│   G = Goal   (red)      │               │
│   ■ = Wall   (dark)     │  Nodes: 0     │
│                         │  Cost:  -     │
│                         │  Time:  -     │
│                         │               │
│                         │  Status: Idle │
└─────────────────────────┴───────────────┘
```

### Controls

| Action                | How                                         |
| --------------------- | ------------------------------------------- |
| Pick algorithm        | Click **GBFS** or **A\*** button            |
| Pick heuristic        | Click **Manhattan** or **Euclidean** button |
| Run the search        | Click **Run**                               |
| Reset to default grid | Click **Reset**                             |
| Place a wall          | Left-click any empty cell                   |
| Remove a wall         | Left-click any existing wall                |
| Draw walls fast       | Hold left-click and drag across cells       |
| Erase walls fast      | Hold left-click on a wall and drag          |
| Quit                  | Press **ESC**                               |

> **Note:** Walls can be placed/removed when the state is **Idle**, **Done**, or **No Path**. Clicking **Run** keeps your custom walls — only **Reset** restores the original layout.

### Colour Legend

| Colour          | Meaning                                          |
| --------------- | ------------------------------------------------ |
| 🟢 Dark Green   | Start node                                       |
| 🔴 Red          | Goal node                                        |
| ⬛ Dark Grey    | Wall / obstacle                                  |
| 🟡 Yellow       | Frontier — nodes currently in the priority queue |
| 🔵 Blue         | Visited — nodes that have been expanded          |
| 🟢 Bright Green | Final path found                                 |
| ⬜ White        | Empty cell                                       |

---

## Algorithm Details

### 1. Greedy Best-First Search (GBFS)

**File:** `gbfs.py`

**Evaluation function:**

```
f(n) = h(n)
```

GBFS selects the next node to expand based **purely on the heuristic** — it always picks the node that looks closest to the goal, ignoring the actual cost of the path taken so far.

#### How it is built

1. A **min-heap** (priority queue) is initialised with the start node, prioritised by `h(start, goal)`.
2. A `came_from` dictionary tracks each node's parent for path reconstruction.
3. A `visited` set prevents re-expanding nodes already processed.
4. On each step:
   - Pop the node with the lowest `h(n)` from the heap.
   - If it has already been visited, skip it.
   - Mark it as visited and yield the current state for animation.
   - If it is the goal, reconstruct the path by following `came_from` back to start and yield a `done` result.
   - Otherwise, add all unvisited, undiscovered neighbours to the heap, each scored by their heuristic value.
5. A `counter` is used as a tie-breaker so that nodes with equal heuristic values are expanded in insertion order, keeping the heap stable.
6. The function is implemented as a **Python generator** — it `yield`s one step at a time so the PyGame loop can animate each expansion without blocking.

#### Characteristics

| Property         | Value                                              |
| ---------------- | -------------------------------------------------- |
| Complete         | Not guaranteed (can loop without visited tracking) |
| Optimal          | No — ignores path cost                             |
| Time complexity  | O(b^m) worst case                                  |
| Space complexity | O(b^m)                                             |
| Speed            | Fast — heads straight toward goal                  |

---

### 2. A\* Search

**File:** `astar.py`

**Evaluation function:**

```
f(n) = g(n) + h(n)
```

Where:

- `g(n)` = actual cost from the start node to node `n`
- `h(n)` = estimated cost from node `n` to the goal (heuristic)

A\* balances the known path cost with the estimated remaining cost. It is **optimal** as long as the heuristic never overestimates the true cost (i.e., it is _admissible_). Both Manhattan and Euclidean distance on a unit-cost grid are admissible.

#### How it is built

1. A **min-heap** is initialised with the start node, prioritised by `f(start) = 0 + h(start, goal)`.
2. `came_from` tracks each node's parent for path reconstruction.
3. `g_score` is a dictionary mapping each node to its best known cost from the start.
4. A `visited` set prevents re-expanding already-closed nodes.
5. On each step:
   - Pop the node with the lowest `f(n)` from the heap.
   - If already visited, skip it.
   - Mark as visited and yield the current state for animation.
   - If it is the goal, reconstruct and yield the path along with the final `g_score`.
   - For each neighbour, compute `tentative_g = g(current) + 1`. If this is a better path than previously known, update `g_score`, update `came_from`, compute the new `f`, and push to the heap.
6. Like GBFS, this is a **Python generator** that yields one step at a time for smooth animation.

#### Characteristics

| Property         | Value                                        |
| ---------------- | -------------------------------------------- |
| Complete         | Yes                                          |
| Optimal          | Yes (with admissible heuristic)              |
| Time complexity  | O(b^d) where d = depth of optimal solution   |
| Space complexity | O(b^d)                                       |
| Speed            | Slower than GBFS but finds the shortest path |

---

## Heuristic Functions

Both heuristics are defined in `grid.py` and estimate the distance from any cell to the goal.

### Manhattan Distance

```
D_manhattan = |x1 - x2| + |y1 - y2|
```

Measures distance as the sum of horizontal and vertical steps. Best suited for grids where movement is restricted to 4 directions (up, down, left, right), which matches this project exactly.

### Euclidean Distance

```
D_euclidean = √((x1 - x2)² + (y1 - y2)²)
```

Measures straight-line distance. It is also admissible on a unit-cost 4-directional grid because the straight line is always ≤ the actual path length. It tends to produce a slightly different exploration pattern compared to Manhattan.

---

## File Reference

### `grid.py`

Shared module imported by all other files. Contains:

- Grid dimensions, cell size, colours
- `build_grid()` — creates the default 8×8 layout with preset walls
- `get_neighbors()` — returns valid 4-directional neighbours for a cell
- `manhattan()` / `euclidean()` — heuristic functions
- `pixel_to_cell()` — converts mouse coordinates to grid row/col
- `toggle_wall()` — handles placing and erasing walls with drag support
- `draw_grid()` — renders the grid with colour-coded cell states and hover highlight
- `draw_panel()` — renders the right-side control panel (not used in latest `main.py`, panel drawing is inline)

### `gbfs.py`

Contains the `gbfs()` generator function. Imports `get_neighbors` from `grid.py`.

### `astar.py`

Contains the `astar()` generator function. Imports `get_neighbors` from `grid.py`.

### `main.py`

The PyGame event loop. Responsibilities:

- Opens the window and handles all events (clicks, keypresses)
- Manages two state functions: `fresh_state()` (full reset) and `clear_search()` (keeps walls, clears search overlay)
- Calls `next()` on the active generator each frame to advance the animation
- Passes all state to `draw_grid()` and `draw_panel()` each frame

---

## GBFS vs A\* — Quick Comparison

| Feature             | GBFS                     | A\*                    |
| ------------------- | ------------------------ | ---------------------- |
| Uses path cost g(n) | No                       | Yes                    |
| Uses heuristic h(n) | Yes                      | Yes                    |
| Finds shortest path | Not guaranteed           | Always                 |
| Nodes explored      | Fewer (faster)           | More (thorough)        |
| Best for            | Speed, approximate paths | Optimal, correct paths |

---

## Grid Layout (Default)

```
  0 1 2 3 4 5 6 7
0 . . . . . . . .
1 . S . . . . . .
2 . . . ■ . ■ . .
3 . . . ■ . ■ . .
4 . ■ ■ ■ . ■ . .
5 . . . . . . . .
6 . . . . ■ ■ ■ G    ← Goal blocked by walls on left
7 . . . . . . . .

S = Start (1,1)   G = Goal (6,6)   ■ = Wall
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'pygame'`**
→ Run `pip install pygame` in your terminal.

**Window does not open / crashes immediately**
→ Make sure all 4 files are in the same folder and you are running `python main.py`, not opening it in Jupyter.

**`pygame.error: No video mode has been set`**
→ You may be running in a headless environment (e.g., a remote server). PyGame needs a display. Run it on your local machine.

**Walls disappear when I click Run**
→ Make sure you are using the latest `main.py`. The fix separates `clear_search()` (keeps walls) from `fresh_state()` (resets everything).
