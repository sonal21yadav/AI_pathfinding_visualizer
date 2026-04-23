# AI PATHFINDING VISUALIZER
## Overview
An interactive **pathfinding algorithm visualizer** built using **Python** and **Pygame**.
The prooject demonstrates how different AI search algorithms explore a grid to find a path between two points, along with real time animation and performance insights.
## Preview
| **Region**  |   **Description**
|:----------- | :---------------
| Header (72px) | Algorithm selector, case modes, tool picker, and action buttons
| Grid (840x560px) | 30x20 interactive cells (28 px each)
| Side Panel (330px) | Algorithm insight, results, and time complexity cards
| Footer(86px) | Color legend and animation speed control

## Features
- Visualize multiple pathfinding algorithms in real-time.
- Real-time animation with adjustable speed (1-20)
- Interactive grid - draw walls by clicking and dragging, place/move start and end points
- Live statistics panel showing nodes visited, path length, execution time in ms, and time complexity (best/average/worst).
- Color-coded paths - gold for best case, purple for averag, red for worst

## Algorithms Implemented
Algorithm |                                   Description
-----------------------    |         ------------------
**BFS(Breadth-First Search)** |       Explores level by level, guarantees shortest path
**DFS(Depth-First Search)**  |       Explores deeply, not guaranteed shortest
**A***                      |        Uses heuristic + cost for optimal pathfinding
**Hill Climbing**       |            Greedy local search
**Best First Search**    |           Chooses node closest to goal (heuristic only)
**MiniMax**               |          Adversarial-style consideration

## Project Structure
├── pathfinding_visualizer.py      # Main application (Pygame UI + algorithms)

├── pathfinding.ipynb              # Jupyter notebook

├── README.md                      # Project documentation

## Installation and Running
1. Clone the repository
```bash
https://github.com/sonal21yadav/AI_pathfinding_visualizer.git
```
2. Install Pygame
```
pip install pygame== 2.6.1
```
3. Run the visualizer
```
python pathfinding_visualizer.py
```

## HOW TO USE
Setting up the grid
1. Select a tool from the toolbar
   - D - Draw walls (left-click + drag to point, right-click to erase)
   - S - Place the **Start** cell (green)
   - E - Place the **End** cell (orange)
2. Choose an algorithm from the top row of the header
3. Choose a case mode from the second row:
   - **BEST Case** - grid arranged to give the algorithm an easy run
   - **AVERAGE Case** - randomized obstacle layout
   - **WORST Case** - grid arranged to force the worst performance
4. Click **Visualize** to run.

During/after a run
- Visited cells animate in light blue, one step at a time.
- The final path is drawn in the case-mode color (gols/purple/red).
- The side panel shows STATUS, NODES, VISITED, PATH LENGTH, TIME(MS), and TIME COMPLEXITY chips.

## ALGORITHMS
**1. Breadth-First Search (BFS)**
Explores grid level-by-level using FIFO queue. Every neighbor at distance d is visited before any neighbor at distance d+1.
    - Guarantees the shortest path on an unweighted grid.
    - Time Complexity: O(V+E)
    - Space Complexity: O(V)
**2. Depth-First Search** 
Dives as deep as possible alone one branch before backtracking, using a LIFO stack.
   - Does NOT guarantee the shortest path
   - Can get trapped in long dead ends.
   - Time Complexity : O(V+E)
**3. A-star**
Combines the actual cost from the start (g) with the estimated cost to the goal (h=Manhattan distance) to score each node: f=g+h
   - Optimal and complete when the heuritic is admissible.
   - Most efficient of the six for finding shortest paths.
   - Time Complexity: O(b^d)
**4. Hill Climbing**
A greedy local search that always moves to the neighboring cell with the best heuritic score. No backtracking.
   - Fast but not complete -  can get stuck in local optima or plateau regions.
   - Time Complexity: O(bxm(
**5. Best First Search**
Expands the node that looks most promising according to heuristic alone (ignores path cost so far). Uses a min-heap priority queue.
   - MOre focused than BFS/DFS but not guaranteed to find the shortest path.
   - Time Complexity: O(b^m)
**6. MINIMAX**
Adapted form adversarial game-tree search: alternates between maximizing (moving away from goal) and minimizing (moving toward goal) steps to stimulate worst-case exploration.
   - Explores broadly like BFS in adversarial conditions.
   - Time Complexity: O(b^m)
 

